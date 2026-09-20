# Contributing to Virgo-Eye

First off — thanks for taking the time to contribute.

## Project baseline

- **Backend**: Python 3.12, FastAPI, Pydantic v2, `pytest` / `pytest-asyncio`.
- **Frontend**: Next.js 15 (App Router), React 19, TypeScript **strict**, Tailwind v3.
- **No secrets**: `.env` values are never committed. Use `.env.example`.

## How to get started

1. **Fork** the repository and clone your fork.
2. Create a branch: `git checkout -b <yourname>/<short-description>`.
3. Run the app (demo mode, no GPU needed):

   ```bash
   # backend
   python -m pip install -r backend/requirements.txt
   VIRGO_DEMO_MODE=true python -m uvicorn backend.main:app --port 8000

   # frontend
   cd frontend && npm install && npm run dev
   ```

4. Make your change, then run the full verification below.
5. Open a pull request against `main`.

## Development workflow

### Backend

```bash
cd backend
python -m pytest tests/ -q       # must stay green (schemas + pipeline)
```

New pipeline stages, SSE events, or schemas **must** ship with tests.

- Schemas live in `backend/schema/` and are the contract with the frontend —
  update `frontend/lib/types.ts` in the same PR.
- SSE frame types are listed in `docs/architecture.md#sse-contract` — keep them
  in sync.
- Prefer `async`; the orchestrator runs all four stages against the backend as
  concurrent streaming calls.

### Frontend

```bash
cd frontend
npm run typecheck               # tsc --noEmit, must pass
npm run build                   # production build, must pass
```

- Keep `tsconfig.json` strictness intact — no `any` leaking into new code.
- Styling is Tailwind; theme tokens live in `tailwind.config.ts` (virgo palette,
  keyframes). Don't hardcode hex values.
- New components go in `frontend/components/<feature>/` and can be composed from
  the `shared/` and `ui/` primitives.

## Pull request guidelines

- Reference the issue/feature in the description (`Closes #123`).
- Keep PRs focused; split unrelated changes into separate PRs.
- Update `README.md` and `docs/` when user-visible behavior changes.
- CI must pass (`.github/workflows/ci.yml` runs tests + typecheck + build).
- Conventional-ish commit messages help: `feat:`, `fix:`, `docs:`, `test:`,
  `refactor:`, `chore:`.

## Coding style

- **Python**: PEP 8, 4-space indent, `snake_case`. Type hints on all public
  functions. Docstrings on new modules.
- **TypeScript**: strict mode, `PascalCase` components, `camelCase` functions,
  props modeled on the backend Pydantic types.
- **No comments that just restate the code** — prefer descriptive names.

## Testing tips

- Demo mode runs with zero GPU/Ollama — great for fast local iteration.
- `scripts/generate_test_data.py` produces the canonical sample images
  (PCB / X-ray / blueprint) used by the test suite.
- `scripts/benchmark.py` measures the full 4-stage latency; record changes in
  `docs/benchmarks.md`.

## Questions?

Open a discussion or reach out to the maintainers before starting large work —
we'd rather align on direction than review a big surprise.