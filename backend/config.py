import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_WORKSPACE_ID = os.getenv("ANTHROPIC_WORKSPACE_ID", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


# --- Model ------------------------------------------------------------------
# If "auto", the client probes Ollama for a loaded vision model at startup.
VIRGO_MODEL = _env("VIRGO_MODEL", "auto")
FALLBACK_MODEL = _env("VIRGO_FALLBACK_MODEL", "llava:7b")
OLLAMA_BASE_URL = _env("OLLAMA_URL", "http://localhost:11434")
OLLAMA_REQUEST_TIMEOUT = _env_float("OLLAMA_TIMEOUT", 600.0)
OLLAMA_KEEP_ALIVE_MINUTES = _env_float("OLLAMA_KEEP_ALIVE", 30.0)

# vLLM alternative (OpenAI-compatible endpoint)
VLLM_ENABLED = _env_bool("VLLM_ENABLED", False)
VLLM_BASE_URL = _env("VLLM_URL", "http://localhost:8000/v1")
VLLM_API_KEY = _env("VLLM_API_KEY", "not-required")
VLLM_MODEL = _env("VLLM_MODEL", "Qwen/Qwen2-VL-7B-Instruct-AWQ")

# --- Image preprocessing ----------------------------------------------------
MAX_IMAGE_SIZE = _env_int("VIRGO_MAX_IMAGE_SIZE", 1280)  # Max longest side px
JPEG_QUALITY = _env_int("VIRGO_JPEG_QUALITY", 85)
SUPPORTED_MIME = {"image/jpeg", "image/png", "image/webp", "image/bmp"}

# --- Pipeline / performance --------------------------------------------------
ENABLE_KV_CACHE = _env_bool("ENABLE_KV_CACHE", True)
KV_CACHE_MAX_STAGES = _env_int("KV_CACHE_MAX_STAGES", 3)
GPU_MEMORY_FRACTION = _env_float("GPU_MEMORY_FRACTION", 0.85)
NUM_PREDICT = _env_int("VIRGO_NUM_PREDICT", 4096)
TEMPERATURE = _env_float("VIRGO_TEMPERATURE", 0.1)
TOP_P = _env_float("VIRGO_TOP_P", 0.9)
SEED = _env_int("VIRGO_SEED", 42)

# --- Server ------------------------------------------------------------------
SSE_RETRY_TIMEOUT = _env_int("SSE_RETRY_TIMEOUT", 3000)  # ms
SSE_PING_INTERVAL = _env_float("SSE_PING_INTERVAL", 15.0)
MAX_IMAGE_BYTES = _env_int("VIRGO_MAX_IMAGE_BYTES", 20 * 1024 * 1024)
CORS_ORIGINS = [o.strip() for o in _env("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]

HOST = _env("VIRGO_HOST", "0.0.0.0")
PORT = _env_int("VIRGO_PORT", 8000)

# --- Fallback mode (no Ollama reachable) -------------------------------------
# When unset (default), the orchestrator auto-detects Ollama at startup and
# falls back to the image-aware demo engine only if unreachable. Set to "true"
# to ALWAYS force demo mode for presentations/CI.
VIRGO_DEMO_MODE = _env_bool("VIRGO_DEMO_MODE", False)

CRITIC_PARALLEL_AGENTS = _env_int("CRITIC_PARALLEL_AGENTS", 1)
# Public demo safeguards. Public mode must be explicitly configured before launch.
PUBLIC_MODE = _env_bool("VIRGO_PUBLIC_MODE", False)
ACCESS_CODE = _env("VIRGO_ACCESS_CODE", "")
MAX_ANALYSES = _env_int("VIRGO_MAX_ANALYSES", 10)
DEMO_BUDGET_USD = _env_float("VIRGO_DEMO_BUDGET_USD", 0.0)
INPUT_USD_PER_M = _env_float("VIRGO_INPUT_USD_PER_M", 0.0)
OUTPUT_USD_PER_M = _env_float("VIRGO_OUTPUT_USD_PER_M", 0.0)
MAX_INPUT_TOKENS = _env_int("VIRGO_MAX_INPUT_TOKENS", 12000)
USAGE_DB = _env("VIRGO_USAGE_DB", str(Path(__file__).resolve().parents[1] / ".runtime" / "usage.sqlite3"))
