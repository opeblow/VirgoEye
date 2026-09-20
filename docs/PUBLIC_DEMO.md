# Public demo release

The local release defaults to standard inspection. Additional automated review
is opt-in; the small ablation did not demonstrate improved outcome categories.
Sample images are real, attributed PlantVillage images, and run live analysis.
See `frontend/public/samples/ATTRIBUTION.md` for sources and derivative licensing.

## Deployment requirements

Use one backend process and a persistent volume for `VIRGO_USAGE_DB`. Multiple
replicas with separate databases would each have their own limits. Do not delete
the database on restart: admissions and reservations intentionally persist.

Configure `VIRGO_PUBLIC_MODE=true`, a nonempty `VIRGO_ACCESS_CODE`, the approved
`VIRGO_MAX_ANALYSES` and `VIRGO_DEMO_BUDGET_USD`, plus verified input/output USD
prices per million tokens for the configured Anthropic model. Missing budget,
prices, live key or access code causes startup to fail. Keep secrets server-only.

Both analysis routes require the access code. A global two-inspections-per-minute
limit and a persistent total admission limit apply before analysis. Invalid and
failed inspections still consume admissions. The frontend asks for the code but
does not store it persistently or include it in exports.

Before every model generation, the backend counts input tokens and reserves the
full output allowance plus 20% and 512 input tokens. Reservations are never
refunded, including failed or cancelled calls. This is a conservative application
budget estimate, not a guarantee about provider billing. Use a dedicated provider
workspace and its provider-side spending limit as an additional control; other
applications using the same credentials are outside this ledger. Set prices
correctly and review them if the model changes. Hosting fees are separate.

Use HTTPS and a same-origin frontend `/api` proxy. `BACKEND_URL` is a frontend
build-time setting for the internal backend address. Keep the backend private,
set CORS to the deployed frontend, and avoid logging request bodies or secrets.
The existing GPU/Ollama compose file is not the hosted Anthropic demo setup.

## Release checks

- Run backend tests, frontend build, and report export tests.
- Check one live standard sample; ensure no extra review is claimed.
- Confirm a wrong access code is rejected on both routes.
- Confirm limits survive a backend restart using a temporary test database.
- Verify public URL, browser streaming, report download, mobile layout and
  sample attribution from a fresh browser session before sharing.
- Record the actual deployed commit and model; disclose prior work and the
  small evaluation's limitations in the submission.

A VPS preview has been deployed with a user-approved $4 application budget,
30 total admissions and an access code. Usage persists across container restarts.
Final competition eligibility and a stable submission URL remain prerequisites
for submission. See [VPS_DEPLOYMENT.md](VPS_DEPLOYMENT.md).

## Local release verification (20 September 2026)

79 backend tests passed, frontend production build passed, and standalone report
export test passed. A live standard damaged-leaf inspection completed in 29.2 s;
the deliberately blurred sample completed in 26.1 s and requested a clearer image.
A repeated image correctly displayed three reused stages. Browser error log was
empty on the final build. These are functional checks, not clinical/agronomic
validation or a performance guarantee.

A 3:11 narrated demo was rendered in the separate videos/virgoeye-demo project.
It uses real recorded product interactions, local speech and a user-selected music
bed. Recordings and rendered media are not included in this source repository.
The app now has a temporary HTTPS preview; no submitted entry is recorded here.
