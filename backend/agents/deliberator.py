"""STAGE 2: Chain-of-Visual-Thought (CoVT) Deliberation agent."""

from typing import Any, AsyncGenerator, Dict

from backend.agents.base_agent import BaseAgent, strip_thought_tags
from backend.prompts.deliberation_prompt import build_deliberation_prompt


class Deliberator(BaseAgent):
    stage_name = "deliberation"

    async def run(
        self, ctx: Any, image_b64: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        if not ctx.map_json:
            yield self._error("Stage 2 requires a Stage 1 map.")
            return
        prompt = build_deliberation_prompt(ctx.map_json, ctx.domain)
        text = ""
        stream = self._stream(image_b64, prompt)
        try:
            async for chunk in stream:
                delta = chunk.get("delta", "")
                text = chunk.get("response", text + delta)
                self._track(chunk)
                yield {
                    "type": "thought",
                    "stage": self.stage_name,
                    "chunk": delta,
                    # expose lightly so the UI can render partial reasoning
                    "clean": strip_thought_tags(delta),
                }
                if chunk.get("done"):
                    break
        except Exception as exc:  # noqa: BLE001
            yield self._error(f"Stage 2 inference failed: {exc}")
            return

        ctx.reasoning_output = text
        yield {
            "type": "stage_result",
            "stage": self.stage_name,
            "data": {"thought_chain": text, "total_tokens_approx": len(text.split())},
        }

    def _error(self, message: str) -> Dict[str, Any]:
        return {"type": "error", "stage": self.stage_name, "message": message}