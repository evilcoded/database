#!/bin/bash
set -euo pipefail
umask 077
"$HOME/anaconda3/bin/python" -I -B - <<'PYTHON'
import datetime,hashlib,json,os,pathlib,urllib.request,zipfile
ROOT=pathlib.Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2')
now=datetime.datetime.now(datetime.timezone.utc)
report={'schema':'porquinho.cost-package-context/1.0','collected_at':now.isoformat(),'financial_mutation':False,'models_modified':False,'sources':{},'issues':[]}
attachments={}
def encode(value):return json.dumps(value,ensure_ascii=False,indent=2).encode()
try:
 request=urllib.request.Request('http://127.0.0.1:8765/api/research/monitor-consolidation',headers={'Accept':'application/json'})
 with urllib.request.urlopen(request,timeout=60) as response:
  raw=response.read(40*1024*1024+1)
 if len(raw)>40*1024*1024:raise ValueError('RESPONSE_SIZE_LIMIT')
 data=json.loads(raw)
 if not isinstance(data,dict):raise ValueError('RESPONSE_OBJECT_REQUIRED')
 # Keep only the existing cost/research projections; no account credentials or full status.
 keys=('cash_plan_visibility','cash_plan_assessment','cash_documentary_cost_summary','action_cost_visibility','official_bank_cost_references','official_exchange_fee_references','action_research_handoff','action_component_validation')
 attachments['contexto_custos.json']=encode({k:data.get(k) for k in keys})
 visibility=data.get('action_cost_visibility') or {};rows=visibility.get('rows') or []
 findings=[]
 for context in (data.get('cash_plan_visibility') or {}).get('contexts',[]):
  for scenario in (context.get('learned_scenario_transport') or {}).get('scenarios',[]):
   finding={'account_id':context.get('account_id'),'currency':context.get('currency'),'candidate_id':scenario.get('candidate_id'),'projection_status':(scenario.get('documentary_cost_projection') or {}).get('status'),'manual_route_status':(scenario.get('manual_route_availability') or {}).get('status'),'legs':[]}
   for leg in scenario.get('legs',[]):
    matches=[r for r in rows if (r.get('account_id'),r.get('currency'),r.get('instrument_id'),r.get('side'))==(context.get('account_id'),context.get('currency'),leg.get('instrument_id'),'BUY')]
    finding['legs'].append({'instrument_id':leg.get('instrument_id'),'provider':leg.get('provider'),'provider_id':leg.get('provider_id'),'currency':leg.get('quote_currency'),'matched_reference_rows':len(matches),'rows_with_bank_component':sum(bool(r.get('bank_components')) for r in matches),'rows_with_exchange_hypotheses':sum(bool(r.get('exchange_hypotheses')) for r in matches),'reference_statuses':sorted(set(str(r.get('status')) for r in matches))})
   findings.append(finding)
 report['scenario_findings']=findings
 print('CENARIOS:',len(findings))
 for f in findings:
  print('CENARIO:',f['candidate_id'],'|',f['currency'],'|',f['projection_status'])
  for l in f['legs']:print(' ',l['instrument_id'],'| banco:',l['rows_with_bank_component'],'| bolsa:',l['rows_with_exchange_hypotheses'],'| vinculos:',l['matched_reference_rows'])
except Exception as exc:report['issues'].append({'stage':'local_monitor','error_type':type(exc).__name__})
# Explicit source allowlist: never collect env files, Keychain, models or portfolios.
files=('universal_portfolio/cash_documentary_cost_projection_a24.py','universal_portfolio/action_cost_visibility_a24.py','universal_portfolio/exchange_fee_reference_a24.py','universal_portfolio/official_bank_cost_reference_a24.py','universal_portfolio/account_cost_evidence_a24.py','universal_portfolio/cash_execution_cost_projection_a24.py','universal_portfolio/cash_counterfactual_comparison_a24.py','universal_portfolio/cash_plan_assessment_a24.py','universal_portfolio/learned_cash_plan_transport_a24.py','universal_portfolio/monitor_consolidation_a24.py','universal_portfolio/universal_observation_bridge.py','config/official_exchange_fee_policies_a24.json','config/official_bank_component_policies_a24.json')
for name in files:
 try:
  p=ROOT/name
  if any(x.is_symlink() for x in (p,*p.parents)):raise ValueError('SYMLINK_REFUSED')
  if p.stat().st_size>2*1024*1024:raise ValueError('SOURCE_SIZE_LIMIT')
  body=p.read_bytes();report['sources'][name]={'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body)};attachments['fontes/'+name]=body
 except Exception as exc:report['sources'][name]={'error_type':type(exc).__name__}
attachments['relatorio.json']=encode(report)
out=pathlib.Path.home()/'Downloads'/('PORQUINHO_PACOTE_CUSTOS_V99_'+now.strftime('%Y%m%d_%H%M%S')+'_'+os.urandom(3).hex()+'.zip')
out.parent.mkdir(parents=True,exist_ok=True)
with out.open('xb') as stream:
 os.chmod(out,0o600)
 with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as archive:
  for name,body in attachments.items():archive.writestr(name,body)
print('SOMENTE_LEITURA; SEM_REINICIO; DADOS_E_MODELOS_NAO_ALTERADOS')
print('ENVIAR='+str(out))
if report['issues']:print('COLETA_PARCIAL:',json.dumps(report['issues']))
PYTHON
