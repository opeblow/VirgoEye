"""STAGE 4: Optimized Synthesis — Final Verdict agent."""

from typing import Any, AsyncGenerator, Dict

from backend.agents.base_agent import BaseAgent, extract_json_block, parse_json
from backend.prompts.synthesis_prompt import build_synthesis_prompt
from backend.schema.verdict import FinalVerdict, Severity
from backend.pipeline.review_policy import apply_review_policy


class Synthesizer(BaseAgent):
    stage_name = "synthesis"

    async def run(
        self, ctx: Any, image_b64: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        if not ctx.map_json or not ctx.reasoning_output or not ctx.critique_json:
            yield self._error("Stage 4 requires map + thoughts + critique.")
            return

        prompt = build_synthesis_prompt(
            ctx.map_json, ctx.reasoning_output, ctx.critique_json
        )
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
        except Exception as exc:  # noqa: BLE001
            yield self._error(f"Stage 4 inference failed: {exc}")
            return

        try:
            payload = parse_json(extract_json_block(text))
            # Summary is display-only; keep the full finding and evidence intact.
            if isinstance(payload.get("summary"), str) and len(payload["summary"]) > 500:
                payload["summary"] = payload["summary"][:497] + "..."
            verdict = FinalVerdict.model_validate(payload)
        except Exception as exc:  # noqa: BLE001
            yield self._error(f"Stage 4 schema validation failed: {exc}")
            return

        try:
            verdict = apply_review_policy(verdict, ctx.map_json, ctx.critique_json)
        except ValueError as exc:
            yield self._error(str(exc))
            return

        yield {
            "type": "stage_result",
            "stage": self.stage_name,
            "data": verdict.model_dump(),
        }

    def _error(self, message: str) -> Dict[str, Any]:
        return {"type": "error", "stage": self.stage_name, "message": message}