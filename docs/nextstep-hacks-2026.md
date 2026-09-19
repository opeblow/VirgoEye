# NextStep Hacks 2026 — Competition Intel & Game Plan

Compiled from the official Devpost page, rules, dates, sponsors page, and past
winners' galleries. All facts re-verify before the deadline — hackathon
details can change.

## 1. Event facts

| Field | Value |
| --- | --- |
| Organizer | HackAlphaX (student-run; 3,000+ students reached in 6 years) |
| Title | "Breaking barriers, one idea at a time." |
| **Theme** | **Earth Forward** — environmental challenges |
| Format | Online, public |
| Participants | 974 (Sep 2026) |
| Eligibility | Ages 13–24 as of Aug 21 2026, students only, groups up to 5, all countries |
| Build window | Aug 21 12:00am EDT → **Sep 20 5:00pm EDT** (extended 1 week) |
| Judging | Sep 20 5:00pm → Sep 25 5:00pm EDT |
| Winners announced | Sep 26 9:00am EDT |
| Contact | contact@hackalphax.co, Discord https://discord.gg/hFxwvgZDsh |

## 2. What they're looking for — theme statement

> Our planet is facing unprecedented environmental challenges — climate
> change, pollution, biodiversity loss, resource depletion. The theme **Earth
> Forward** invites participants to use technology to create meaningful
> environmental impact: reducing waste, improving renewable energy,
> conserving water, protecting wildlife, **monitoring ecosystems**, advancing
> sustainable agriculture, and helping communities **adapt to climate
> change**. Collaborate with local orgs/researchers to address real-world
> needs.

Virgo-Eye's natural fit — every one of these maps to the existing 4-stage CoVT
pipeline over **satellite/aerial + drone imagery**:

- monitoring ecosystems → land-cover change detection
- sustainable agriculture → crop health / disease stress
- protecting wildlife → conservation/poaching disturbance surveys
- climate resilience / adaptation → post-disaster damage assessment
- water conservation → water body / discoloration detection

## 3. Required deliverables

1. **Video demonstration / pitch — no longer than 5 minutes.**
2. **Link to repository/code.**
3. **Link to live website/application (if applicable).**
4. Cross-submission to other hackathons is allowed **this month only** (if the
   other hackathon permits).
5. **Continuing an old project?** Must specify in Devpost what was done
   1) before the hackathon and 2) during the hackathon.

> Note: the rules page says "video (3–5 minutes)" while the overview says
> "**no longer than 5 minutes**". Target 3.5–4.5 min to satisfy both.

## 4. Judging criteria (verbatim) — the 6 boxes to hit

| Criterion | What judges ask | VirgoEye answer plan |
| --- | --- | --- |
| **Originality** | "Done before at hackathons? How creative is the solution?" | 4-stage Chain-of-Visual-Thought with a self-critic + calibrated verdict is not a wrapper; it's a novel reasoning architecture. |
| **Adherence to Track** | "Does it adhere to Earth Forward, fully or partially?" | Pivot to environmental-scene diagnosis (satellite/crop/wildlife/disaster) in the live demo, prompts, sample data, Devpost page, and video. |
| **Completion** | "Does the hack work? Everything they wanted?" | Demo mode runs with zero GPU; backend tests green; streaming UI live. Show it end-to-end. |
| **Learning** | "Did they stretch? Learn something new?" | CoVT/critic engineering, quantization, VLM streaming, SSE — document the journey in the write-up. |
| **Design** | "Thought put into UX? How well designed?" | Polished Next.js dashboard: bbox overlays, thought terminal, critic report, animated gauges. |
| **Technology** | "Difficult? Clever? Many components? 'Wow'?" | Multi-stage VLM loop, 4-bit AWQ on consumer VRAM, KV-level caching, single weight residency, SSE streaming, vLLM alternative. This is the differentiator. |

## 5. Sponsors & prize integration

Sponsor logos on the 2026 page: **Claude**, **Wolfram**, **Saily**, **Incogni**,
**XYZ**, **Kinetik**, **AOPS**, **NordPass**, **NordVPN**.

Prizes: 1st $1,000 cash + $500 Claude credits + **Final Round Interview @ a YC
startup** + AOPS coupons + XYZ domains + 1yr NordVPN/NordPass/Saily/Incogni;
2nd $500 + $250 Claude; 3rd $250 + $100 Claude; participation Wolfram/XYZ.

Ideas to weave sponsor tech in (visible = memorable to judges):

- **Claude credits** → use the credits for the follow-up "extra analysis"
  path (e.g., a second-opinion pass) and demo it during the video.
- **Wolfram** → surface a Wolfram-powered "model-card / confidence"
  computation or a Wolfram|Alpha-backed comparison of environmental index
  data. Wolfram Language + LLM usage is a small, low-risk integration.
- **Kinetik (gigs/internship)** → mention your availability/team in the
  description; prize is a final-round interview.
- **NordVPN family** — no integration needed; list as a recognizable sponsor
  always visible in the virtual booth/demo.

## 6. Past winners — what actually wins

### 2025 — "Breaking limits" (885 participants)
Winners (Winner ribbon in gallery): **DyslexicAssist** (reading accessibility),
**Memora** (face-blindness AI training + real-time assistance), **Eyelink**
(accessibility). Theme was accessibility; AI + disability impact + real-time
assistance dominated.

### 2024 — "Code4Good" (399 participants, NordVPN-sponsored)
Winners: **BizVision** (AI computer vision to empower blind-run businesses),
**LocalHarvest** (support local farmers / cut out the middleman). Also strong:
**Green Health Monitor** (AI plant-disease detection from leaf images).

### Patterns across years
- Winners are **AI applied to a real, personal, high-impact problem** — not
  CRUD apps.
- **Computer-vision / accessibility** projects recur and place.
- Strong **live demo + clean UI** is table stakes.
- Winners rarely ship a 4-stage *self-criticizing* reasoning pipeline: most
  submissions are single-pass "upload → one answer". Virgo-Eye's Technology +
  Originality story is a genuine differentiator.

## 7. Game plan — make VirgoEye "surpass all"

**Positioning (one line):** *Virgo-Eye is the reasoning-first environmental
diagnostic engine — a 4-stage Chain-of-Visual-Thought pipeline that maps,
deliberates, criticizes, and delivers a calibrated verdict on Earth-Forward
imagery.*

**Deliverables by deadline (Sep 20 5:00pm EDT):**

- [ ] Domain pivot merged: `agriculture`, `wildlife`, `disaster` domains added
      (schema + prompts + demo engine + frontend). `satellite` stays, now the
      default.
- [ ] Earth-Forward sample data around the 4 demo scripts.
- [ ] Devpost draft: title/tagline/description/tech stack already defined in
      `docs/project-requirements.md` §2.2; update copy to the environmental
      framing.
- [ ] Demo video 3.5–4.5 min, scripted per `docs/project-requirements.md`
      §2.1, lead with an environmental scene (e.g., crop-stress or satellite
      change-detection) then a second domain for breadth.
- [ ] Repo public, CI green (backend 42 tests + frontend typecheck/build).
- [ ] Live link if deployable (demo mode needs no GPU — easily hostable).
- [ ] "Before vs during hackathon" statement written into the Devpost
      (repo history shows set-up before; the environment-domain work, sample
      data, docs, and video are "during").
- [ ] Sponsor-touch integrations: Wolfram note + Claude-credit second opinion
      noted in the project description.
- [ ] Submit before Sep 20 5:00pm EDT.

## 8. Sources

- Devpost overview: https://nextstep2026.devpost.com/
- Dates: https://nextstep2026.devpost.com/details/dates
- Rules: https://nextstep2026.devpost.com/rules
- 2025 gallery: https://nextstep2025.devpost.com/project-gallery
- 2024 gallery: https://nextstep2024.devpost.com/project-gallery
- 2025 winner announcement: https://nextstep2025.devpost.com/updates/33949-and-the-winner-is