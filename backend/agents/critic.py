"""STAGE 3: Counter-Factual Verification (Critic) agent."""

from typing import Any, AsyncGenerator, Dict

from backend.agents.base_agent import BaseAgent, extract_json_block, parse_json
from backend.prompts.critic_prompt import build_critic_prompt
from backend.schema.verification import VerificationReport


class Critic(BaseAgent):
    stage_name = "critic"

    async def run(
        self, ctx: Any, image_b64: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        if not ctx.map_json or not ctx.reasoning_output:
            yield self._error("Stage 3 requires map + thought chain.")
            return

        prompt = build_critic_prompt(ctx.map_json, ctx.reasoning_output)
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
            yield self._error(f"Stage 3 inference failed: {exc}")
            return

        try:
            report = VerificationReport.model_validate(
                parse_json(extract_json_block(text))
            )
        except Exception as exc:  # noqa: BLE001
            yield self._error(f"Stage 3 schema validation failed: {exc}")
            return

        ctx.critique_json = report.model_dump_json()
        yield {
            "type": "stage_result",
            "stage": self.stage_name,
            "data": report.model_dump(),
        }

    def _error(self, message: str) -> Dict[str, Any]:
        return {"type": "error", "stage": self.stage_name, "message": message}