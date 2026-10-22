#!/bin/bash
set -euo pipefail
"$HOME/anaconda3/bin/python" -I -B - <<'PY'
import json,datetime,urllib.request,zipfile
from pathlib import Path
url='http://127.0.0.1:8765/api/research/monitor-consolidation'
try:
 with urllib.request.urlopen(url,timeout=45) as response:
  body=response.read(40*1024*1024+1)
 if len(body)>40*1024*1024:raise ValueError('Resposta maior que o limite de coleta')
 d=json.loads(body)
 if not isinstance(d,dict):raise ValueError('Resposta JSON inesperada')
except Exception as exc:
 raise SystemExit('COLETA_NAO_CONCLUIDA: '+type(exc).__name__+'; confirme que o Porquinho está aberto. Nenhum arquivo de diagnóstico foi gerado.')
keys=('schema','status','observed_at','diagnostic_revision','canonical','issues','analysis_coverage','cash_plan_assessment','cash_plan_visibility','economic_action_policy','economic_action_evidence','economic_action_plan','learned_policy_economic_basis','learned_policy_account_context','account_cost_evidence')
report={k:d[k] for k in keys if k in d}
report['collection']={'mode':'LOCAL_HTTP_READ','training_requested':False,'financial_mutation_requested':False,'missing_fields':[k for k in keys if k not in d]}
folder=Path.home()/'Downloads';folder.mkdir(exist_ok=True)
output=folder/('PORQUINHO_FLUXO_RECOMENDACOES_V83_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip')
with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED) as z:
 z.writestr('fluxo_recomendacoes.json',json.dumps(report,ensure_ascii=False,indent=2))
print('PUBLICACAO_CANONICA:',(d.get('canonical') or {}).get('status','CAMPO_AUSENTE'))
for key in ('cash_plan_assessment','economic_action_policy','economic_action_evidence','economic_action_plan'):
 value=d.get(key) or {};print(key+':',value.get('status','CAMPO_AUSENTE'))
print('COLETA_LOCAL_CONCLUIDA; SEM_SOLICITACAO_DE_TREINAMENTO_OU_NEGOCIACAO')
print('ENVIAR='+str(output))
PY
