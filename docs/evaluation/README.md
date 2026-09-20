# Live Claude smoke evaluation — 20 September 2026

These are two development sanity checks, not an accuracy benchmark, held-out test, or evidence of field effectiveness. Neither image filename nor dataset label was sent to the model; only the image and agriculture domain were supplied. Source URLs, complete stage results and measured timings are preserved in the adjacent JSON files. Images were downloaded to a temporary evaluation folder, not redistributed in the app.

Source: [PlantVillage, Mohanty, Hughes and Salathé](https://github.com/spMohanty/PlantVillage-Dataset). Selected the first file returned by GitHub in each of Tomato___healthy and Tomato___Early_blight. These are controlled leaf photographs, not representative field deployment conditions. No specialist ground-truth review of generated boxes was performed.

Before running, expected behavior was defined as: describe visible leaf condition, avoid unsupported causal diagnosis/treatment, and provide appropriate next inspection steps. A healthy-labelled image should not generate a confident disease claim; a visibly affected image should not receive a blanket all-clear.

| Input | Measured time | Output | Assessment |
| --- | --- | --- | --- |
| Healthy-labelled tomato leaf | 44.2 s | WARNING; normal overall color/venation, ambiguous margin marks and specks; no clear lesions or diagnostic disease pattern | Avoided a disease diagnosis, but potentially over-alerted on a healthy sample. Needs a larger false-positive evaluation. |
| Early-blight-labelled tomato leaf | 42.8 s | WARNING; visible dark spots/blotches and pale mottling, multiple possible causes | Identified visible concerns and avoided claiming a confirmed cause. |

Both completed all four stages. Both passed the automated critic; this does not constitute independent expert verification. No comparison against a single-pass baseline was run, so improved accuracy from the critic is not established. Live token totals use provider-reported output usage. These timings replace assumptions about a 5–8 second pipeline on this configuration.

An earlier live browser test of the repository's synthetic illustration correctly identified that the image was illustrative. That run exposed a summary-length validation failure in stage four. The summary display field is now bounded to 500 characters while preserving the complete primary finding and evidence. The two real-photo tests above ran after that fix.

Next evaluation: multiple healthy, visibly affected, ambiguous, and irrelevant images; reviewer-labelled visible findings; false-positive/false-negative tally; same images with and without critic; separate timing and cost measurement. Do not claim sensitivity, specificity, crop yield gains, or a winning probability from this smoke test.

Final browser verification: the affected image also completed through the production dashboard in 44.1 seconds using `claude-sonnet-5` (the configured model). Its standalone HTML report downloaded successfully with an embedded image, evidence, limitations, provider/model metadata, and next field checks. This repeated smoke check is not an additional independent evaluation sample. Final validation: 53 backend tests, report export test, and production frontend build.
