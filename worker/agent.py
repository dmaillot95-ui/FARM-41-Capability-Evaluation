import hashlib, json, os, pathlib, subprocess

PREFERRED=['/generate','/chat','/predict','/respond','/infer','/run']

def run(cmd, timeout=240):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

def payload_for(spec, prompt):
    p={}; set_prompt=False
    for x in spec.get('parameters',[]):
        n=x.get('name',''); l=n.lower(); req=bool(x.get('required',False)); default=x.get('default'); typ=(x.get('type') or {}).get('type')
        if l in {'message','prompt','text','query','input','instruction','user_message'}:
            p[n]=prompt; set_prompt=True
        elif l in {'chat_history','history','messages'}: p[n]=[]
        elif l in {'max_new_tokens','max_tokens','maximum_new_tokens'}: p[n]=600
        elif l=='temperature': p[n]=0.1
        elif l=='top_p': p[n]=0.9
        elif l=='top_k': p[n]=40
        elif l in {'system','system_prompt'}: p[n]='CLAIM<=EVIDENCE. PERFORMANCE ON ONE TASK!=GENERAL CAPABILITY. UNKNOWN REMAINS UNKNOWN. SIMULATION!=TEST.'
        elif req and default is None:
            if typ=='string' and not set_prompt:
                p[n]=prompt; set_prompt=True
            else:
                return None
    return p if set_prompt else None

def extract(raw):
    raw=raw.strip()
    try:
        o=json.loads(raw)
        if isinstance(o,dict):
            for k in ('Response','response','text','output','message'):
                if isinstance(o.get(k),str): return o[k].strip()
    except Exception:
        pass
    return raw

def invoke(space,prompt):
    info=run(['hf-gradio','info',space],120)
    if info.returncode!=0:
        return False,'',{'error':info.stderr[-4000:]}
    api=json.loads(info.stdout)
    eps=list(api.items())
    eps.sort(key=lambda kv:(PREFERRED.index(kv[0]) if kv[0] in PREFERRED else 99,kv[0]))
    errors=[]
    for ep,spec in eps:
        payload=payload_for(spec,prompt)
        if payload is None: continue
        pred=run(['hf-gradio','predict',space,ep,json.dumps(payload,ensure_ascii=False)],240)
        if pred.returncode==0 and pred.stdout.strip():
            text=extract(pred.stdout)
            if text:
                return True,text,{'endpoint':ep,'sha256':hashlib.sha256(text.encode()).hexdigest()}
        errors.append((ep,(pred.stderr or pred.stdout)[-2000:]))
    return False,'',{'errors':errors}

role=os.environ['ROLE']
space=os.environ['MODEL']
out=pathlib.Path('out'); out.mkdir(exist_ok=True)
prompt=f'''You are {role} in CEREBRON Ω FARM 41 CAPABILITY EVALUATION.
Evaluate capability claims rigorously. Separate demonstrated task performance from general capability, transfer, robustness, reproducibility, calibration, limitations and unknowns. Do not certify a capability without evidence. Do not infer capability from confidence, style or self-report. Record: target capability, evidence required, observed evidence, failure evidence, transfer boundary, robustness status, reproducibility status, calibration issues, unknowns, decisive next test, conclusion status. CLAIM<=EVIDENCE. SIMULATION!=TEST. UNKNOWN REMAINS UNKNOWN.'''

ok,text,meta=invoke(space,prompt)
status='UNREVIEWED_EXTERNAL_AGENT_OUTPUT' if ok else 'EXTERNAL_INFERENCE_FAILED'
packet={'role':role,'model':space,'inference_success':ok,'status':status,'output':text if ok else '', 'meta':meta}
(out/f'{role}.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'role':role,'inference_success':ok,'status':status,'meta':meta},ensure_ascii=False))
