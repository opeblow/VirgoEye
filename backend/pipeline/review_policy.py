"""Deterministic checks on model-generated inspection findings."""
import json
import re
from backend.schema.verdict import Severity


def _unfinished_text(value):
    """Catch empty or template-only text without altering substantive findings."""
    normalized = re.sub(r"[^a-z0-9]+", "", value.casefold())
    return normalized in {"", "placeholder", "todo", "tbd", "na", "null", "none"}


def apply_review_policy(verdict, map_json, critique_json):
    mapping, critique = json.loads(map_json), json.loads(critique_json)
    entities = {e["id"]: e for e in mapping["entities"]}
    referenced = {a.entity_id for a in verdict.affected_entities}
    referenced.update(i for step in verdict.evidence_chain for i in step.supporting_entity_ids)
    if referenced - entities.keys():
        raise ValueError("Evidence references an unmapped region; inspection requires another review.")
    # Use the mapped location rather than accepting a second inconsistent box.
    for affected in verdict.affected_entities:
        affected.bbox = type(affected.bbox).model_validate(entities[affected.entity_id]["bbox"])
    review_performed = critique.get("review_performed", True)
    rejected = review_performed and (not critique.get("verified", False) or any(
        flag.get("severity") in {"major", "critical"}
        for flag in critique.get("hallucinations", [])
    ))
    verdict.review_status = "needs_review" if rejected else ("reviewed" if review_performed else "not_reviewed")
    verdict.limitations = ["Visual inspection support; not a confirmed diagnosis.",
                          "Image regions are approximate. Confidence is not a measured probability."]
    if critique.get("missed_entities"):
        verdict.limitations.append("The reviewer reported regions not fully assessed.")
    if rejected:
        verdict.primary_finding = "Human review required — automated findings were not verified."
        verdict.severity = Severity.WARNING
        verdict.recommended_action = "Inspect the image and flagged regions with a qualified field officer before acting. Obtain a clearer image or field observations."
        verdict.summary = "Needs review: the automated evidence check did not support a verified inspection conclusion."
        verdict.limitations.append("The automated reviewer rejected or identified substantial issues in the initial analysis.")
    # Uncertainty and unusable input must not look like crop damage or an all-clear.
    if not rejected and (verdict.image_suitability == "unsuitable" or verdict.visible_concern == "uncertain"):
        verdict.review_status = "needs_review"
        verdict.severity = Severity.WARNING
        if verdict.image_suitability == "unsuitable":
            verdict.primary_finding = "A clearer, relevant photograph is needed for inspection."
            verdict.recommended_action = "Upload a real crop photograph in focus, with the leaf or affected area filling the frame."
            verdict.affected_entities = []
        verdict.limitations.append("The image does not support a definite visible-concern assessment.")
    elif not rejected and verdict.visible_concern == "absent":
        verdict.severity = Severity.NOMINAL
        verdict.affected_entities = []
        verdict.limitations.append("No visible concern in one image does not establish whole-plant health.")
    elif not rejected and verdict.visible_concern == "present" and verdict.severity == Severity.NOMINAL:
        verdict.severity = Severity.WARNING
    if _unfinished_text(verdict.recommended_action):
        verdict.recommended_action = (
            "Obtain a clear, in-focus photograph of the crop and affected area, "
            "and review it with a qualified field officer before acting. "
            "The automated inspection did not provide a usable next step."
        )
        verdict.review_status = "needs_review"
        verdict.severity = Severity.WARNING
        verdict.limitations.append("The generated next step was incomplete; general review guidance is shown instead.")
    if _unfinished_text(verdict.summary):
        verdict.summary = verdict.primary_finding[:500]
    return verdict
