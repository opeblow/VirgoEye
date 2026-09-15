<div align="center">

<img src="./frontend/app/icon.svg" alt="Virgo-Eye favicon" width="96" />

# Virgo-Eye

**Reasoning-first multimodal diagnostic engine on a 4-stage
Chain-of-Visual-Thought (CoVT) pipeline.**

Fast-thinking LLMs glance at an image and blurt out an answer. Virgo-Eye
forces a vision-language model into slow, deliberate, observable reasoning:
**map every entity → reason about relationships → verify against itself →
produce a calibrated verdict** — while streaming every stage to a real-time UI.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](backend/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](backend/main.py)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=next.js&logoColor=white)](frontend/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](frontend/)
[![TypeScript](https://img.shields.io/badge/TypeScript-strict-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](frontend/tsconfig.json)
[![License](https://img.shields.io/badge/License-MIT-red?style=for-the-badge)](LICENSE)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](.github/workflows/ci.yml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge)](CONTRIBUTING.md)

</div>

Targets where pattern-matching fails: **PCB fault detection, medical imaging,
architectural plan analysis, satellite/aerial change detection.**

## The 4-stage CoVT pipeline

```
  image
   │
   ▼
 ┌─────────────────────────┐   stage: spatial semantic mapping
 │ STAGE 1  SpatialMapper  │──► DiagnosticMap JSON (entities + bboxes)
 └─────────────────────────┘
   │
   ▼
 ┌─────────────────────────┐   stage: chain-of-visual-thought
 │ STAGE 2  Deliberator    │──► <thought>…</thought> stream, SSE chunks
 └─────────────────────────┘
   │
   ▼
 ┌─────────────────────────┐   stage: critic verification
 │ STAGE 3  Critic         │──► VerificationReport (hallucinations, gaps)
 └─────────────────────────┘
   │
   ▼
 ┌─────────────────────────┐   stage: optimized synthesis
 │ STAGE 4  Synthesizer    │──► FinalVerdict (severity + confidence + evidence)
 └─────────────────────────┘
   │
   ▼
 metrics: latency, tokens/sec, VRAM, tok throughput
```

Every stage crosses a strict Pydantic v2 gate. Every SSE frame is tagged with
its stage so the UI can render mapping boxes, a streaming thought terminal, a
critic report, and calibrated gauges in real time.

## Quick start

### Demo mode (zero GPU, full UI in 30 seconds)

Demo mode is fully **image-aware**, computing real pixel statistics so the
synthetic-but-structured output is meaningful. No model, no Ollama, no cloud.

```bash
# terminal 1 — backend
cd backend && pip install -r requirements.txt
python -m uvicorn backend.main:app --port 8000

# terminal 2 — frontend  (install once)
cd frontend && npm install && npm run dev
# open http://localhost:3000
```

Upload any image, pick a domain, press **RUN DIAGNOSTIC**. The 4-stage
pipeline streams into the UI immediately.

### Real inference (Ollama)

```bash
ollama pull qwen2-vl:7b
ollama create virgo-qwen2-vl -f models/Modelfile
# .env: VIRGO_MODEL=virgo-qwen2-vl
```

If `VIRGO_MODEL=auto` (default) the backend probes Ollama at startup and picks
the best vision model it finds. `scripts/setup_ollama.sh` automates this.

### vLLM (production-grade batched inference)

```bash
vllm serve Qwen/Qwen2-VL-7B-Instruct-AWQ --quantization awq --gpu-memory-utilization 0.85
# .env: VLLM_ENABLED=true VLLM_MODEL=Qwen/Qwen2-VL-7B-Instruct-AWQ
```

### Docker

```bash
docker compose up --build
```

## Stack

| Layer | Tech |
| --- | --- |
| Backend | Python 3.12, FastAPI, SSE (`sse-starlette`), Pydantic v2, agent classes |
| Models | Qwen2-VL-7B (4-bit AWQ), LLaVA-1.6-Mistral-7B fallback — via Ollama or vLLM |
| Frontend | Next.js 15 App Router, React 19, TypeScript strict, Tailwind v3, framer-motion, lucide |
| Speed | 4-bit AWQ quantization, KV-cache bookkeeping across stages, streaming token tracking, GPU monitors |

## Repository layout

```
VirgoEye/
├── README.md                      # this file
├── LICENSE                        # MIT
├── CONTRIBUTING.md                # dev setup + PR guidelines
├── SECURITY.md                    # how to report vulnerabilities
├── CODE_OF_CONDUCT.md             # Contributor Covenant 2.1
├── docker-compose.yml             # ollama + backend + frontend
├── .env.example                   # configuration template
├── .gitignore
├── .github/
│   ├── dependabot.yml             # weekly dep updates (actions, pip, npm)
│   └── workflows/
│       └── ci.yml                 # pytest + typecheck + build + E2E smoke
│
├── backend/                       # FastAPI service
│   ├── main.py                    # SSE /v1/analyze, /v1/health
│   ├── config.py                  # env-driven configuration
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── agents/                    # one class per CoVT stage
│   │   ├── base_agent.py          # streaming + JSON extraction helpers
│   │   ├── spatial_mapper.py      # STAGE 1 — semantic map
│   │   ├── deliberator.py         # STAGE 2 — coVT thought chain
│   │   ├── critic.py              # STAGE 3 — counter-factual verification
│   │   └── synthesizer.py         # STAGE 4 — calibrated verdict
│   ├── pipeline/
│   │   ├── orchestrator.py        # chains stages, owns SSE framing
│   │   ├── image_processor.py     # decode/normalize/resize once
│   │   ├── kv_cache_manager.py    # (model, image, stage) result cache
│   │   └── demo_engine.py         # image-aware zero-GPU fallback
│   ├── ml_utils/
│   │   ├── ollama_client.py       # Ollama /api/generate streamer
│   │   ├── vllm_client.py         # OpenAI-compatible batch backend
│   │   ├── quantization.py        # 4-bit AWQ helpers / VRAM sizing
│   │   ├── gpu_monitor.py         # pynvml, CPU-safe fallback
│   │   └── speed_tracker.py       # per-stage latency + tok/s
│   ├── schema/                    # strict Pydantic contract types
│   │   ├── diagnostic_map.py
│   │   ├── thought_stream.py
│   │   ├── verification.py
│   │   ├── verdict.py
│   │   ├── metrics.py
│   │   └── api.py
│   ├── prompts/
│   │   ├── system_prompts.py      # master prompt + domain contexts
│   │   ├── spatial_prompt.py
│   │   ├── deliberation_prompt.py
│   │   ├── critic_prompt.py
│   │   └── synthesis_prompt.py
│   └── tests/
│       ├── test_schemas.py
│       ├── test_pipeline.py
│       ├── test_agents.py
│       └── sample_images/         # pcb_fault, xray_sample, blueprint_sample
│
├── frontend/                      # Next.js 15 dashboard
│   ├── app/
│   │   ├── layout.tsx             # fonts, theme, shell
│   │   ├── page.tsx               # single-page pipeline dashboard
│   │   └── globals.css
│   ├── lib/
│   │   ├── types.ts               # TS mirror of backend schemas
│   │   ├── constants.ts           # stage/severity/domain constants
│   │   ├── api.ts                 # /api base + endpoint helpers
│   │   ├── sse-parser.ts          # server-sent-event framing
│   │   └── utils.ts
│   ├── hooks/
│   │   ├── useSSEStream.ts
│   │   ├── useDiagnosticPipeline.ts
│   │   ├── useBoundingBoxes.ts
│   │   └── useGPUMetrics.ts
│   ├── components/
│   │   ├── layout/                # Header, SplitPane, Footer
│   │   ├── diagnostic/            # ImageUploader, DiagnosticCanvas, bbox
│   │   │                         #   overlay, EntityList, AnomalyHighlight
│   │   ├── reasoning/             # ThoughtTerminal, CriticReport, VerdictCard,
│   │   │                         #   ScanLineEffect, StageIndicator
│   │   ├── metrics/               # MetricCards + 4 animated gauges
│   │   ├── shared/                # GlassCard, PulsingDot, TypewriterText
│   │   └── ui/                    # button, badge, card primitives
│   ├── Dockerfile
│   ├── next.config.js             # /api → backend rewrite
│   └── package.json
│
├── models/
│   ├── Modelfile                  # Ollama model definition
│   └── README.md
│
├── scripts/
│   ├── setup_ollama.sh            # one-command model bootstrap
│   ├── benchmark.py               # end-to-end latency harness
│   └── generate_test_data.py      # canonical PCB/X-ray/blueprint samples
│
└── docs/
    ├── submission.md              # ML write-up (the "why")
    ├── architecture.md            # diagrams + SSE contract
    └── benchmarks.md              # speed numbers + how to reproduce
```

## Tests & verification

```bash
cd backend && python -m pytest tests/ -q        # schemas + pipeline + agents
cd frontend && npx tsc --noEmit                 # strict typecheck
cd frontend && npm run build                    # production build
```

CI (`.github/workflows/ci.yml`) runs all three plus an E2E smoke test that
drives an analysis through the running frontend proxy.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). TL;DR: tests must stay green,
typecheck must pass, `frontend/lib/types.ts` must mirror backend schemas,
and SSE frame types must match `docs/architecture.md`.

## Security

Found a vulnerability? Report it privately — see [SECURITY.md](SECURITY.md).
No public GitHub issues for security bugs.

## License

[MIT](LICENSE).