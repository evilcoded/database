#!/bin/bash
set -euo pipefail
"$HOME/anaconda3/bin/python" -I -B - <<'PY'
import datetime, hashlib, json, pathlib, zipfile
root=pathlib.Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2')
if not (root/'webapp/server.py').is_file():
    raise SystemExit('PROJETO_NAO_LOCALIZADO: '+str(root))
paths=['data/universal_instrument_catalog.json','data/instruments/manual_instruments.json','data/instruments/market_provider_bindings_a24.json','static/data/asset_registry_v365.json']
fields={'instrument_id','symbol','name','asset_class','currency','quote_currency','market','jurisdiction','provider','provider_id','provider_binding_attested','source','identity_provenance','identity_source_ref','confirmed_at','effective_from','metadata','bindings','instruments','assets','items','schema'}
def project(x):
    if isinstance(x,list):return [project(v) for v in x]
    if isinstance(x,dict):
        # Preserve keyed catalog structure, but only approved fields within records.
        if not any(k in x for k in fields):return {k:project(v) for k,v in x.items() if isinstance(v,(dict,list))}
        return {k:project(v) for k,v in x.items() if k in fields}
    return x
report={'schema':'porquinho.binding-source-inspection/1.0','collected_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':[]}
for rel in paths:
    p=root/rel; row={'path':rel}; report['files'].append(row)
    if p.is_symlink() or root.resolve() not in p.resolve().parents:row['status']='SYMLINK_OR_OUTSIDE_PROJECT';continue
    if not p.exists():row['status']='MISSING';continue
    try:
        if p.stat().st_size>16*1024*1024:row['status']='SIZE_LIMIT';continue
        raw=p.read_bytes(); data=json.loads(raw)
        row.update(status='READ',sha256=hashlib.sha256(raw).hexdigest(),catalog=project(data))
    except Exception as exc:row.update(status='READ_ERROR',error=type(exc).__name__)
out=pathlib.Path.home()/'Downloads'/('PORQUINHO_VINCULOS_BRL_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip')
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr('vinculos.json',json.dumps(report,ensure_ascii=False,indent=2))
for row in report['files']:print(row['status'],row['path'])
print('SOMENTE_LEITURA; PROJETO_E_BRAIN_NAO_ALTERADOS')
print('ENVIAR='+str(out))
PY
