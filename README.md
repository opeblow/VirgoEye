# VirgoEye

**See the concern. Plan the next check.**

VirgoEye turns a crop photograph into visible observations, approximate image regions, and a practical next inspection step. It helps someone prepare for a field check while keeping the limits of a single photograph visible.

[Quick start](#quick-start) · [How it works](#how-it-works) · [Evaluation](#evaluation-and-limitations) · [Public deployment](docs/PUBLIC_DEMO.md) · [Sample attribution](frontend/public/samples/ATTRIBUTION.md)

## What is built

- **Accessible input:** upload a crop photo or choose a sourced healthy-labelled, damaged, or deliberately blurred example.
- **Live analysis:** Anthropic-backed vision requests stream progress into the browser; configured provider failures are reported instead of replaced with simulated findings.
- **Inspectable evidence:** select detected regions, read observations, and compare them with the image. Bounding boxes are approximate.
- **Clear next steps:** findings and recommended actions appear first. Unusable or uncertain input requires further review; incomplete action text receives explicitly labelled general guidance.
- **Portable reports:** download a standalone HTML report containing the photo, evidence, region references, next action and limitations. Open it in a browser or print it as PDF.
- **Optional automated review:** the standard inspection uses three stages. An additional critic pass is available, but does not establish independent expert verification.

The focused product is a crop-inspection prototype for the Earth Forward theme. Other domain adapters and local inference paths remain in the repository as experimental infrastructure, not validated product capabilities.

## Quick start

Use Python 3.12+, Node.js 20+, and npm. Run backend commands **from the repository root**.

```bash
git clone https://github.com/opeblow/VirgoEye.git
cd VirgoEye
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
cp .env.example .env
```

On Windows, activate with `.venv\Scripts\activate` and use the equivalent environment-variable syntax for your shell.

### Real image analysis

Set `ANTHROPIC_API_KEY` in the ignored `.env` file. Set `ANTHROPIC_WORKSPACE_ID` if required by your account, and choose `ANTHROPIC_MODEL` from models available to it. Keep credentials on the server; never use a `NEXT_PUBLIC_` variable for a secret.

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open <http://localhost:3000/dashboard>. The frontend proxies `/api/v1/*` to the backend. Configure `BACKEND_URL` before starting or building Next.js if the backend address differs. API documentation is available at <http://127.0.0.1:8000/docs>.

Live analysis sends the selected image to Anthropic and incurs provider charges. Upload only images you intend to share with that service. Three requests are used for a standard uncached inspection; enabling the critic adds a fourth. Repeated inputs may reuse earlier stage outputs, which the UI identifies. Set `ENABLE_KV_CACHE=false` for an uncached demonstration or evaluation.

### Simulation without a key

```bash
VIRGO_DEMO_MODE=true python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

This exercises the UI with synthetic, image-aware output. It is not real model inference or evidence of inspection accuracy. Keep simulation and live demonstrations clearly distinguished.

For the demonstrated ports (backend 8011, frontend 3011), production-build commands and evaluation scripts, see [local setup](docs/RUN_LOCAL.md). Do not run a Next.js development server and production build against the same `.next` directory simultaneously.

## How it works

```text
Crop photograph
    ↓
1. Map approximate regions
    ↓
2. Describe visible evidence and uncertainty
    ↓
3. Optional automated critic
    ↓
4. Synthesize a provisional finding and next check
    ↓
Deterministic review safeguards → UI + downloadable report
```

Pydantic schemas validate structured outputs, and server-sent events carry progress and results to Next.js. Evidence references must point to mapped entities. Review safeguards prevent rejected or unsuitable findings from appearing as a verified all-clear and replace empty/template-only action text with disclosed general guidance.

The displayed evidence is model-generated explanatory output, not a verified account of internal reasoning. Confidence values are uncalibrated model estimates, not measured probabilities. The stage cache reuses results; it does not demonstrate transformer KV-cache acceleration.

## Evaluation and limitations

A six-case development evaluation compared a standard inspection with an added critic while sharing the upstream map and observations. **Five completed pairs agreed on the visible-concern category; one case failed.** Agreement does not establish correctness, and this small test did not demonstrate a category-level benefit from the critic. Additional review therefore remains opt-in.

Read the [method and results](docs/evaluation/reliability/RESULTS.md), [case manifest](docs/evaluation/reliability/manifest.json), and [regression notes](docs/evaluation/reliability/REGRESSIONS.md). Evaluation scripts can make paid API calls and preserve earlier result files.

Important limits:

- Controlled PlantVillage leaf photos do not represent field deployment conditions.
- A single photo cannot establish a disease cause, justify treatment, or establish whole-plant health.
- Region boxes and observations can be wrong; broader field testing and agronomist review are outstanding.
- Model latency and outputs vary. Functional demos are not performance or accuracy guarantees.
- Public hosting and final competition eligibility remain unconfirmed. No public app deployment is claimed.

A narrated demo with real product recordings was rendered separately. Large recordings, music and rendered video files are not stored in this source repository.

## Repository layout

```text
backend/
  agents/          Mapping, observations, critic and synthesis
  pipeline/        Orchestration, cache and deterministic review policy
  ml_utils/        Provider clients and metrics helpers
  prompts/         Stage prompts
  schema/          Request, evidence and result contracts
  tests/           Automated backend tests
frontend/
  app/             Landing page and inspection workspace
  components/      Image, evidence, progress and result UI
  lib/             API contracts and standalone report export
  public/samples/  Attributed sample images
  tests/           Report export test
scripts/evaluation/  Reproducible development evaluation tools
docs/                Setup, deployment requirements and evaluation records
```

Stack: FastAPI, Pydantic, Python, Next.js 15, React 19, TypeScript and Tailwind. Ollama/vLLM adapters and Docker scaffolding remain available for experimentation; they are not the verified hosted Anthropic deployment path.

## Tests

```bash
# Repository root, with the virtual environment active
python -m pytest -q

# frontend/
npm ci
npm run test:report
npm run typecheck
npm run build
```

CI runs backend tests, report export checks, TypeScript checks, a production build and a simulation-mode API/proxy smoke test. Live provider quality is evaluated separately; CI requires no Anthropic key.

## Public deployment

Read [PUBLIC_DEMO.md](docs/PUBLIC_DEMO.md) before exposing the app. Public mode requires persistent admission/budget storage, configured model prices and an approved budget. An access code is required by default; explicitly set `VIRGO_OPEN_ACCESS=true` for anonymous use with the same spending and admission limits. The application budget is a conservative estimate, not a guarantee about provider billing. Use a provider-side spending limit too.

For a CPU-only server with the Anthropic API, see the [VPS deployment guide](docs/VPS_DEPLOYMENT.md). It includes production containers, persistent usage storage, restart behavior, and temporary HTTPS preview limitations.

The current public guard is designed for one backend process with persistent storage. Production use still needs HTTPS, operational monitoring and deployment verification. Keep credentials, usage ledgers and private images out of Git.

## Attribution and contributions

Bundled sample images are credited to PlantVillage authors Sharada P. Mohanty, David P. Hughes and Marcel Salathé under CC BY-SA 3.0. The blurred sample is a labelled derivative. See [full sources and licensing](frontend/public/samples/ATTRIBUTION.md); dataset labels are not VirgoEye diagnoses.

Codex assisted with implementation, evaluation, testing, documentation and demo preparation. The team remains responsible for reviewing findings, describing limitations and checking submission rules. Earlier planning documents are retained as historical context, not current product claims.

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Code of conduct](CODE_OF_CONDUCT.md)

## License

Source code: [MIT](LICENSE). Sample images retain their separate attribution and share-alike terms.
