"""Base agent: shared Ollama/vLLM connection, streaming, metrics hooks."""

import asyncio
import json
import re
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, Optional

from backend import config
from backend.ml_utils.gpu_monitor import GPUMonitor
from backend.ml_utils.ollama_client import OllamaClient
from backend.ml_utils.speed_tracker import SpeedTracker
from backend.ml_utils.vllm_client import VLLMClient


class BaseAgent(ABC):
    """Every pipeline stage subclasses BaseAgent."""

    stage_name: str = "base"

    def __init__(
        self,
        ollama: Optional[OllamaClient] = None,
        vllm: Optional[VLLMClient] = None,
        gpu: Optional[GPUMonitor] = None,
        tracker: Optional[SpeedTracker] = None,
        model_name: str = "",
    ) -> None:
        self.ollama = ollama or OllamaClient()
        self.vllm = vllm
        self.gpu = gpu or GPUMonitor()
        self.tracker = tracker or SpeedTracker()
        self.model_name = model_name or config.VIRGO_MODEL
        self._system = ""

    def set_system_prompt(self, prompt: str) -> None:
        self._system = prompt

    @abstractmethod
    async def run(
        self, ctx: Any, image_b64: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Yield per-token/event dicts; final event has done=True."""
        yield {"done": True}

    # ----- shared streaming helpers -----------------------------------------
    async def _stream_ollama(
        self, image_b64: str, prompt: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        async for chunk in self.ollama.generate_stream(
            model=self.model_name,
            image_base64=image_b64,
            prompt=prompt,
            system=self._system,
            raw=False,
        ):
            yield chunk

    async def _stream_vllm(
        self, image_b64: str, prompt: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        assert self.vllm is not None
        options = {}
        if getattr(self.vllm, "supports_response_schema", False):
            from backend.schema.diagnostic_map import DiagnosticMap
            from backend.schema.verification import VerificationReport
            from backend.schema.verdict import FinalVerdict
            schema = {"mapping": DiagnosticMap, "critic": VerificationReport, "synthesis": FinalVerdict}.get(self.stage_name)
            if schema is not None:
                options["response_schema"] = schema.model_json_schema()
        async for chunk in self.vllm.chat_stream(
            image_base64=image_b64, prompt=prompt, system=self._system, **options
        ):
            yield chunk

    def _stream(self, image_b64: str, prompt: str):
        if self.vllm is not None:
            return self._stream_vllm(image_b64, prompt)
        return self._stream_ollama(image_b64, prompt)

    def _track(self, chunk: Dict[str, Any]) -> None:
        delta = chunk.get("delta") or ""
        if delta:
            # delta length is characters, not tokens — approximate ~4 chars/
            # token so throughput numbers are not inflated by raw char counts.
            self.tracker.record_tokens(self.stage_name, max(1, len(delta) // 4))
        eval_count = chunk.get("eval_count")
        if eval_count:
            # Ollama reports the exact cumulative token count on the final
            # chunk; it is authoritative for this stage.
            self.tracker.record_eval_count(self.stage_name, int(eval_count))


def extract_json_block(text: str) -> str:
    """Pull the first balanced JSON object/array out of arbitrary model text."""
    text = text.strip()
    start = min(
        [i for i in (text.find("{"), text.find("[")) if i != -1], default=-1
    )
    if start == -1:
        raise ValueError("No JSON object found in model output")
    depth = 0
    in_str = False
    esc = False
    end = -1
    for i in range(start, len(text)):
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c in "{[":
            depth += 1
        elif c in "}]":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end == -1:
        raise ValueError("Unbalanced JSON in model output")
    return text[start:end]


def parse_json(text: str) -> Any:
    block = extract_json_block(text)
    return json.loads(block)


def strip_thought_tags(text: str) -> str:
    """Remove <thought>...</thought> wrappers, keep inner content."""
    return re.sub(r"<\s*/\s*thought\s*>", "", re.sub(r"<\s*thought\s*>", "", text))


async def first_done(agen: AsyncGenerator[Dict[str, Any], None]) -> Dict[str, Any]:
    """Consume a generator, returning only the last (final) chunk."""
    final: Dict[str, Any] = {}
    async for chunk in agen:
        final = chunk
    return final