"""Bounded development evaluation: six cases, five calls/case, no automatic retries.
Run from the repository root. Images remain in a temporary directory.
The no-critic baseline shares mapping and observations with the full pipeline.
"""
import asyncio,base64,json,sys,time,hashlib
from pathlib import Path
import httpx
from PIL import Image,ImageFilter
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from backend.pipeline.orchestrator import PipelineOrchestrator
from backend.pipeline.image_processor import load_from_base64
from backend.schema.api import AnalyzeRequest
from backend.schema.verdict import FinalVerdict
from backend.agents.base_agent import parse_json
from backend.prompts.synthesis_prompt import build_synthesis_prompt
from backend.pipeline.kv_cache_manager import PROMPT_VERSION

OUT=Path('docs/evaluation/reliability');TMP=Path('/tmp/virgoeye-reliability')
async def prepare():
    TMP.mkdir(exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    cases=[]
    async with httpx.AsyncClient(follow_redirects=True,timeout=30) as client:
        for category,expected in [('Tomato___healthy','absent'),('Tomato___Early_blight','present')]:
            r=await client.get('https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color/'+category)
            r.raise_for_status()
            files=sorted([f for f in r.json() if f['type']=='file'],key=lambda x:x['name'])[:2]
            for i,file in enumerate(files):
                identifier=f'{expected}-{i+1}'
                path=TMP/(identifier+'.jpg')
                image=await client.get(file['download_url']);image.raise_for_status();path.write_bytes(image.content)
                cases.append(dict(id=identifier,path=str(path),source=file['download_url'],expected=expected,
                    sha256=hashlib.sha256(image.content).hexdigest(),expectation_basis='PlantVillage directory label; visible-concern proxy, not a specialist annotation'))
    blurred=TMP/'blurred.jpg'
    Image.open(cases[0]['path']).resize((6,6)).resize((256,256)).filter(ImageFilter.GaussianBlur(16)).save(blurred)
    cases.append(dict(id='blurred',path=str(blurred),source=cases[0]['source'],expected='uncertain',expectation_basis='Deliberately degraded to 6x6 and blurred; should not assert leaf condition'))
    path=Path('backend/tests/sample_images/pcb_fault.png')
    cases.append(dict(id='unrelated',path=str(path),source='Repository-generated PCB illustration',expected='uncertain',expectation_basis='Non-crop input to agriculture inspection'))
    (OUT/'manifest.json').write_text(json.dumps(cases,indent=2))
    return cases

def compact(e): return e.get('type') in ('info','error','stage_result','metrics')
async def main():
    cases=await prepare()
    pipeline=PipelineOrchestrator();await pipeline.initialize()
    if pipeline.demo_mode or pipeline.vllm is None: raise RuntimeError('Live provider required')
    pipeline.cache.enabled=False
    try:
        for case in cases:
            dest=OUT/(case['id']+'.json')
            if dest.exists():
                print(case['id'],'already recorded; skipping to avoid repeat charges',flush=True);continue
            req=AnalyzeRequest(domain='agriculture',image_base64=base64.b64encode(Path(case['path']).read_bytes()).decode())
            t=time.monotonic();events=[]
            async for event in pipeline.analyze(req):
                if compact(event):events.append(event)
                if event['type'] in ('stage_result','error'): print(case['id'],event['stage'],event['type'],flush=True)
            full_seconds=round(time.monotonic()-t,2)
            stages={e['stage']:e['data'] for e in events if e['type']=='stage_result'}
            result={'case':case,'prompt_version':PROMPT_VERSION,'model':pipeline.model_name,'full_seconds':full_seconds,'full_events':events}
            if 'mapping' in stages and 'deliberation' in stages:
                t=time.monotonic();text='';output_tokens=0
                prompt=build_synthesis_prompt(json.dumps(stages['mapping']),stages['deliberation']['thought_chain'],
                    'No critic was run in this experimental branch. Judge only the image, map and observations. Do not claim verification.')
                try:
                    async for chunk in pipeline.vllm.chat_stream(load_from_base64(req.image_base64).base64,prompt,''):
                        text=chunk.get('response',text)
                        if chunk.get('done'):output_tokens=chunk.get('eval_count',0)
                    payload=parse_json(text)
                    if isinstance(payload.get('summary'),str):payload['summary']=payload['summary'][:500]
                    result['no_critic']=FinalVerdict.model_validate(payload).model_dump(mode='json')
                except Exception as e:result['no_critic_error']=str(e)
                result['no_critic_synthesis_seconds']=round(time.monotonic()-t,2)
                result['no_critic_output_tokens']=output_tokens
            dest.write_text(json.dumps(result,indent=2))
            print(case['id'],'saved',flush=True)
    finally:await pipeline.close()
asyncio.run(main())
