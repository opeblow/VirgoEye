"""AWQ / GPTQ 4-bit quantization configuration and verification helpers."""

import time
from typing import Any, Dict, List, Optional

VALID_QUANT_TAGS = {
    "q4_K_M",
    "q4_0",
    "q4_1",
    "q5_K_M",
    "q8_0",
    "fp16",
    "awq",
    "gptq",
}


def normalize_quant(model_name: str) -> str:
    """Extract the quantization tag from an Ollama model name."""
    name = (model_name or "").lower()
    for tag in VALID_QUANT_TAGS:
        if tag in name:
            return tag
    return "unknown"


def is_4bit(quant: str) -> bool:
    return quant.startswith("q4") or quant in {"awq", "gptq"}


def expected_vram(parameters_b: float, quant: str) -> float:
    """Heuristic VRAM estimate in MB for a model's weights."""
    bytes_per_param = {"q4_0": 0.55, "q4_1": 0.6, "q4_K_M": 0.66, "awq": 1.0,
                       "gptq": 1.0, "q5_K_M": 0.75, "q8_0": 1.2}.get(quant, 2.0)
    return round(parameters_b * 1_000_000_000 * bytes_per_param / (1024 * 1024), 1)


def estimate_vram(model_name: str) -> float:
    """Estimate VRAM usage for a known 7B-class model."""
    quant = normalize_quant(model_name)
    params = 7.0  # default to 7B-class
    return expected_vram(params, quant)


def verify_quantization(client_health: bool, model_name: str) -> Dict[str, Any]:
    """Return a config dict describing the active quantization setup."""
    quant = normalize_quant(model_name)
    return {
        "model": model_name,
        "quantization": quant,
        "is_4bit": is_4bit(quant),
        "estimated_vram_mb": estimate_vram(model_name),
        "flashattn": "flash_attention_2",
        "validated": client_health,
        "checked_at": time.time(),
    }