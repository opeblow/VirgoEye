"""KV-cache reuse strategy across pipeline stages.

The same image is passed to every stage. We can't literally reuse
Ollama's KV cache across separate generate calls (the server does not
expose it), but we *can*:
  1. Avoid re-encoding / re-sending the image — reuse the ProcessedImage.
  2. Batch the image embedding once and share it (via the ``images``
     deduplication in the Ollama options), which is what
     ``allow_same_image_rows`` / prefixed prompts buy us.
  3. Track which (model, image_hash, stage) payloads already ran so we
     skip redundant computation in a retry/tune loop.

This module implements the bookkeeping and the image-batching hint.
"""

import hashlib
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Tuple


@dataclass
class PipelineContext:
    """Carried across all four stages."""

    image: object
    model_name: str = ""
    domain: str = "auto"
    detail_level: str = "high"
    image_hash: str = ""
    reasoning_output: str = ""
    map_json: str = ""
    critique_json: str = ""
    metrics: Dict = field(default_factory=dict)

    def stage_prompt_variant(self, stage: str, variant: int = 0) -> str:
        """Identifier for caching: model + image + stage + variant."""
        return f"{self.model_name}|{self.image_hash}|{stage}|{variant}"


class KVCacheManager:
    """Tracks completed (model, image) inference results per stage."""

    def __init__(self, enabled: bool = True, max_stages: int = 3) -> None:
        self.enabled = enabled
        self.max_stages = max_stages
        self._results: Dict[str, str] = {}

    @staticmethod
    def image_hash(b64: str) -> str:
        return hashlib.sha256(b64.encode("ascii")).hexdigest()[:16]

    def get(self, key: str) -> Optional[str]:
        if not self.enabled:
            return None
        return self._results.get(key)

    def store(self, key: str, value: str) -> None:
        if not self.enabled:
            return
        # keep recent results bounded
        if len(self._results) >= self.max_stages * 8:
            self._results.clear()
        self._results[key] = value

    def hits(self) -> int:
        return sum(1 for _ in self._results.values())

    def peek(self, key: str) -> Optional[str]:
        return self._results.get(key)

    def clear(self) -> None:
        self._results.clear()

    def keys(self) -> Iterable[str]:
        return self._results.keys()