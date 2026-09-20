import json
import pytest
from backend.schema.verdict import FinalVerdict
from backend.pipeline.review_policy import apply_review_policy
BOX = {"xmin": 0.1, "ymin": 0.1, "xmax": 0.7, "ymax": 0.7}
MAP = json.dumps({"entities": [{"id": "E1", "bbox": BOX}]})
def finding(entity="E1"):
    return FinalVerdict(image_suitability="adequate", visible_concern="absent", primary_finding="No concern", severity="NOMINAL", confidence=.9,
        affected_entities=[{"entity_id":entity,"role":"primary","bbox":BOX}],
        evidence_chain=[{"step_number":1,"description":"Visible region","supporting_entity_ids":[entity]}],
        recommended_action="No action",summary="Clear")
@pytest.mark.parametrize("critique", [
    {"verified":False,"hallucinations":[]},
    {"verified":True,"hallucinations":[{"severity":"critical"}]},
    {"verified":True,"hallucinations":[{"severity":"major"}]},
])
def test_rejected_findings_cannot_be_all_clear(critique):
    result=apply_review_policy(finding(),MAP,json.dumps(critique))
    assert result.review_status == "needs_review"
    assert result.severity == "WARNING"
    assert "Human review" in result.primary_finding
    assert "No action" not in result.recommended_action

def test_unknown_evidence_fails_closed():
    with pytest.raises(ValueError,match="unmapped"):
        apply_review_policy(finding("E9"),MAP,'{"verified":true}')

def test_verified_result_keeps_limitations():
    result=apply_review_policy(finding(),MAP,'{"verified":true}')
    assert result.review_status == "reviewed"
    assert result.limitations

def test_long_display_summary_preserves_full_finding():
    import asyncio
    from types import SimpleNamespace
    from backend.agents.synthesizer import Synthesizer
    async def run():
        payload=finding().model_dump(mode='json')
        payload['summary']='A long display summary. ' * 40
        agent=object.__new__(Synthesizer)
        async def stream(*args):
            yield {'delta':'','response':json.dumps(payload),'done':True}
        agent._stream=stream
        agent._track=lambda chunk: None
        ctx=SimpleNamespace(map_json=MAP,reasoning_output='Visible leaf',critique_json='{"verified":true}')
        events=[event async for event in agent.run(ctx,'image')]
        assert events[-1]['type']=='stage_result'
        assert len(events[-1]['data']['summary']) == 500
        assert events[-1]['data']['primary_finding']==payload['primary_finding']
        assert events[-1]['data']['evidence_chain']==payload['evidence_chain']
    asyncio.run(run())


def test_uncertainty_is_not_a_verified_crop_problem():
    verdict=finding()
    verdict.visible_concern="uncertain"
    result=apply_review_policy(verdict,MAP,'{"verified":true}')
    assert result.review_status=="needs_review"

def test_unsuitable_image_requests_a_new_photo():
    verdict=finding()
    verdict.image_suitability="unsuitable"
    result=apply_review_policy(verdict,MAP,'{"verified":true}')
    assert result.review_status=="needs_review"
    assert result.affected_entities==[]
    assert "photograph" in result.primary_finding

def test_absent_visible_concern_does_not_become_warning():
    verdict=finding()
    verdict.severity="WARNING"
    result=apply_review_policy(verdict,MAP,'{"verified":true}')
    assert result.severity=="NOMINAL"
    assert result.affected_entities==[]
    assert any("whole-plant" in note for note in result.limitations)

def test_rejection_overrides_absent_concern():
    result=apply_review_policy(finding(),MAP,'{"verified":false}')
    assert result.review_status=="needs_review"
    assert result.severity=="WARNING"


def test_skipped_review_never_claims_verification():
    result = apply_review_policy(finding(), MAP, '{"review_performed":false}')
    assert result.review_status == "not_reviewed"
    assert result.severity == "NOMINAL"


def test_skipped_review_still_requires_human_review_for_uncertainty():
    verdict = finding()
    verdict.visible_concern = "uncertain"
    result = apply_review_policy(verdict, MAP, '{"review_performed":false}')
    assert result.review_status == "needs_review"


@pytest.mark.parametrize("unfinished", ["placeholder", " Placeholder. ", "...", "", "TODO", "N/A"])
def test_incomplete_generated_action_requires_review(unfinished):
    verdict = finding()
    verdict.image_suitability = "limited"
    verdict.visible_concern = "uncertain"
    verdict.primary_finding = "Image is out of focus; inspection is inconclusive."
    verdict.recommended_action = unfinished
    verdict.summary = unfinished
    result = apply_review_policy(verdict, MAP, '{"review_performed":false}')
    assert result.review_status == "needs_review"
    assert "in-focus photograph" in result.recommended_action
    assert "did not provide" in result.recommended_action
    assert result.summary == verdict.primary_finding
    assert any("incomplete" in note for note in result.limitations)


def test_substantive_uncertain_action_is_preserved():
    verdict = finding()
    verdict.visible_concern = "uncertain"
    verdict.recommended_action = "Inspect several neighboring leaves and their undersides."
    result = apply_review_policy(verdict, MAP, '{"review_performed":false}')
    assert result.recommended_action == "Inspect several neighboring leaves and their undersides."
