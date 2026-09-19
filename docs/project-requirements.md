# Project and Submission Requirements

**Hackathon:** NextStep Hacks 2026 (HackAlphaX, on Devpost) — submit via the
Devpost project page.

This document codifies the eligibility, deliverable, and judging requirements
for the Virgo-Eye submission so the team can check everything before the
deadline. It mirrors the official Devpost rules for **NextStep Hacks 2026**
(theme: **Earth Forward**). Full organizer intel lives in
[`docs/nextstep-hacks-2026.md`](nextstep-hacks-2026.md).

Key dates: build window Aug 21 → **Sep 20, 2026 @ 5:00pm EDT** (extended);
winners announced Sep 26 9:00am EDT. All requirements below are the final
published ones.

## 1. Project eligibility

- Anyone **13–24** as of Aug 21, 2026; **students only**; groups up to 5;
  companies/professional organizations excluded.
- Any software or hardware product built within the specified time frame is
  eligible.
- The product must be original work completed during the hackathon time frame.
- Plagiarized projects, or projects not completed within the time frame, will
  be disqualified.
- The organizers retain **full discretion** over the selection of winners.
- Cross-submission to other hackathons is allowed during the event month only
  if the other hackathon also permits it.
- **Continuing an old project**: the Devpost page MUST specify what was worked
  on (1) before the hackathon and (2) during the hackathon.

### Virgo-Eye status (self-assessment)

- [x] Original 4-stage CoVT pipeline implemented in this repo (backend +
      frontend + models).
- [x] No third-party code copied without license-compatible attribution
      (review deps in `backend/requirements.txt`, `frontend/package.json`).
- [ ] Recorded work log / git history timestamps fall inside the window.
- [ ] "Before vs during hackathon" statement drafted for the Devpost page.

## 2. Required deliverables

### 2.1 Demo video (no longer than 5 minutes)

A video demoing the project is mandatory (rules page: "video 3–5 minutes").

**Virgo-Eye video outline (target ~3.5–4.5 min):**

1. 30 s — Hook: fast-thinking VLMs glance and blurt an answer; sub-pixel
   environmental signals — stressed crops, land-cover change, post-disaster
   damage — hide in breaks of spatial + relational regularity.
2. 60 s — Live demo in **demo mode** (zero GPU): upload an Earth-Forward
   sample (satellite scene / crop field), run a diagnostic, show the 4-stage
   pipeline streaming (Stage 1 bbox map → Stage 2 thought stream → Stage 3
   critic report → Stage 4 calibrated verdict + gauges).
3. 45 s — Second domain for breadth: agriculture (crop stress / disease) or
   disaster damage assessment — same pipeline, different Earth-Forward
   problem.
4. 60 s — Switch to **real inference** (quantized Qwen2-VL-7B via Ollama or
   vLLM), show first thought tokens stream within a few hundred ms and
   end-to-end completion in single-digit seconds on consumer hardware.
5. 45 s — Why it's fast & novel: 4-bit AWQ, single weight residency,
   KV/level caching, image normalization once, SSE streaming, vLLM
   alternative backend, and a self-critic stage that calibrates confidence.
6. 15 s — Links: repo, docs, benchmarks.

Rules and checks:

- [ ] Video length is **between 3:00 and 5:00** (target ≤ 4:30).
- [ ] Demo captured from a real, running instance (not slides).
- [ ] Audio is audible / captions present for the demo portion.
- [ ] Uploaded to an unlisted/public link and linked from the Devpost page.

### 2.2 Devpost project page

The Devpost project page must be filled out, including a repo link and (if
applicable) a live-app link.

Required sections and Virgo-Eye (Earth Forward) content:

- **Title:** Virgo-Eye — the reasoning-first Earth-Forward diagnostic engine
- **Tagline:** A 4-stage Chain-of-Visual-Thought (CoVT) pipeline that maps,
  deliberates, criticizes, and emits calibrated verdicts on environmental
  imagery — ecosystem monitoring, sustainable agriculture, wildlife
  conservation, and climate/disaster assessment.
- **Description:** Fast VLMs glance and answer; Virgo-Eye maps → deliberates →
  verifies → synthesizes a calibrated verdict, streaming every stage to a
  real-time UI. Built to spot the sub-pixel signals pattern-matching misses —
  crop stress, land-cover change, habitat disturbance, post-disaster damage —
  and audit its own reasoning. Demo mode runs with zero GPU; switch to
  Ollama/vLLM for real inference on Qwen2-VL-7B (4-bit AWQ).
- **Submission gallery / images:** upload the favicon
  (`frontend/app/icon.svg`), a UI screenshot with bboxes + thought stream +
  verdict, and a metrics gauge close-up.
- **Built with:** Python, FastAPI, Pydantic v2, Next.js 15, React 19,
  TypeScript, Tailwind, Qwen2-VL-7B (4-bit AWQ), LLaVA-1.6-Mistral-7B, Ollama,
  vLLM, SSE.
- **The video** (section 2.1).
- **Links:** GitHub repo, live demo link if hosted, docs (architecture,
  benchmarks, submission write-up, competition intel).
- **Before vs during hackathon** statement (required for continued projects).

Checklist:

- [ ] All required Devpost fields complete.
- [ ] Demo video embedded or linked.
- [ ] Source repository public and linked.
- [ ] "Before vs during hackathon" statement present.

## 3. Submission rights & display

- The organizers may use **public project information** submitted in future
  advertising.
- The project may be showcased on the website to highlight past winners.

> Implication: do not put private keys, personal data, or non-public assets in
> the Devpost page or repo. `SECURITY.md` already directs private
> vulnerability reports away from public issues.

## 4. Prize & winner selection + sponsors

- Winners are selected at the **full discretion** of the organizers.
- Submissions are judged based on the **specified rubric** (below).
- **Prizes (2026):** 1st $1,000 cash + $500 Claude credits + Final Round
  Interview @ a YC startup + AOPS + XYZ domains + 1yr NordVPN/NordPass/Saily/
  Incogni; 2nd $500 + $250 Claude; 3rd $250 + $100 Claude; participation
  prizes from Wolfram and XYZ.
- **Sponsors:** Claude/Anthropic, Wolfram, Saily, Incogni, XYZ, Kinetik,
  AOPS, NordPass, NordVPN. Sponsor-tech integration ideas are in
  `docs/nextstep-hacks-2026.md` §5.

### Judging rubric (official, verbatim)

| Criterion | Weight | What judges ask | Virgo-Eye lever |
| --- | --- | --- | --- |
| Originality | Equal | Done before at hackathons? How creative is the solution? | 4-stage CoVT with self-critic — not a single-pass API wrapper |
| Adherence to Track | Equal | Does it adhere to "Earth Forward", fully or partially? | Environmental-scene positioning: agriculture / wildlife / disaster / satellite domains, sample data, live demo |
| Completion | Equal | Does the hack work? Everything they wanted? | 42 passing backend tests, typecheck-clean frontend, zero-GPU demo mode |
| Learning | Equal | Did they stretch? Learn something new? | CoVT reasoning, quantization, VLM streaming — documented in the write-up |
| Design | Equal | Thought into UX? How well designed? | Polished streaming dashboard: bboxes, thought terminal, critic report, gauges |
| Technology | Equal | Difficult? Clever? "Wow"? | Multi-stage VLM loop, 4-bit AWQ on consumer VRAM, KV-cache, SSE streaming, vLLM |

All six carry equal stated weight; no single "best skill" — a project must be
strong across the board (which matches past winners: AI + real impact +
polished live demo).

## 5. Pre-deadline checklist

- [ ] Demo video rendered, 3–5 min (target ≤ 4:30), uploaded, linked.
- [ ] Devpost page fully filled out (incl. "before vs during" statement).
- [ ] Repo public; LICENSE, README, CONTRIBUTING, SECURITY present.
- [ ] `cd backend && python -m pytest tests/ -q` green.
- [ ] `cd frontend && npx tsc --noEmit` clean.
- [ ] `cd frontend && npm run build` passes.
- [ ] Benchmarks updated in `docs/benchmarks.md` (see reproduction steps).
- [ ] No secrets in repo (`git log` checked, `.env` untracked).
- [ ] Submitted on Devpost before **Sep 20, 2026 @ 5:00pm EDT**.