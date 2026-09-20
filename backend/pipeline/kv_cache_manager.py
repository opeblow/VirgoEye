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
import json
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional, Tuple

# Bump this whenever a stage prompt/format changes so stale cached
# results are automatically invalidated.
PROMPT_VERSION = "2.3.0"


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
    extra_review: bool = True

    def stage_prompt_variant(self, stage: str, variant: int = 0) -> str:
        """Identifier for caching: model + image + variant inputs + stage.

        Includes domain/detail_level because those change the prompts the
        stages receive (e.g. the domain block prepended to Stage 1).
        """
        return "|".join(
            [
                self.model_name,
                self.image_hash,
                self.domain,
                self.detail_level,
                stage,
                str(variant),
                PROMPT_VERSION,
                str(self.extra_review) if stage in {"critic", "synthesis"} else "shared",
            ]
        )

    def restore(self, stage: str, event: Dict[str, Any]) -> None:
        """Rehydrate this context from a cached stage_result event so
        downstream stages see the same artifacts as a live run."""
        data = event.get("data") or {}
        if stage == "mapping":
            self.map_json = json.dumps(data, ensure_ascii=False)
        elif stage == "deliberation":
            self.reasoning_output = str(data.get("thought_chain", ""))
        elif stage == "critic":
            self.critique_json = json.dumps(data, ensure_ascii=False)


class KVCacheManager:
    """Tracks completed (model, image, variant) stage events per stage."""

    def __init__(self, enabled: bool = True, max_stages: int = 3) -> None:
        self.enabled = enabled
        self.max_stages = max_stages
        self._results: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def image_hash(b64: str) -> str:
        return hashlib.sha256(b64.encode("ascii")).hexdigest()[:16]

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None
        return self._results.get(key)

    def store(self, key: str, value: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        # do not cache error frames — only successful stage results
        if not isinstance(value, dict) or value.get("type") != "stage_result":
            return
        # keep recent results bounded
        if len(self._results) >= self.max_stages * 8:
            self._results.clear()
        self._results[key] = value

    def hits(self) -> int:
        return sum(1 for _ in self._results.values())

    def peek(self, key: str) -> Optional[Dict[str, Any]]:
        return self._results.get(key)

    def clear(self) -> None:
        self._results.clear()

    def keys(self) -> Iterable[str]:
        return self._results.keys()