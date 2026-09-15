# Model Setup

Virgo-Eye runs on a local Ollama instance (no cloud dependency).

## Primary model

| Model | Notes |
| --- | --- |
| `qwen2-vl:7b-instruct-q4_K_M` | Default. 4-bit AWQ-equivalent quant, ~4 GB VRAM, 30–50 tok/s on consumer GPU. |
| `llava:7b` | Fallback for weaker or non-NVIDIA hardware. |

### Quick start

```bash
# 1. Install Ollama (https://ollama.com)
# 2. Pull the vision model
ollama pull qwen2-vl:7b
# 3. Build the tuned Modelfile (optional but recommended)
ollama create virgo-qwen2-vl -f models/Modelfile
# 4. Point the backend at it (default auto-detects)
#    .env: VIRGO_MODEL=virgo-qwen2-vl   (or qwen2-vl:7b)
```

### Update the model list
```bash
ollama list
```

If `VIRGO_MODEL=auto` (default), the backend probes Ollama `/api/tags`
and picks the first VLM it finds.

## vLLM alternative (production)

```bash
pip install vllm
vllm serve Qwen/Qwen2-VL-7B-Instruct-AWQ --quantization awq \
  --max-model-len 8192 --gpu-memory-utilization 0.85
# .env: VLLM_ENABLED=true
```

## Demo mode

If Ollama is unreachable at startup the backend automatically falls back
to an image-aware **demo engine** so the full UI flow can be shown on any
laptop with zero GPU. `VIRGO_DEMO_MODE=true` forces it.