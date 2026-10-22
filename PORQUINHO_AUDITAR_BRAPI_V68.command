#!/bin/bash
set -euo pipefail
umask 077
"$HOME/anaconda3/bin/python" -I -B - <<'PY'
import ast,datetime as dt,hashlib,json,os,pathlib,re,sys,zipfile
ROOT=pathlib.Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2')
assert (ROOT/'webapp/server.py').is_file(),'PROJETO_NAO_LOCALIZADO'
sys.path.insert(0,str(ROOT))
original=pathlib.Path.cwd()
report={'schema':'porquinho.brapi-credential-audit/1.0','collected_at':dt.datetime.now(dt.timezone.utc).isoformat(),'modules':[], 'credential_values_exported':False,'credential_store_modified':False}
for rel in ('universal_portfolio/provider_credentials.py','universal_portfolio/provider_connectivity.py','market_data/gateway.py','universal_portfolio/provider_registry.py'):
 p=ROOT/rel;row={'path':rel};report['modules'].append(row)
 if p.is_symlink() or not p.is_file():row['status']='MISSING_OR_SYMLINK';continue
 raw=p.read_bytes()
 if len(raw)>1024*1024:row['status']='SIZE_LIMIT';continue
 row.update(status='READ',sha256=hashlib.sha256(raw).hexdigest())
 try:
  tree=ast.parse(raw)
  row['functions']=[n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
  row['probe_unavailable_literal_present']=any(isinstance(n,ast.Constant) and n.value=='CONNECTIVITY_PROBE_UNAVAILABLE' for n in ast.walk(tree))
 except Exception as exc:row.update(status='PARSE_ERROR',error_type=type(exc).__name__)
report['environment_token_present']=bool(os.getenv('BRAPI_TOKEN','').strip())
# Export only existence/equality booleans; never token text, lengths or hashes.
try:
 from universal_portfolio.provider_credentials import resolve_provider_secret
 secrets={}
 original=pathlib.Path.cwd()
 try:
  for label,cwd,explicit in [('project_explicit_root',ROOT,True),('project_default_root',ROOT,False),('temporary_default_root',pathlib.Path('/tmp'),False)]:
   os.chdir(cwd)
   try:
    options={'env_fallback':'BRAPI_TOKEN'}
    if explicit:options['root']=ROOT
    secret=resolve_provider_secret('brapi',**options)
    secrets[label]=secret if isinstance(secret,str) else ''
    report[label]={'status':'RESOLVED' if secrets[label] else 'NOT_CONFIGURED','present':bool(secrets[label])}
   except Exception as exc:report[label]={'status':'READ_FAILED','error_type':type(exc).__name__}
 finally:os.chdir(original)
 if all(k in secrets for k in ('project_explicit_root','project_default_root')):
  report['project_and_gateway_credentials_match']=bool(secrets['project_explicit_root']) and secrets['project_explicit_root']==secrets['project_default_root']
 if all(k in secrets for k in ('project_default_root','temporary_default_root')):
  report['credential_independent_of_working_directory']=secrets['project_default_root']==secrets['temporary_default_root']
 secrets.clear()
except Exception as exc:report['credential_module_import']={'status':'FAILED','error_type':type(exc).__name__}
# Same transport used by the radar; report sanitized status only.
try:
 os.chdir(ROOT)
 from market_data.gateway import get_json
 try:
  result=get_json('https://brapi.dev/api/quote/ABEV3',token_env='BRAPI_TOKEN',provider_id='brapi',timeout=10)
  rows=result.get('results') if isinstance(result,dict) else None
  report['authenticated_quote']={'status':'RESPONSE_RECEIVED','matching_symbol':isinstance(rows,list) and any(isinstance(r,dict) and r.get('symbol')=='ABEV3' for r in rows)}
 except Exception as exc:
  code=str(exc)
  report['authenticated_quote']={'status':code if re.fullmatch(r'PROVIDER_[A-Z0-9_]+',code) else 'PROBE_FAILED','error_type':type(exc).__name__}
except Exception as exc:report['authenticated_quote']={'status':'PROBE_IMPORT_FAILED','error_type':type(exc).__name__}
finally:os.chdir(original)
out=pathlib.Path.home()/'Downloads'/('PORQUINHO_AUDITORIA_BRAPI_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip')
with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED) as z:z.writestr('auditoria.json',json.dumps(report,ensure_ascii=False,indent=2))
for key in ('environment_token_present','project_explicit_root','project_default_root','temporary_default_root','project_and_gateway_credentials_match','credential_independent_of_working_directory','authenticated_quote'):print(key+': '+str(report.get(key)))
print('SOMENTE_LEITURA; TOKENS_NAO_EXPORTADOS; BRAIN_NAO_ALTERADO')
print('ENVIAR='+str(out))
PY
