#!/bin/bash
set -euo pipefail
umask 077
"$HOME/anaconda3/bin/python" -I -B - <<'PY'
"""Collect existing global experiment evidence. Never run project code or training."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import os
import re
import urllib.request
import zipfile

ROOT=Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2')
MAX_FILE=8*1024*1024
MAX_TOTAL=96*1024*1024
SECTIONS=('global_existing_lab','global_model_evaluation','global_research_lab',
 'global_history_source','learned_allocation_policy','prospective_allocation_policy',
 'learned_policy_account_context','learned_policy_economic_basis',
 'research_economic_components','action_component_validation','action_research_handoff',
 'economic_action_policy','economic_set_producer_diagnostic',
 'scoped_economic_comparison_summary','cash_documentary_cost_summary',
 'official_bank_cost_references','official_exchange_fee_references')
GROUPS=(
 ('data/brain/global_existing_lab_a24/experiments','*/*.json',60),
 ('data/brain/global_research_lab_a24/experiments','*/*.json',60),
 ('data/brain/learned_allocation_policy_a24/versions','*.json',12),
 ('data/brain/prospective_allocation_policy_a24','*/*.json',24),
 ('data/brain/global_history_source_a24/bundles','*/*.json',80),
)
CODE=('brain/evolution/global_existing_lab_a24.py','brain/evolution/global_research_lab_a24.py',
 'brain/evolution/global_model_evaluation_a24.py','brain/evolution/learned_allocation_policy_a24.py',
 'brain/evolution/prospective_allocation_policy_a24.py','brain/evolution/prediction_lab.py',
 'brain/evolution/global_market_frame_a24.py','universal_portfolio/research_economic_components_a24.py',
 'universal_portfolio/forward_risk_estimator_a24.py','universal_portfolio/monitor_consolidation_a24.py',
 'universal_portfolio/universal_runtime_composition.py')
DATA=('results/governed_economic_components_a24.json','data/account_action_policies_a24.json',
 'data/cash_counterfactual_models_a24.json','results/current_crypto_reference_acquisition_a24.json')
SECRET=('password','passwd','secret','token','api_key','apikey','authorization','credential')


def redact(value):
    if isinstance(value,dict):
        return {k:('[REDACTED]' if any(s in str(k).lower() for s in SECRET) else redact(v)) for k,v in value.items()}
    if isinstance(value,list):return [redact(v) for v in value]
    if isinstance(value,str):
        # Source references can contain a URL query; do not export inline tokens.
        return re.sub(r'(?i)([?&](?:token|api_key|apikey|access_token)=)[^&#\s]+',r'\1[REDACTED]',value)
    return value


def encoded(value):
    return json.dumps(redact(value),ensure_ascii=False,indent=2,allow_nan=False).encode()


def read(root,relative):
    root=Path(root);p=root/relative
    if any(a.is_symlink() for a in (p,*p.parents)) or not p.resolve().is_relative_to(root.resolve()):
        raise ValueError('SYMLINK_OR_EXTERNAL_PATH_REFUSED')
    with p.open('rb') as f:
        before=os.fstat(f.fileno());body=f.read(MAX_FILE+1);after=os.fstat(f.fileno())
    if len(body)>MAX_FILE:raise ValueError('FILE_SIZE_LIMIT')
    if (before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_ino,after.st_size,after.st_mtime_ns):
        raise ValueError('FILE_CHANGED_DURING_READ')
    return body


def collect(root,archive,fetch=None):
    root=Path(root)
    manifest={'schema':'porquinho.global-model-audit/1.0','collected_at':dt.datetime.now(dt.timezone.utc).isoformat(),
      'model_or_history_writes':False,'training_requested':False,'market_collection_requested':False,
      'financial_mutation':False,'canonical_validation_granted':False,'files':[],'groups':[]}
    total=0
    def save(name,body):
        nonlocal total
        if total+len(body)>MAX_TOTAL-(0 if name=='manifest.json' else min(1024*1024,MAX_TOTAL//4)):raise ValueError('TOTAL_SIZE_LIMIT')
        archive.writestr(name,body);total+=len(body)
    try:
        if fetch is None:
            request=urllib.request.Request('http://127.0.0.1:8765/api/research/monitor-consolidation',headers={'Cache-Control':'no-cache'})
            # Refuse redirects rather than following a local response to an external URL.
            class NoRedirect(urllib.request.HTTPRedirectHandler):
                def redirect_request(self,*args,**kwargs):return None
            with urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect).open(request,timeout=60) as response:
                raw=response.read(64*1024*1024+1)
            if len(raw)>64*1024*1024:raise ValueError('API_SIZE_LIMIT')
            monitor=json.loads(raw)
        else:monitor=fetch()
        if not isinstance(monitor,dict):raise ValueError('MONITOR_OBJECT_REQUIRED')
        projection={k:monitor[k] for k in SECTIONS if k in monitor}
        projection['observed_at']=monitor.get('observed_at')
        save('api/global_model_context.json',encoded(projection))
        manifest['api_status']='READ_ONLY_LOCAL_RESPONSE_RECEIVED'
    except Exception as exc:
        manifest['api_status']='UNAVAILABLE';manifest['api_error_type']=type(exc).__name__
    def add(relative):
        try:
            raw=read(root,relative)
            if relative.endswith('.json'):
                parsed=json.loads(raw);clean=redact(parsed);body=encoded(parsed)
                changed=clean!=parsed
            else:body=raw;changed=False
            save('project/'+relative,body)
            manifest['files'].append({'path':relative,'status':'COLLECTED',
                'original_sha256':hashlib.sha256(raw).hexdigest(),'content_redacted':changed})
        except Exception as exc:
            manifest['files'].append({'path':relative,'status':'UNAVAILABLE','error_type':type(exc).__name__})
    for relative in CODE+DATA:add(relative)
    for directory,pattern,limit in GROUPS:
        base=root/directory
        if any(a.is_symlink() for a in (base,*base.parents)):
            manifest['groups'].append({'directory':directory,'status':'SYMLINK_REFUSED'});continue
        paths=list(base.glob(pattern)) if base.is_dir() else []
        # This is a bounded archive sample, not a claim that selected versions are current.
        safe=[p for p in paths if not any(a.is_symlink() for a in (p,*p.parents)) and p.is_file()]
        safe.sort(key=lambda p:(p.stat().st_mtime_ns,str(p)),reverse=True)
        chosen=safe[:limit]
        manifest['groups'].append({'directory':directory,'discovered':len(paths),
          'selected':len(chosen),'truncated':len(safe)>limit,'selection':'MOST_RECENT_FILE_MTIME_NOT_MODEL_PROMOTION'})
        for p in chosen:add(p.relative_to(root).as_posix())
    manifest['payload_bytes']=total
    save('manifest.json',encoded(manifest))
    return manifest


def main():
    if not (ROOT/'porquinho.py').is_file():raise SystemExit('PROJETO_NAO_ENCONTRADO')
    downloads=Path.home()/'Downloads';downloads.mkdir(exist_ok=True)
    target=downloads/('PORQUINHO_MODELOS_GLOBAIS_V114_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip')
    fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,'wb') as stream:
            with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as archive:
                manifest=collect(ROOT,archive)
        with zipfile.ZipFile(target) as archive:
            if archive.testzip() is not None:raise ValueError('ARCHIVE_INTEGRITY_FAILED')
    except Exception:
        target.unlink(missing_ok=True);raise
    print('API='+manifest['api_status'])
    print('ARQUIVOS_COLETADOS='+str(sum(f['status']=='COLLECTED' for f in manifest['files'])))
    print('SOMENTE_LEITURA; SEM_TREINAMENTO; SEM_COLETA_DE_MERCADO; DADOS_E_MODELOS_NAO_ALTERADOS')
    print('ENVIAR='+str(target))


if __name__=='__main__':main()

PY
