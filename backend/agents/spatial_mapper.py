"""STAGE 1: Spatial Semantic Mapping agent."""

import asyncio
from typing import Any, AsyncGenerator, Dict

from backend import config
from backend.agents.base_agent import BaseAgent, extract_json_block, parse_json
from backend.prompts.spatial_prompt import build_spatial_prompt
from backend.schema.diagnostic_map import DiagnosticMap


class SpatialMapper(BaseAgent):
    stage_name = "mapping"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.set_system_prompt(
            "You are the Virgo-Diagnostic Engine v2.0. You output ONLY strict "
            "JSON in every stage. Never add prose outside the JSON. The JSON "
            "outermost object is exactly what the caller expects."
        )

    async def run(
        self, ctx: Any, image_b64: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        prompt = build_spatial_prompt(ctx.domain)
        text = ""
        stream = self._stream(image_b64, prompt)
        try:
            async for chunk in stream:
                delta = chunk.get("delta", "")
                text = chunk.get("response", text + delta)
                self._track(chunk)
                yield {"type": "chunk", "stage": self.stage_name, "delta": delta}
                if chunk.get("done"):
                    break
        except Exception as exc:  # noqa: BLE001 — surfaced as structured error
            yield self._error(f"Stage 1 inference failed: {exc}")
            return

        try:
            block = extract_json_block(text)
        except ValueError as exc:
            yield self._error(f"Stage 1 produced no JSON: {exc}")
            return

        try:
            obj = parse_json(block)
            diagnostic_map = DiagnosticMap.model_validate(obj)
        except Exception as exc:  # noqa: BLE001
            yield self._error(f"Stage 1 schema validation failed: {exc}")
            return

        ctx.map_json = diagnostic_map.model_dump_json()
        yield {
            "type": "stage_result",
            "stage": self.stage_name,
            "data": diagnostic_map.model_dump(),
        }

    def _error(self, message: str) -> Dict[str, Any]:
        return {"type": "error", "stage": self.stage_name, "message": message}