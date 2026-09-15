import pytest
from pydantic import ValidationError

from backend.schema.diagnostic_map import BoundingBox, DetectedEntity, DiagnosticMap
from backend.schema.verdict import FinalVerdict, Severity
from backend.schema.verification import VerificationReport


def test_bounding_box_valid():
    bb = BoundingBox(xmin=0.1, ymin=0.2, xmax=0.3, ymax=0.4)
    assert bb.ymax == 0.4


def test_bounding_box_out_of_range():
    with pytest.raises(ValidationError):
        BoundingBox(xmin=-0.1, ymin=0.0, xmax=0.3, ymax=0.4)


def test_diagnostic_map_roundtrip():
    ent = DetectedEntity(
        id="E1",
        label="IC Chip",
        bbox=BoundingBox(xmin=0.1, ymin=0.1, xmax=0.2, ymax=0.2),
        confidence=0.9,
        category="component",
    )
    m = DiagnosticMap(entities=[ent], total_entities=1, image_context="PCB", scan_coverage=0.95)
    data = m.model_dump()
    assert data["entities"][0]["category"] == "component"


def test_verdict_roundtrip():
    v = FinalVerdict(
        primary_finding="Cold solder joint on J7",
        severity=Severity.WARNING,
        confidence=0.72,
        affected_entities=[],
        evidence_chain=[],
        recommended_action="Re-flow J7",
        summary="x" * 50,
    )
    assert v.severity == "WARNING"


def test_verdict_summary_too_long():
    with pytest.raises(ValidationError):
        FinalVerdict(
            primary_finding="x",
            severity=Severity.NOMINAL,
            confidence=0.5,
            affected_entities=[],
            evidence_chain=[],
            recommended_action="x",
            summary="x" * 501,
        )


def test_verification_report_defaults():
    r = VerificationReport(
        verified=True,
        hallucination_count=0,
        hallucinations=[],
        corrections=[],
        critic_confidence=0.9,
        critic_notes="clean",
    )
    assert r.missed_entities == []


def make_entity(eid: str) -> DetectedEntity:
    return DetectedEntity(
        id=eid,
        label="IC",
        bbox=BoundingBox(xmin=0.1, ymin=0.1, xmax=0.2, ymax=0.2),
        confidence=0.9,
        category="component",
    )


def test_bbox_corner_ordering_is_enforced():
    with pytest.raises(ValidationError):
        BoundingBox(xmin=0.3, ymin=0.2, xmax=0.1, ymax=0.4)


def test_bbox_degenerate_zero_area_rejected():
    with pytest.raises(ValidationError):
        BoundingBox(xmin=0.1, ymin=0.1, xmax=0.1, ymax=0.4)


def test_map_duplicate_ids_rejected():
    with pytest.raises(ValidationError):
        DiagnosticMap(
            entities=[make_entity("E1"), make_entity("E1")],
            total_entities=2,
            image_context="PCB",
            scan_coverage=0.9,
        )


def test_map_total_count_mismatch_rejected():
    with pytest.raises(ValidationError):
        DiagnosticMap(
            entities=[make_entity("E1"), make_entity("E2")],
            total_entities=3,
            image_context="PCB",
            scan_coverage=0.9,
        )


def test_verification_hallucination_count_mismatch():
    from backend.schema.verification import HallucinationFlag

    with pytest.raises(ValidationError):
        VerificationReport(
            verified=False,
            hallucination_count=2,
            hallucinations=[
                HallucinationFlag(
                    chunk_id=0, claim="c", issue="i", severity="major"
                )
            ],
            corrections=[],
            critic_confidence=0.4,
            critic_notes="x",
        )


def test_hallucination_severity_enum():
    from backend.schema.verification import HallucinationFlag

    with pytest.raises(ValidationError):
        HallucinationFlag(chunk_id=0, claim="c", issue="i", severity="fatal")


def test_verdict_duplicate_affected_entities_rejected():
    with pytest.raises(ValidationError):
        FinalVerdict(
            primary_finding="x",
            severity=Severity.WARNING,
            confidence=0.6,
            affected_entities=[
                {
                    "entity_id": "E1",
                    "role": "primary",
                    "bbox": {"xmin": 0.0, "ymin": 0.0, "xmax": 0.1, "ymax": 0.1},
                },
                {
                    "entity_id": "E1",
                    "role": "context",
                    "bbox": {"xmin": 0.0, "ymin": 0.0, "xmax": 0.1, "ymax": 0.1},
                },
            ],
            evidence_chain=[],
            recommended_action="y",
            summary="s" * 20,
        )