"""Millisecond-precision latency & token-throughput tracking."""

import time
from typing import Dict, Optional


class SpeedTracker:
    """Tracks per-stage latency and token throughput for the SPEED challenge."""

    def __init__(self) -> None:
        self._stage_start: Dict[str, float] = {}
        self.stage_latencies: Dict[str, float] = {}
        self.total_tokens_generated = 0
        self._tok_start_by_stage: Dict[str, float] = {}
        self._tok_count_by_stage: Dict[str, int] = {}

    def begin_stage(self, stage: str) -> None:
        self._stage_start[stage] = time.perf_counter()
        self._tok_start_by_stage[stage] = time.perf_counter()
        self._tok_count_by_stage[stage] = 0

    def end_stage(self, stage: str) -> float:
        start = self._stage_start.pop(stage, time.perf_counter())
        ms = (time.perf_counter() - start) * 1000.0
        self.stage_latencies[stage] = round(ms, 1)
        return ms

    def record_tokens(self, stage: str, n: int = 1) -> None:
        self._tok_count_by_stage[stage] = self._tok_count_by_stage.get(stage, 0) + n
        self.total_tokens_generated += n

    @property
    def total_latency_ms(self) -> float:
        return round(sum(self.stage_latencies.values()), 1)

    def stage_tokens_per_sec(self, stage: str) -> float:
        count = self._tok_count_by_stage.get(stage, 0)
        if count == 0:
            return 0.0
        started = self._tok_start_by_stage.get(stage, time.perf_counter())
        elapsed = time.perf_counter() - started
        return round(count / elapsed, 1) if elapsed > 0 else 0.0

    @property
    def tokens_per_second(self) -> float:
        token_time = sum(
            (time.perf_counter() - s) for s in self._tok_start_by_stage.values()
        )
        if token_time <= 0:
            return 0.0
        return round(self.total_tokens_generated / token_time, 1)

    def metrics(self, gpu: Optional[Dict] = None, model_name: str = "", quantization: str = "", resolution: str = "") -> Dict:
        gpu = gpu or {}
        return {
            "total_latency_ms": self.total_latency_ms,
            "stage_latencies": self.stage_latencies,
            "tokens_per_second": self.stage_tokens_per_sec("deliberation")
            or self.tokens_per_second,
            "total_tokens_generated": self.total_tokens_generated,
            "vram_usage_mb": gpu.get("vram_usage_mb", 0.0),
            "vram_total_mb": gpu.get("vram_total_mb", 0.0),
            "gpu_utilization_percent": gpu.get("gpu_utilization_percent", 0.0),
            "model_name": model_name,
            "quantization": quantization,
            "image_resolution": resolution,
        }


def ms(start: float) -> float:
    return (time.perf_counter() - start) * 1000.0