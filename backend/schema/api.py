import time
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Request body for /v1/analyze"""

    image_base64: str = Field(..., description="Base64 encoded image")
    domain: str = Field(
        default="auto", description="auto|pcb|medical|architecture|satellite"
    )
    detail_level: str = Field(default="high", description="low|medium|high")


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
