# Reliability development evaluation — 20 September 2026

This is a six-case development check, not a validated accuracy benchmark. No clinician/agronomist independently annotated these outputs. Source directory labels are used as a visible-concern proxy. Samples are controlled PlantVillage photographs, one degraded derivative and one repository-generated non-crop illustration. They do not represent deployment conditions.

## Method

Four photographs were selected before inference: the first two sorted filenames from each of PlantVillage Tomato___healthy and Tomato___Early_blight. The blur fixture was reduced to 6×6, enlarged and blurred. The unrelated fixture is a PCB illustration submitted under agriculture. Labels and filenames were not passed to Claude. The manifest records sources and transformations; photographs are not redistributed here.

Both branches share the same model-generated map and evidence summary. The full branch adds a critic and final synthesis; the comparison branch synthesizes the same upstream evidence without critic feedback. This isolates reviewer context more closely than comparing against an unrelated prompt, but single runs remain subject to model variation. It is a three-stage no-critic ablation, not a single-call chatbot benchmark. All runs used the configured model recorded in the result JSON and prompt version 2.2.0, without stage caching or automatic retries.

## Observed outcomes

| Case | Expected | With critic | No critic | Review status | Full seconds | Derived no-critic seconds |
| --- | --- | --- | --- | --- | ---: | ---: |
| absent-1 | absent | uncertain | uncertain | needs_review | 32.39 | 26.7 |
| absent-2 | absent | absent | absent | reviewed | 31.51 | 23.9 |
| blurred | uncertain | uncertain | uncertain | needs_review | 24.08 | 20.6 |
| present-1 | present | present | present | reviewed | 33.85 | 25.7 |
| present-2 | present | present | present | reviewed | 32.86 | 24.4 |
| unrelated | uncertain | error | error | error | 9.35 | 0.0 |

No-critic time is derived from the shared map/observation stage times plus its separate synthesis call; it is not a separately measured end-to-end request.

An uncertain result on a healthy-labelled photograph counts as abstention, not a correct clean assessment. A new-photo/review request is preferable to claiming crop damage, but still creates user friction.

## Interpretation

Branches agreed on visible-concern category in 5/5 completed paired cases; 1 case(s) had a failed branch. Agreement does not establish correctness. This set does not establish that the critic improves accuracy; avoid any such product or pitch claim.

## Case findings

### absent-1

With critic: Single detached leaf on plain background shows normal ovate shape and typical marginal lobing; one low-confidence faint surface mark noted but not distinguishable from shadow or texture.

Without critic: Single detached leaf on plain background shows normal ovate shape and shallow marginal lobing; a low-confidence faint surface streak (E4) is not clearly a lesion and may be shadow or artifact.

### absent-2

With critic: Single detached leaf photographed against a plain gray background shows symmetrical, natural lobing and intact margins; no lesions, discoloration, or pest damage observed.

Without critic: Single detached leaf photographed against a plain gray background; margin lobing appears consistent with natural leaf morphology, no clear lesions, discoloration, or pest damage visible.

### blurred

With critic: A clearer, relevant photograph is needed for inspection.

Without critic: Image is severely blurred/out-of-focus, showing only a diffuse green patch on a gray background; no plant structures, lesions, or texture are resolvable, making inspection inconclusive.

### present-1

With critic: Single leaf image shows dark irregular spots near tip/margin and central-lower area, plus a lighter yellow-green patch; cause cannot be determined from appearance alone.

Without critic: Single leaf image shows dark irregular spots near tip/margin, scattered smaller dark spots near veins, and a yellow-green chlorotic patch on left side; cause cannot be determined from image alone.

### present-2

With critic: Detached leaf shows a diffuse grayish-white surface patch and scattered dark speckling; features differ from surrounding tissue but composition/cause cannot be determined from this single image.

Without critic: Detached leaf shows a diffuse grayish-white surface patch and scattered dark speckled lesions; composition and cause cannot be determined from a single image.

### unrelated

With critic: No final finding

Without critic: No baseline finding

## Follow-up

Obtain an independent field-reviewer-labelled set with more healthy examples and ambiguous conditions. Measure unnecessary alerts, abstentions, missed visible concerns and reviewer usefulness separately. Compare repeated runs and a genuine single-call baseline before deciding whether automated critique justifies its latency and cost. This evaluation does not support yield, diagnostic sensitivity, or environmental impact claims.

See [post-fix regression results](REGRESSIONS.md).
