"""Master pipeline — chains the four CoVT stages and streams SSE events."""

import asyncio
import time
from typing import Any, AsyncGenerator, Dict, Optional

from backend import config
from backend.agents.critic import Critic
from backend.agents.deliberator import Deliberator
from backend.agents.spatial_mapper import SpatialMapper
from backend.agents.synthesizer import Synthesizer
from backend.ml_utils.gpu_monitor import GPUMonitor
from backend.ml_utils.ollama_client import OllamaClient
from backend.ml_utils.quantization import normalize_quant
from backend.ml_utils.speed_tracker import SpeedTracker
from backend.ml_utils.vllm_client import VLLMClient
from backend.pipeline.image_processor import (
    ImageValidationError,
    brightness_stats,
    load_from_base64,
)
from backend.pipeline.kv_cache_manager import KVCacheManager, PipelineContext
from backend.schema.api import AnalyzeRequest
from backend.schema.metrics import PerformanceMetrics


class PipelineOrchestrator:
    """Runs image -> map -> thoughts -> critique -> verdict, streaming events."""

    def __init__(
        self,
        ollama: Optional[OllamaClient] = None,
        vllm: Optional[VLLMClient] = None,
        gpu: Optional[GPUMonitor] = None,
        tracker: Optional[SpeedTracker] = None,
    ) -> None:
        self.ollama = ollama or OllamaClient()
        self.vllm = vllm or (VLLMClient() if config.VLLM_ENABLED else None)
        self.gpu = gpu or GPUMonitor()
        self.tracker = tracker or SpeedTracker()
        self.cache = KVCacheManager(
            enabled=config.ENABLE_KV_CACHE, max_stages=config.KV_CACHE_MAX_STAGES
        )
        self._model_name = config.VIRGO_MODEL
        self._quantization = "unknown"
        self._ollama_ok: Optional[bool] = None
        self._demo_mode: bool = config.VIRGO_DEMO_MODE

    async def initialize(self) -> None:
        """Probe the backend, resolve the model, and decide demo vs real mode."""
        # An explicit VIRGO_DEMO_MODE=true always wins (presentation mode).
        if config.VIRGO_DEMO_MODE:
            self._demo_mode = True
            self._model_name = "DEMO-SYSTEM"
            self._quantization = "n/a"
            self._ollama_ok = False
            return
        if self.vllm is not None:
            self._ollama_ok = await self.vllm.health()
            if self._ollama_ok:
                self._model_name = getattr(self.vllm, "model", "vllm-model")
                self._demo_mode = False
            else:
                self._demo_mode = True
                self._model_name = "DEMO-SYSTEM"
                self._quantization = "n/a"
            return
        self._ollama_ok = await self.ollama.health()
        if not self._ollama_ok:
            self._demo_mode = True
            self._model_name = "DEMO-SYSTEM"
            self._quantization = "n/a"
            return
        model = config.VIRGO_MODEL
        if model == "auto":
            model = (await self.ollama.pick_vision_model()) or config.FALLBACK_MODEL
        self._model_name = model
        self._quantization = normalize_quant(model)
        self._demo_mode = False

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def demo_mode(self) -> bool:
        return self._demo_mode

    @property
    def ollama_ok(self) -> Optional[bool]:
        return self._ollama_ok

    def agent(self, cls: type, **kw: Any):
        return cls(
            ollama=self.ollama,
            vllm=self.vllm,
            gpu=self.gpu,
            tracker=self.tracker,
            model_name=self._model_name,
            **kw,
        )

    async def analyze(
        self, req: AnalyzeRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Yield SSE-friendly event dicts. Raises on unrecoverable input errors."""
        t0 = time.perf_counter()
        try:
            processed = load_from_base64(req.image_base64)
        except ImageValidationError as exc:
            yield {"type": "error", "stage": "input", "message": str(exc)}
            return
        image_b64 = processed.base64
        self.tracker = SpeedTracker()

        ctx = PipelineContext(
            image=processed,
            model_name=self._model_name,
            domain=req.domain,
            detail_level=req.detail_level,
            image_hash=self.cache.image_hash(image_b64),
        )
        stats = brightness_stats(processed.image)

        yield {
            "type": "info",
            "stage": "system",
            "data": {
                "image_resolution": processed.resolution_label,
                "domain": req.domain,
                "model": self._model_name,
                "quantization": self._quantization,
                "demo_mode": self._demo_mode,
                "ollama_ok": self._ollama_ok,
            },
        }

        if self._demo_mode:
            async for ev in self._demo_pipeline(ctx, processed, stats, t0):
                yield ev
            return

        async for ev in self._real_pipeline(ctx, image_b64, t0):
            yield ev

    # ------------------------------------------------------------------ real
    async def _real_pipeline(
        self, ctx: PipelineContext, image_b64: str, t0: float
    ) -> AsyncGenerator[Dict[str, Any], None]:
        agents = [
            self.agent(SpatialMapper),
            self.agent(Deliberator),
            self.agent(Critic),
            self.agent(Synthesizer),
        ]
        for agent in agents:
            self.tracker.begin_stage(agent.stage_name)
            cache_key = ctx.stage_prompt_variant(agent.stage_name)
            cached = self.cache.get(cache_key)
            failed = False
            if cached is not None:
                ctx.restore(agent.stage_name, cached)
                yield cached
            else:
                stage_result = None
                async for ev in agent.run(ctx, image_b64):
                    if ev.get("type") == "error":
                        failed = True
                    if ev.get("type") == "stage_result":
                        stage_result = ev
                    yield ev
                if stage_result is not None and not failed:
                    self.cache.store(cache_key, stage_result)
            self.tracker.end_stage(agent.stage_name)
            if failed:
                # A stage error is terminal — later stages only degrade the
                # stream with cascading "requires Stage X" errors.
                return
        async for ev in self._emit_metrics(ctx):
            yield ev

    async def _emit_metrics(
        self, ctx: PipelineContext
    ) -> AsyncGenerator[Dict[str, Any], None]:
        gpu = self.gpu.snapshot()
        metrics = PerformanceMetrics(
            **self.tracker.metrics(
                gpu,
                model_name=self._model_name,
                quantization=self._quantization,
                resolution=ctx.image.resolution_label,
            )
        )
        yield {
            "type": "metrics",
            "stage": "metrics",
            "data": metrics.model_dump(),
        }

    # ------------------------------------------------------------------ demo
    async def _demo_pipeline(
        self,
        ctx: PipelineContext,
        processed: Any,
        stats: Dict[str, Any],
        t0: float,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Deterministic, image-aware synthetic pipeline for UI demos."""
        from backend.pipeline.demo_engine import run_demo_pipeline

        async for ev in run_demo_pipeline(
            ctx, processed, stats, self.tracker, t0, self.gpu, self._model_name, self._quantization
        ):
            yield ev

    async def close(self) -> None:
        await self.ollama.close()
        if self.vllm is not None:
            await self.vllm.close()
        self.gpu.close()