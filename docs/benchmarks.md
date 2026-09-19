# Speed Benchmarks

> Representative numbers. Fill in with your hardware. Record via
> `scripts/benchmark.py`.

## Methodology

- Sample images: `scripts/generate_test_data.py` (Earth-Forward set:
  satellite land-cover, crop stress, wildlife disturbance, disaster flood;
  plus PCB, X-ray, blueprint).
- `scripts/benchmark.py` runs the full 4-stage pipeline per image and reports
  wall-clock end-to-end latency from the orchestrator.
- Real-inference metrics (tokens/sec, VRAM) come from the `metrics` SSE frame
  emitted at the end of every analysis.

## Demo path (no GPU — image-aware demo engine)

| Sample | End-to-end (ms) | Notes |
| --- | --- | --- |
| pcb_fault.png | ~350 | deterministic, pixel-statistics driven |
| xray_sample.png | ~340 | |
| blueprint_sample.png | ~350 | |
| satellite_landcover.png | ~350 | |
| crop_stress.png | ~350 | |
| wildlife_disturbance.png | ~350 | |
| disaster_flood.png | ~355 | |

## Real inference — template (fill after running on target GPU)

| Metric | Value |
| --- | --- |
| Model | Qwen2-VL-7B-Instruct q4_K_M |
| Quantization | 4-bit AWQ |
| VRAM resident | ~4 GB |
| Tokens/sec (decode) | 30–50 |
| First-thought-token latency | ~300 ms |
| Full pipeline (4 stages) | ~5–8 s @ 1280px |

## Speed engineering checklist

- [x] Image resized/encoded once, reused across all 4 stages
- [x] KV-cache / stage-result cache keyed by `(model, image_hash, stage)`
- [x] Token streaming so perceived latency = first token, not completion
- [x] 4-bit AWQ quantization config + VRAM estimator
- [x] GPU monitor (VRAM, util, temp) surfaced in every metrics frame
- [x] Optional vLLM backend for continuous batching
- [x] SSE keeps the frontend rendering Stage-1 boxes during Stage-2 reads

## Running your own

```bash
python scripts/generate_test_data.py
python scripts/benchmark.py
```