import json, urllib.request
from pathlib import Path
BASE='https://raw.githubusercontent.com/dmaillot95-ui/cerebron-omega-encyclopedia/main/'
def _get(url,timeout=20):
    with urllib.request.urlopen(url,timeout=timeout) as r: return r.read().decode('utf-8')
def load_context(categories):
    meta={'loaded':False,'registry_version':None,'categories':[],'errors':[]}; chunks=[]
    try:
        local=json.loads(Path('CEREBRON_REGISTRY.json').read_text(encoding='utf-8'))
        manifest=json.loads(_get(local['registry'])); meta['registry_version']=manifest.get('version'); paths=manifest.get('paths',{})
        for cat in categories:
            rel=paths.get(cat)
            if not rel: meta['errors'].append(f'NO_PATH:{cat}'); continue
            try:
                text=_get(BASE+rel); chunks.append(f'### {cat.upper()}\n{text[:12000]}'); meta['categories'].append(cat)
            except Exception as e: meta['errors'].append(f'{cat}:{e!r}')
        meta['loaded']=bool(chunks)
    except Exception as e: meta['errors'].append(f'MANIFEST:{e!r}')
    return '\n\n'.join(chunks),meta
