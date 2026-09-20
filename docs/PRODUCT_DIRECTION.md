# VirgoEye: competition readiness and product direction

Decision date: 20 September 2026. This is an assessment and proposed implementation scope, not a claim that the features below already exist.

## Product decision

Focus the primary experience on crop inspection support: help a field officer identify visible areas that warrant inspection, explain the evidence and uncertainty, and record the next action. Keep the reusable analysis engine, but stop presenting seven unrelated domains as the main product.

Suggested positioning: “VirgoEye helps crop inspectors turn field images into evidence-backed inspection priorities.”

Do not infer disease identity, treatment, yield loss, acreage, water savings, or environmental impact from a photograph alone. Those require additional evidence. A visibly affected area and a suggested field check are narrower, testable outputs.

## Assessment against the published NextStep criteria

| Criterion | Current evidence | Required improvement |
| --- | --- | --- |
| Originality | Four-stage image analysis is a recognizable AI workflow; no demonstrated unique outcome yet | Show why evidence-linked inspection and explicit uncertainty are more useful than a generic image chatbot |
| Theme adherence | Environmental domain options and sample illustrations exist | Make one environmental user, task, and decision central to the entire experience |
| Completion | Upload-to-result fallback works; 45 backend tests pass | Demonstrate real inference and deliberate handling of failure, ambiguity, and rejected findings |
| Learning | Architecture and commit history show engineering work | Team must explain actual learning and individual contributions; do not invent this narrative |
| Design | Dashboard provides an end-to-end visual flow | Prioritize findings, evidence, and next action over token speed and lengthy generated reasoning |
| Technology | Streaming, schemas, cache, model adapters and critic exist | Add real provider integration and compare critic-assisted output with a baseline on the same labelled examples |

These are qualitative judgments, not official scores or estimates of winning probability. The competitor field has not been evaluated.

## Implementation scope

1. Add Anthropic vision support on the server, with explicit provider/model status, timeouts, bounded output and request limits, and provider-reported usage. Keep secrets out of browser code. Label remote inference and image transmission in the upload experience. Fail visibly on provider errors; simulation must remain an explicit mode.
2. Change the user-facing analysis into concise observable evidence, alternative explanations, uncertainty, and the recommended field check. Do not market generated reasoning as access to the model's private thoughts.
3. Present image regions as approximate visual references. Vision models are not precise object detectors; support review/correction or user-supplied regions where accuracy matters.
4. Introduce a needs-review outcome. Critic rejection or critical unresolved contradictions must prevent a confident all-clear. Validate evidence references against mapped entities.
5. Replace synthetic throughput and unsupported confidence/accuracy/VRAM claims with truthful status and measured results.
6. Add a simple exportable inspection report containing the image reference, observations, uncertain claims, next actions, model/provider, timestamp, and review status.

## Evidence gate before recording

- Use a small documented set of real, appropriately licensed crop photographs, including healthy-looking, visibly affected, ambiguous, and irrelevant inputs. Record source and reviewer-labelled expectations. Generated illustrations are interface fixtures only.
- Define evaluation questions before running: did the app identify the visible issue, ground it in an appropriate region, avoid unsupported diagnosis, and recommend a proportionate next check?
- Compare a single model pass with the critic-assisted pipeline. Record disagreements and failures as well as successes. A small development set supports a demo, not a general accuracy claim.
- Measure actual end-to-end latency and provider usage. Report cache hits separately. Do not claim the critic improves accuracy until the comparison supports it.
- Complete the browser workflow with live inference, including uncertainty and service failure. Export the result and verify its contents.
- Show at least one normal and one affected case in the eventual video; identify any prerecorded output and disclose limitations.

## Submission requirements still needing confirmation

Sources: https://nextstep2026.devpost.com/ and https://nextstep2026.devpost.com/rules

Registration, student eligibility, age 13–24 on 21 August 2026, team of at most five, and accurate before/during-event contribution disclosure are not verified by code review. Prepare a completed Devpost page, accessible code, an applicable live link, and a 3–5 minute video. Published deadline is 20 September 2026 at 5 p.m. EDT (10 p.m. Lagos). Product improvements cannot waive an organizer's deadline or eligibility rules.

## Anthropic credentials

Put `ANTHROPIC_API_KEY` in the repository's ignored local `.env` file, not chat or any `NEXT_PUBLIC_` variable. The provider adapter and environment loading still need implementation. Use only intended test images for remote requests. A user-specified testing budget is needed before an open-ended evaluation run.

## Implementation update

The crop-focused landing page, workspace, server-side Anthropic adapter (including workspace-scoped headers), deterministic review policy, honest simulation metrics, and standalone printable HTML report are now implemented. The provider credential is loaded only on the server. Initial live testing identified an overlong model summary; display summaries are now bounded without changing the full finding or evidence. Live dataset sanity checks are being recorded separately; they do not establish general accuracy or competitive ranking.
