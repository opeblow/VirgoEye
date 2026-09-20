from enum import Enum
from typing import List, Literal

from pydantic import BaseModel, Field, model_validator

from .diagnostic_map import BoundingBox


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    NOMINAL = "NOMINAL"


class AffectedEntity(BaseModel):
    """An entity involved in the final finding"""

    entity_id: str
    role: str = Field(..., description="Role in finding: primary|secondary|context")
    bbox: BoundingBox


class EvidenceStep(BaseModel):
    """A single step in the evidence chain"""

    step_number: int
    description: str
    supporting_entity_ids: List[str]


class FinalVerdict(BaseModel):
    """Stage 4 output: The final diagnostic verdict"""

    review_status: Literal["reviewed", "needs_review", "not_reviewed"] = "needs_review"
    limitations: List[str] = Field(default_factory=list)
    image_suitability: Literal["adequate", "limited", "unsuitable"] = "limited"
    visible_concern: Literal["present", "absent", "uncertain"] = "uncertain"
    primary_finding: str
    severity: Severity
    confidence: float = Field(..., ge=0.0, le=1.0)
    affected_entities: List[AffectedEntity]
    evidence_chain: List[EvidenceStep]
    recommended_action: str
    summary: str = Field(..., max_length=500)

    @model_validator(mode="after")
    def _check_consistency(self) -> "FinalVerdict":
        affected_ids = [a.entity_id for a in self.affected_entities]
        if len(set(affected_ids)) != len(affected_ids):
            raise ValueError("affected_entities ids must be unique")
        step_numbers = [e.step_number for e in self.evidence_chain]
        if len(set(step_numbers)) != len(step_numbers):
            raise ValueError("evidence_chain step_numbers must be unique")
        if any(n < 1 for n in step_numbers):
            raise ValueError("evidence_chain step_numbers must be >= 1")
        return self
