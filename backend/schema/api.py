import time
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

from backend import config


class AnalyzeRequest(BaseModel):
    """Request body for /v1/analyze"""

    image_base64: str = Field(
        ...,
        min_length=16,
        max_length=((config.MAX_IMAGE_BYTES + 2) // 3) * 4,
        description="Base64 encoded image",
    )
    domain: Literal[
        "auto", "pcb", "medical", "architecture", "satellite"
    ] = Field(default="auto", description="auto|pcb|medical|architecture|satellite")
    detail_level: Literal["low", "medium", "high"] = Field(
        default="high", description="low|medium|high"
    )


class ErrorResponse(BaseModel):
    """Error payload sent to the SSE stream or returned directly"""

    error: str
    message: str
    stage: Optional[str] = None


class SSEEvent(BaseModel):
    """A single SSE event in the stream"""

    stage: str = Field(
        ..., description="mapping|thought|critic|verdict|metrics|error"
    )
    data: Dict[str, Any]
    timestamp: float = Field(default_factory=time.time)
