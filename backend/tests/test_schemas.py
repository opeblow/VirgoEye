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