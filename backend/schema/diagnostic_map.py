from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class EntityCategory(str, Enum):
    COMPONENT = "component"
    CONNECTION = "connection"
    TRACE = "trace"
    STRUCTURE = "structure"
    ANOMALY = "anomaly"
    TEXT = "text"
    REGION = "region"


class BoundingBox(BaseModel):
    """Pixel-normalized bounding box coordinates (0.0 to 1.0)"""

    xmin: float = Field(..., ge=0.0, le=1.0, description="Left edge")
    ymin: float = Field(..., ge=0.0, le=1.0, description="Top edge")
    xmax: float = Field(..., ge=0.0, le=1.0, description="Right edge")
    ymax: float = Field(..., ge=0.0, le=1.0, description="Bottom edge")


class DetectedEntity(BaseModel):
    """A single detected entity in the image"""

    id: str = Field(..., description="Unique entity ID (E1, E2, ...)")
    label: str = Field(..., description="Human-readable label")
    bbox: BoundingBox
    confidence: float = Field(..., ge=0.0, le=1.0)
    category: EntityCategory
    description: Optional[str] = None


class DiagnosticMap(BaseModel):
    """Stage 1 output: Complete spatial semantic map of the image"""

    entities: List[DetectedEntity]
    total_entities: int
    image_context: str = Field(..., description="Brief description of image type/domain")
    scan_coverage: float = Field(..., ge=0.0, le=1.0, description="% of image analyzed")
