> Historical planning/reference document. For current behavior, setup and evidence, use the [README](../README.md) and [evaluation results](evaluation/reliability/RESULTS.md). Earlier targets and claims below are not validated product results.

# Virgo-Eye — ML Architecture Write-up

**Submission for the SPEED Virgo Challenge.**

## 1. Problem

Frontier multimodal models operate in "fast-thinking" mode: one forward pass,
one glance, one answer. For classification-style questions this is adequate.
For spatially-grounded diagnostics it is not. PCB solder-joint defects, micro-
calcifications in radiographs, and blueprint code violations hide in
sub-pixel discontinuities that require **multi-step spatial + relational +
self-critical deliberation**.

## 2. Chain-of-Visual-Thought (CoVT)

We force the VLM into four sequential, independently-inspectable stages:

### Stage 1 — Spatial Semantic Mapping
The model is prompted to scan the image in a grid pattern and emit a strict
JSON map: every entity with an ID, a human label, a normalized bounding box
`[xmin, ymin, xmax, ymax] ∈ [0,1]⁴`, a confidence, and a category. This map
is the ground-truth spatial reference for the rest of the pipeline. A broken
map cannot be silently recovered later — it is validated by schema before
Stage 2 starts.

### Stage 2 — CoVT Deliberation
Forced `<thought>` monologue. The model must analyze relationships between
mapped entities, cross-reference each claim with exact coordinates, reason
spatially then relationally then causally, and explicitly declare entities
that are *nominal* (with evidence). Streamed to the UI token-by-token.

### Stage 3 — Counter-Factual Verification (Critic)
A second pass with the map + the thought chain checks:
1. Spatial hallucinations (coordinates that don't match the map)
2. Logical fallacies (hasty generalizations)
3. Missed entities (mapped but never analyzed)
4. False positives / negatives
5. Confidence calibration

Output is a structured `VerificationReport` with corrections.

### Stage 4 — Optimized Synthesis
Merge map + thoughts + critique; drop hallucinated claims, use corrected
claims, then emit severity (`CRITICAL/WARNING/NOMINAL`), calibrated confidence,
affected entities, and an evidence chain. Confidence is *reduced* by critic
hallucinations and *increased* by evidence-chain strength.

## 3. Pipeline engineering for SPEED

- **4-bit AWQ quantization** — 7B-class weights ≈ 4 GB VRAM; ~3× faster than
  fp16 for the weight-bound decode path.
- **Single weight residency** — the model stays GPU-pinned across all four
  stages (no CPU↔GPU swaps).
- **KV/level caching** — a `KVCacheManager` fingerprints `(model, image_hash,
  stage)` so a retry or re-run never re-encodes or redundantly re-infers a
  completed stage.
- **Image normalization once** — resize/encode happens one time in
  `image_processor`, then the same normalized tensor is reused in every stage.
- **Streaming, not blocking** — SSE lets the UI render Stage 1 boxes while the
  model is still writing Stage 2; perceived latency ≈ first-token latency.
- **Alternative vLLM backend** — OpenAI-compatible `vLLMClient` with
  continuous batching for production-scale concurrent analysis.

## 4. Model choice

| Model | Size | Quant | VRAM | Notes |
| --- | --- | --- | --- | --- |
| Qwen2-VL-7B-Instruct | 7B | 4-bit | ~4 GB | Dynamic resolution, strong spatial grounding |
| LLaVA-v1.6-Mistral-7B | 7B | 4-bit | ~4 GB | Automatic fallback |

7B-quantized runs 30–50 tok/s on a consumer GPU vs 3–5 tok/s for a 70B class,
which is the difference between "live deliberation stream" and "spin for a
minute".

## 5. Observability

Every pipeline artifact is typed by Pydantic v2 and streamed over SSE:

```
info      → resolution, model, quantization, demo mode
chunk     → stage-1 scan lines (delta tokens)
thought   → stage-2 reasoning stream
stage_result → map / thought-chain / critic report / verdict
metrics   → total latency, per-stage latency, tokens/sec, VRAM, GPU util
error     → structured failure (never kills the stream)
```

## 6. Failure handling

- **No Ollama reachable** → deterministic, pixel-statistics-aware **demo
  engine** with identical event shapes, so the UI is always demonstrable.
- **Unparseable model JSON** → structured error event; pipeline aborts
  cleanly at the offending stage.
- **Unsupported / oversized images** → rejected with typed errors before any
  GPU work.

## 7. Results summary (see benchmarks.md)

Demo-path end-to-end latency on a mid laptop: sub-second for synthetic images.
With a quantized 7B model, first thought tokens stream within a few hundred
ms of upload; full pipeline typically completes in single-digit seconds on
consumer hardware.