"""Summarize outcomes without presenting a small development set as accuracy."""
import json,statistics
from pathlib import Path
folder=Path('docs/evaluation/reliability')
rows=[]
for p in sorted(folder.glob('*.json')):
    if p.name=='manifest.json':continue
    r=json.loads(p.read_text());stages={e['stage']:e['data'] for e in r['full_events'] if e['type']=='stage_result'}
    f=stages.get('synthesis',{});b=r.get('no_critic',{});expected=r['case']['expected']
    metrics=next((e['data'] for e in r['full_events'] if e['type']=='metrics'),{})
    times=metrics.get('stage_latencies',{})
    approx_baseline=(times.get('mapping',0)+times.get('deliberation',0))/1000+r.get('no_critic_synthesis_seconds',0)
    rows.append(dict(case=r['case']['id'],expected=expected,full=f.get('visible_concern','error'),baseline=b.get('visible_concern','error'),
                     review=f.get('review_status','error'),suitability=f.get('image_suitability','error'),seconds=r['full_seconds'],baseline_seconds=round(approx_baseline,1),
                     finding=f.get('primary_finding','No final finding'),baseline_finding=b.get('primary_finding','No baseline finding')))
lines=['# Reliability development evaluation — 20 September 2026','',
'This is a six-case development check, not a validated accuracy benchmark. No clinician/agronomist independently annotated these outputs. Source directory labels are used as a visible-concern proxy. Samples are controlled PlantVillage photographs, one degraded derivative and one repository-generated non-crop illustration. They do not represent deployment conditions.','',
'## Method','',
'Four photographs were selected before inference: the first two sorted filenames from each of PlantVillage Tomato___healthy and Tomato___Early_blight. The blur fixture was reduced to 6×6, enlarged and blurred. The unrelated fixture is a PCB illustration submitted under agriculture. Labels and filenames were not passed to Claude. The manifest records sources and transformations; photographs are not redistributed here.','',
'Both branches share the same model-generated map and evidence summary. The full branch adds a critic and final synthesis; the comparison branch synthesizes the same upstream evidence without critic feedback. This isolates reviewer context more closely than comparing against an unrelated prompt, but single runs remain subject to model variation. It is a three-stage no-critic ablation, not a single-call chatbot benchmark. All runs used the configured model recorded in the result JSON and prompt version 2.2.0, without stage caching or automatic retries.','',
'## Observed outcomes','',
'| Case | Expected | With critic | No critic | Review status | Full seconds | Derived no-critic seconds |','| --- | --- | --- | --- | --- | ---: | ---: |']
for r in rows:lines.append(f"| {r['case']} | {r['expected']} | {r['full']} | {r['baseline']} | {r['review']} | {r['seconds']} | {r['baseline_seconds']} |")
lines+=['','No-critic time is derived from the shared map/observation stage times plus its separate synthesis call; it is not a separately measured end-to-end request.','',
'An uncertain result on a healthy-labelled photograph counts as abstention, not a correct clean assessment. A new-photo/review request is preferable to claiming crop damage, but still creates user friction.','',
'## Interpretation','',f"Branches agreed on visible-concern category in {sum(r['full']==r['baseline'] and r['full']!='error' for r in rows)}/{sum(r['full']!='error' and r['baseline']!='error' for r in rows)} completed paired cases; {sum(r['full']=='error' or r['baseline']=='error' for r in rows)} case(s) had a failed branch. Agreement does not establish correctness. This set does not establish that the critic improves accuracy; avoid any such product or pitch claim.",'',
'## Case findings','']
for r in rows:lines += [f"### {r['case']}",'',f"With critic: {r['finding']}",'',f"Without critic: {r['baseline_finding']}",'']
lines+=['## Follow-up','',
'Obtain an independent field-reviewer-labelled set with more healthy examples and ambiguous conditions. Measure unnecessary alerts, abstentions, missed visible concerns and reviewer usefulness separately. Compare repeated runs and a genuine single-call baseline before deciding whether automated critique justifies its latency and cost. This evaluation does not support yield, diagnostic sensitivity, or environmental impact claims.']
lines += ['', 'See [post-fix regression results](REGRESSIONS.md).']
(folder/'RESULTS.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(rows,indent=2))
