from enum import Enum
from typing import List

from pydantic import BaseModel, Field

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

    primary_finding: str
    severity: Severity
    confidence: float = Field(..., ge=0.0, le=1.0)
    affected_entities: List[AffectedEntity]
    evidence_chain: List[EvidenceStep]
    recommended_action: str
    summary: str = Field(..., max_length=500)
