#!/bin/bash
set -euo pipefail
umask 077
"$HOME/anaconda3/bin/python" -I -B - <<'PY'
from pathlib import Path
import datetime as dt,hashlib,json,tempfile,urllib.request,zipfile,os
ROOT=Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2')
MAX=16*1024*1024
ENDPOINTS=(('monitor','/api/research/monitor-consolidation'),('funding','/api/research/funding-contexts'),('portfolio','/api/portfolio/live-projection'),('status','/api/status'))
DATA=(
 'data/institution_accounts.json','data/planning_budgets.json','data/investment_plans.json',
 'data/account_action_policies_a24.json','data/cash_counterfactual_models_a24.json',
 'data/instruments/market_provider_bindings_a24.json','data/instruments/research_identity_links_a24.json',
 'results/governed_economic_components_a24.json','results/current_crypto_reference_acquisition_a24.json',
 'config/official_execution_route_policies_a24.json',
)
SOURCES=(
 'porquinho.py','webapp/server.py','universal_portfolio/universal_observation_bridge.py',
 'universal_portfolio/funded_currency_research_a24.py','universal_portfolio/economic_action_plan_a24.py',
 'universal_portfolio/economic_action_policy_a24.py','universal_portfolio/economic_action_evidence_a24.py',
 'universal_portfolio/action_research_handoff_a24.py','universal_portfolio/action_component_validation_a24.py',
 'universal_portfolio/economic_component_set_producer_a24.py','universal_portfolio/research_economic_components_a24.py',
 'universal_portfolio/learned_policy_account_context_a24.py','universal_portfolio/learned_cash_plan_transport_a24.py',
 'universal_portfolio/cash_plan_assessment_a24.py','universal_portfolio/cash_plan_visibility_a24.py',
 'universal_portfolio/route_documentary_cost_a24.py','universal_portfolio/cash_counterfactual_comparison_a24.py',
 'universal_portfolio/monitor_consolidation_a24.py','universal_portfolio/research_quote_acquisition_a24.py',
)
SECRET_PARTS=('password','passwd','secret','token','api_key','apikey','authorization','credential')
def sanitized(value):
 if isinstance(value,dict):
  return {k:('[REDACTED]' if any(part in str(k).lower() for part in SECRET_PARTS) else sanitized(v)) for k,v in value.items()}
 if isinstance(value,list):return [sanitized(v) for v in value]
 return value

def json_bytes(value):return json.dumps(sanitized(value),ensure_ascii=False,indent=2,allow_nan=False).encode('utf-8')

def snapshot_only(value):
 snap=value.get('snapshot') or {};portfolio=value.get('portfolio') or {}
 training=snap.get('training') or {}
 return {'snapshot':{k:snap.get(k) for k in ('timestamp','portfolio_currency_scope','cash_reconciliation','capital_eur','portfolio_cost_eur','portfolio_value_eur','pnl_eur','cash_eur','total_wealth_eur')},
         'training_status':{k:training.get(k) for k in ('trained','status','calibration_usable','model_ref','model_version')},
         'scores':portfolio.get('scores',snap.get('scores',[]))}

def safe_source(rel):
 p=ROOT/rel
 if p.is_symlink() or any(a.is_symlink() for a in p.parents if a!=ROOT.parent):raise ValueError('SYMLINK_REFUSED')
 if not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError('OUTSIDE_PROJECT')
 if not p.is_file():raise FileNotFoundError()
 before=p.stat()
 if before.st_size>MAX:raise ValueError('FILE_SIZE_LIMIT')
 body=p.read_bytes();after=p.stat()
 if (before.st_size,before.st_mtime_ns,before.st_ino)!=(after.st_size,after.st_mtime_ns,after.st_ino):raise ValueError('CHANGED_DURING_READ')
 return body

def run():
 if not (ROOT/'webapp/server.py').is_file():raise SystemExit('PROJETO_NAO_ENCONTRADO')
 downloads=Path.home()/'Downloads';downloads.mkdir(exist_ok=True)
 stamp=dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f');out=downloads/('PORQUINHO_RECOMENDACOES_GLOBAIS_V110_'+stamp+'.zip')
 manifest={'schema':'porquinho.recommendation-audit/1.0','collected_at':dt.datetime.now(dt.timezone.utc).isoformat(),'read_only':True,'cycle_requested':False,'market_collection_requested':False,'financial_mutation':False,'model_or_training_writes':False,'items':[]}
 with tempfile.TemporaryDirectory(prefix='.porquinho-recommendation-audit-',dir=downloads) as tmp:
  work=Path(tmp)
  def save(name,body):
   p=work/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body)
   manifest['items'].append({'name':name,'status':'COLLECTED','bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
  for name,endpoint in ENDPOINTS:
   print('LENDO_API='+endpoint,flush=True)
   try:
    request=urllib.request.Request('http://127.0.0.1:8765'+endpoint,headers={'Cache-Control':'no-cache'})
    with urllib.request.urlopen(request,timeout=45) as response:raw=response.read(MAX+1)
    if len(raw)>MAX:raise ValueError('API_SIZE_LIMIT')
    obj=json.loads(raw)
    save('api/'+name+'.json',json_bytes(snapshot_only(obj) if name=='status' else obj))
   except Exception as exc:manifest['items'].append({'name':'api/'+name+'.json','status':'UNAVAILABLE','error_type':type(exc).__name__})
  for rel in DATA+SOURCES:
   try:
    body=safe_source(rel)
    if rel in DATA:body=json_bytes(json.loads(body))
    save('project/'+rel,body)
   except FileNotFoundError:manifest['items'].append({'name':'project/'+rel,'status':'MISSING'})
   except Exception as exc:manifest['items'].append({'name':'project/'+rel,'status':'UNAVAILABLE','error_type':type(exc).__name__})
  (work/'manifest.json').write_bytes(json_bytes(manifest))
  with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED) as archive:
   for path in sorted(work.rglob('*')):
    if path.is_file():archive.write(path,path.relative_to(work).as_posix())
  os.chmod(out,0o600)
  with zipfile.ZipFile(out) as archive:
   if archive.testzip() is not None:raise RuntimeError('ZIP_INTEGRITY_FAILED')
 print('SOMENTE_LEITURA; SEM_REINICIO; SEM_CICLO; SEM_ALTERACAO_DE_DADOS_OU_MODELOS')
 print('ENVIAR='+str(out))
run()
PY
