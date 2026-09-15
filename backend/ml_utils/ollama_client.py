"""Ollama REST API client with streaming support."""

import base64
import json
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from backend import config


class OllamaClient:
    """Thin async client over the Ollama generate + chat APIs."""

    def __init__(
        self,
        base_url: str = config.OLLAMA_BASE_URL,
        timeout: float = config.OLLAMA_REQUEST_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._http = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def close(self) -> None:
        await self._http.aclose()

    async def health(self) -> bool:
        try:
            r = await self._http.get("/api/tags", timeout=5.0)
            return r.status_code == 200
        except httpx.HTTPError:
            return False

    async def list_models(self) -> List[str]:
        r = await self._http.get("/api/tags")
        r.raise_for_status()
        data = r.json()
        return [m.get("name", "") for m in data.get("models", [])]

    async def pick_vision_model(self) -> Optional[str]:
        """Choose the best available vision-capable model."""
        try:
            names = await self.list_models()
        except Exception:
            return None
        if not names:
            return None
        priority = [
            "qwen2-vl:7b-instruct-q4_K_M",
            "qwen2-vl:7b",
            "qwen2-vl",
            "llava:7b",
            "llava",
            "llama3.2-vision:11b",
            "bakllava:latest",
        ]
        for pref in priority:
            for name in names:
                if name.startswith(pref):
                    return name
        # fall back to any model that looks like a VL model
        for name in names:
            if "vl" in name or "vision" in name or "llava" in name:
                return name
        return names[0]

    async def generate_stream(
        self,
        model: str,
        image_base64: str,
        prompt: str,
        system: str,
        options: Optional[Dict[str, Any]] = None,
        stream: bool = True,
        raw: bool = False,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream token deltas from Ollama.generate with an image.

        Yields dicts with keys ``delta`` (str), ``text`` (pending but never
        reassigned), ``response`` (full response str), ``done`` (bool).
        """
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "system": system,
            "images": [image_base64],
            "raw": raw,
            "options": {
                "num_predict": config.NUM_PREDICT,
                "temperature": config.TEMPERATURE,
                "top_p": config.TOP_P,
                "seed": config.SEED,
                **({"keep_alive": config.OLLAMA_KEEP_ALIVE_MINUTES} if config.OLLAMA_KEEP_ALIVE_MINUTES else {}),
            },
        }
        if options:
            payload["options"].update(options)

        async with self._http.stream("POST", "/api/generate", json=payload) as resp:
            resp.raise_for_status()
            buf = ""
            async for line in resp.aiter_lines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                token = data.get("response", "")
                done = data.get("done", False)
                buf += token
                yield {
                    "delta": token,
                    "delta_len": len(token),
                    "text": buf,
                    "response": buf,
                    "done": done,
                    "eval_count": data.get("eval_count", 0),
                    "eval_duration_ns": data.get("eval_duration", 0),
                    "total_duration_ns": data.get("total_duration", 0),
                    "load_duration_ns": data.get("load_duration", 0),
                }
                if done:
                    return

    async def generate(
        self,
        model: str,
        image_base64: str,
        prompt: str,
        system: str,
        options: Optional[Dict[str, Any]] = None,
        raw: bool = False,
    ) -> Dict[str, Any]:
        full = {"text": ""}
        async for chunk in self.generate_stream(
            model, image_base64, prompt, system, options=options, stream=True, raw=raw
        ):
            full = chunk
        return full

    async def reset_keepalive(self, model: str) -> None:
        payload = {"model": model, "keep_alive": 0}
        try:
            await self._http.post("/api/generate", json=payload)
        except httpx.HTTPError:
            pass


def encode_image(data: bytes, mime: str) -> str:
    """Base64-encode raw image bytes for multimodal input."""
    return base64.b64encode(data).decode("ascii")


def elapsed_ms(start: float) -> float:
    return (time.perf_counter() - start) * 1000.0