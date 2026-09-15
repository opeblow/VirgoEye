"""Millisecond-precision latency & token-throughput tracking."""

import time
from typing import Dict, Optional


class SpeedTracker:
    """Tracks per-stage latency and token throughput for the SPEED challenge."""

    def __init__(self) -> None:
        self._stage_start: Dict[str, float] = {}
        self.stage_latencies: Dict[str, float] = {}
        self._tok_start_by_stage: Dict[str, float] = {}
        self._tok_count_by_stage: Dict[str, int] = {}
        # Frozen per-stage throughput captured when the stage ends, so a
        # stage's rate is not distorted by later stages' wall time.
        self._stage_tps: Dict[str, float] = {}
        # Exact token counts reported by the backend (e.g. Ollama eval_count)
        # take precedence over char-count approximations.
        self.eval_counts: Dict[str, int] = {}

    def begin_stage(self, stage: str) -> None:
        self._stage_start[stage] = time.perf_counter()
        self._tok_start_by_stage[stage] = time.perf_counter()
        if stage not in self._tok_count_by_stage:
            self._tok_count_by_stage[stage] = 0

    def end_stage(self, stage: str) -> float:
        start = self._stage_start.pop(stage, time.perf_counter())
        ms = (time.perf_counter() - start) * 1000.0
        self.stage_latencies[stage] = round(ms, 1)
        self._stage_tps[stage] = self.stage_tokens_per_sec(stage)
        return ms

    def record_tokens(self, stage: str, n: int = 1) -> None:
        """Record a token approximation for a streamed delta.

        Callers must pass an estimated token count, not raw character length
        (raw chars inflate tokens_per_second and total_tokens_generated).
        """
        self._tok_count_by_stage[stage] = self._tok_count_by_stage.get(stage, 0) + max(
            1, int(n)
        )

    def record_eval_count(self, stage: str, n: int) -> None:
        """Record an exact backend-provided token count (replaces estimate)."""
        self.eval_counts[stage] = int(n)
        self._tok_count_by_stage[stage] = int(n)

    @property
    def total_tokens_generated(self) -> int:
        return sum(self._tok_count_by_stage.values())

    @property
    def total_latency_ms(self) -> float:
        return round(sum(self.stage_latencies.values()), 1)

    def stage_tokens_per_sec(self, stage: str) -> float:
        count = self._tok_count_by_stage.get(stage, 0)
        if count == 0:
            return 0.0
        # Prefer the frozen end-of-stage snapshot when the stage has finished.
        snap = self._stage_tps.get(stage)
        if snap is not None and snap > 0.0:
            return snap
        started = self._tok_start_by_stage.get(stage, time.perf_counter())
        elapsed = time.perf_counter() - started
        return round(count / elapsed, 1) if elapsed > 0 else 0.0

    @property
    def tokens_per_second(self) -> float:
        total_ms = sum(self.stage_latencies.values())
        if total_ms <= 0:
            # No stage finished yet — fall back to a live estimate.
            tok_seconds = sum(
                (time.perf_counter() - s) for s in self._tok_start_by_stage.values()
            )
            if tok_seconds <= 0:
                return 0.0
            return round(self.total_tokens_generated / tok_seconds, 1)
        return round(self.total_tokens_generated / (total_ms / 1000.0), 1)

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