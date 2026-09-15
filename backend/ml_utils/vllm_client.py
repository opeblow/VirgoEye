"""vLLM OpenAI-compatible client (alternative backend to Ollama)."""

import base64
import json
from typing import Any, AsyncGenerator, Dict, Optional

import httpx

from backend import config


class VLLMClient:
    """Async OpenAI-compatible client for a vLLM serve endpoint."""

    def __init__(
        self,
        base_url: str = config.VLLM_BASE_URL,
        api_key: str = config.VLLM_API_KEY,
        model: str = config.VLLM_MODEL,
        timeout: float = config.OLLAMA_REQUEST_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    async def close(self) -> None:
        await self._http.aclose()

    async def health(self) -> bool:
        try:
            r = await self._http.get("/models", timeout=5.0)
            return r.status_code == 200
        except Exception:
            return False

    @staticmethod
    def _image_payload(image_base64: str) -> Dict[str, Any]:
        return {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
        }

    async def chat_stream(
        self,
        image_base64: str,
        prompt: str,
        system: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": [
                        self._image_payload(image_base64),
                        {"type": "text", "text": prompt},
                    ],
                },
            ],
            "stream": True,
            "max_tokens": config.NUM_PREDICT,
            "temperature": config.TEMPERATURE,
            "top_p": config.TOP_P,
        }
        async with self._http.stream("POST", "/chat/completions", json=payload) as resp:
            resp.raise_for_status()
            buf = ""
            async for raw in resp.aiter_lines():
                if not raw.strip() or raw.startswith("data: [DONE]"):
                    continue
                if raw.startswith("data: "):
                    raw = raw[len("data: ") :]
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                delta = data["choices"][0]["delta"].get("content", "")
                if not delta:
                    continue
                buf += delta
                yield {
                    "delta": delta,
                    "delta_len": len(delta),
                    "text": buf,
                    "response": buf,
                    "done": False,
                    "eval_count": 0,
                    "eval_duration_ns": 0,
                    "total_duration_ns": 0,
                    "load_duration_ns": 0,
                }
        yield {
            "delta": "",
            "delta_len": 0,
            "text": buf,
            "response": buf,
            "done": True,
            "eval_count": 0,
            "eval_duration_ns": 0,
            "total_duration_ns": 0,
            "load_duration_ns": 0,
        }


def encode_image(data: bytes, mime: str) -> str:
    return base64.b64encode(data).decode("ascii")