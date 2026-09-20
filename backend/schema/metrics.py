from typing import Dict

from pydantic import BaseModel, Field


class PerformanceMetrics(BaseModel):
    """Real-time performance metrics for the SPEED challenge"""

    cached_stages: list[str] = Field(default_factory=list)
    total_latency_ms: float
    stage_latencies: Dict[str, float] = Field(
        ..., description="Per-stage latency in ms"
    )
    tokens_per_second: float
    total_tokens_generated: int
    vram_usage_mb: float
    vram_total_mb: float
    gpu_utilization_percent: float
    model_name: str
    quantization: str
    image_resolution: str
