from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class HallucinationFlag(BaseModel):
    """A detected hallucination in the thought chain"""

    chunk_id: int
    claim: str
    issue: str
    severity: str = Field(..., description="minor|major|critical")

    @model_validator(mode="after")
    def _check_severity(self) -> "HallucinationFlag":
        if self.severity not in {"minor", "major", "critical"}:
            raise ValueError(f"severity must be minor|major|critical, got {self.severity!r}")
        return self


class Correction(BaseModel):
    """A correction to a hallucinated or inaccurate claim"""

    original_claim: str
    issue: str
    corrected_claim: str
    referenced_entity_id: Optional[str] = None


class VerificationReport(BaseModel):
    """Stage 3 output: Critic's verification of the thought chain"""

    verified: bool
    hallucination_count: int
    hallucinations: List[HallucinationFlag]
    missed_entities: List[str] = Field(default_factory=list)
    corrections: List[Correction]
    critic_confidence: float = Field(..., ge=0.0, le=1.0)
    critic_notes: str

    @model_validator(mode="after")
    def _check_count(self) -> "VerificationReport":
        if self.hallucination_count != len(self.hallucinations):
            raise ValueError(
                f"hallucination_count ({self.hallucination_count}) does not match "
                f"hallucinations length ({len(self.hallucinations)})"
            )
        return self
