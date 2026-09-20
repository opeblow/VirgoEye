# Run the crop-inspection build

From the repository root, place ANTHROPIC_API_KEY in the ignored `.env` file. If the key is organization-scoped, also set ANTHROPIC_WORKSPACE_ID. Optional ANTHROPIC_MODEL overrides the default Claude Haiku model. Credentials are server-only and are never prefixed NEXT_PUBLIC_. Requests with a configured Anthropic key fail visibly on provider errors instead of switching to simulated findings.

Backend (from repository root):

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
CORS_ORIGINS=http://127.0.0.1:3011,http://localhost:3011 .venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8011
```

Frontend (from `frontend`):

```sh
npm ci
BACKEND_URL=http://127.0.0.1:8011 npm run build
npm run start -- --port 3011
```

Open http://127.0.0.1:3011/. Do not run Next dev and build against the same `.next` directory simultaneously. Restart the backend after changing `.env`.

The upload notice explains that live analysis sends the image to Anthropic. A standard uncached inspection performs three model requests; selecting additional automated review performs four, capped at 3,000 output tokens each with automatic retries disabled. It can incur API charges. The current local server serializes analyses to isolate stage accounting; it is not a public multi-tenant deployment. Public safeguards are implemented but disabled locally. Configure them as described in PUBLIC_DEMO.md before deployment.

The report button downloads a standalone HTML file containing the image, evidence, reviewer notes, limitations and next action. Open the file in a browser to read or print/save as PDF. Model-generated text is escaped.

Validation: `python -m pytest -q` from the root; `node --test tests/report.test.cjs` and `npm run build` from `frontend`.

Reliability evaluation: `python scripts/evaluation/run_reliability.py` runs six cases with a shared-upstream no-critic comparison (up to five paid model calls per case). It skips result files already recorded. The cases and expectations are documented in `docs/evaluation/reliability/manifest.json`. Preserve prior results rather than overwriting failures; use a separate output directory for later versions. `python scripts/evaluation/summarize_reliability.py` regenerates the initial comparison. Post-fix notes live separately in `REGRESSIONS.md`.
