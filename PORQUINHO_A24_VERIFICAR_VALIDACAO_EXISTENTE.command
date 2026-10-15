#!/bin/bash
# Read-only evaluation of existing prospective proofs. Does not patch the project.
set -euo pipefail
umask 077
ROOT="${PORQUINHO_ROOT:-$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2}"
PYTHON_BIN="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON_BIN="$ROOT/.venv/bin/python"; fi
"$PYTHON_BIN" -I -B - "$ROOT" <<'PYCODE'
import sys,os,json,hashlib,re
from pathlib import Path
from collections import Counter
if sys.version_info < (3,10):raise SystemExit('Python 3.10+ necessário.')
root=Path(sys.argv[1]).expanduser().resolve(strict=True)
expected={'brain/__init__.py': 'b712772a4999d2207e73fb20ad8eb6ad182ff9b2ea49b1f2ea404205badff721', 'brain/prospective_buy_calibration_acceptance_v3.py': '89c0e1584c52976025cca18b72b02371428b17198c1ce60743702075a0ab8306', 'brain/prospective_buy_calibration_baseline_artifact_v2.py': 'bc160c7b2848374dd9ecaede3e2b30f6c45c8f73607d6bb17d4dd696d8b0718a', 'brain/prospective_buy_calibration_baseline_store_v2.py': 'e0ad7ced888d4018f51d286ecea2d651e1c001eab26bcec1deba4e2156d13962', 'brain/prospective_buy_calibration_holdout_contract.py': '4ed0ba712a0b8045a5c3eb084f80f85202e5a7a8cb636b0690f4c60c559baaa0', 'brain/prospective_buy_calibration_reliability_contract.py': '83bcb6d0dc61d7fa39374406f75b877d2b17bcf3ef3245b384adc7c5e7ecb6db', 'brain/prospective_buy_calibration_split_contract.py': 'c9764d54612aaf66005adbb2394b42c8bcd9126d51aee913a732b8852f7a69a1', 'brain/prospective_buy_calibration_v3_proof_envelope.py': 'b9a4ef0927f4e1db7c0d5efa00e614415a71bf379eaac3768d7955fbe1688312', 'brain/prospective_buy_calibration_verified_holdout_assembler.py': '101e40d5eafccf05abbace44dbe096b51e36532299a51d037ff1faf88d17e041', 'brain/prospective_buy_calibration_verified_lineage.py': '514e94b1f773626626581ea76566523055e8b69a7223192562b80a7adad983eb', 'brain/prospective_buy_forecast.py': 'b6d90078e45c57f60a1dfbebf39e87bac544f5bb2795cdc49e8780936eb3ab82', 'brain/prospective_buy_forecast_store.py': 'b0377cb8a25169d07090d17d59eadb640c0f391e45db58fa89cb4d0b4e6394eb', 'brain/prospective_buy_outcome_join_contract.py': 'cfee2466c2c3d070040cbd631671cf86bdbc21980e54fa9db5dfb3b1c2d180c8', 'brain/prospective_buy_outcome_source_adapter.py': '2af3f023f53b9c401708874fd91f05191cbb012aaeb975268a9e140b41cdce57'}
for rel,digest in expected.items():
 p=root/rel
 if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
  raise SystemExit('FAIL_CLOSED: fonte diferente da versão recebida: '+rel)
# Block all writes, subprocesses and network while evaluating existing modules.
def guard(event,args):
 if event in ('socket.connect','socket.bind','subprocess.Popen','os.system','os.exec','os.fork','os.posix_spawn',
              'os.remove','os.rename','os.rmdir','os.mkdir','os.chmod','os.chown','os.truncate','os.link','os.symlink','os.utime'):
  raise PermissionError('READ_ONLY_OPERATION_DENIED')
 if event=='open':
  path,mode,flags=args
  if (isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)):
   raise PermissionError('READ_ONLY_WRITE_DENIED')
sys.addaudithook(guard)
sys.path.insert(0,str(root))
from brain.prospective_buy_calibration_v3_proof_envelope import evaluate

def load(path):
 if path.is_symlink() or not path.resolve().is_relative_to(root):raise ValueError('SOURCE_PATH_NOT_LOCAL')
 if path.stat().st_size>16*1024*1024:raise ValueError('SOURCE_TOO_LARGE')
 return json.loads(path.read_text(encoding='utf-8'))

def records(rel):
 p=root/rel
 if not p.exists():return [],'MISSING'
 if not p.is_dir():raise ValueError('SOURCE_DIRECTORY_REQUIRED')
 paths=sorted(p.glob('*.json'))
 if len(paths)>20000:raise ValueError('SOURCE_POPULATION_TOO_LARGE')
 data=[load(p) for p in paths]
 if any(not isinstance(x,dict) for x in data):raise ValueError('MALFORMED_SOURCE_RECORD')
 return data,'PRESENT' if data else 'EMPTY'

def safe_code(value):
 return value if isinstance(value,str) and re.fullmatch('[A-Z][A-Z0-9_]{0,180}',value) else 'UNSPECIFIED'

report={'validation':'EXISTING_PROSPECTIVE_PROOF_READ_ONLY',
        'financial_mutation':False,'automatic_training':False,'automatic_promotion':False,
        'services_restarted':False,'expected_returns_certified':False,
        'sizing_certified':False,'canonical_publication_authorized':False}
try:
 baselines,bs=records('data/brain/prospective/buy_calibration_baselines_v2')
 forecasts,fs=records('data/brain/prospective/buy_forecasts')
 joins,js=records('data/brain/prospective/buy_outcome_joins')
 op=root/'data/brain_experimental_episodes/outcomes_latest.json'
 outcomes=load(op) if op.exists() else None
 if isinstance(outcomes,dict):
  outcomes=next((outcomes[k] for k in ('episodes','outcomes','episode_outcomes')
                 if isinstance(outcomes.get(k),list)),None)
 report['sources']={'baseline_store':bs,'forecast_store':fs,'outcome_join_store':js,
                    'canonical_episode_outcomes':'PRESENT' if isinstance(outcomes,list) else 'MISSING_OR_INVALID'}
 report['counts']={'baselines':len(baselines),'forecasts':len(forecasts),'joins':len(joins),
                   'canonical_episode_outcomes':len(outcomes) if isinstance(outcomes,list) else None}
 horizons=Counter()
 for w in baselines:
  b=w.get('baseline')
  if isinstance(b,dict) and type(b.get('horizon_days')) is int:horizons[b['horizon_days']]+=1
 proofs=[]
 for w in baselines:
  b=w.get('baseline') or {};h=b.get('horizon_days') if isinstance(b,dict) else None
  if type(h) is not int:
   proofs.append({'state':'FAIL_CLOSED','reason':'BASELINE_HORIZON_INVALID'});continue
  if horizons[h]!=1:
   proofs.append({'horizon_days':h,'state':'FAIL_CLOSED','reason':'AMBIGUOUS_BASELINE_FOR_HORIZON'});continue
  if not isinstance(outcomes,list):
   proofs.append({'horizon_days':h,'state':'NOT_READY','reason':'CANONICAL_EPISODE_OUTCOMES_REQUIRED'});continue
  value=evaluate(forecasts,joins,w,outcomes)
  proofs.append({'horizon_days':h,'state':safe_code(value.get('state')),
    'reason':safe_code(value.get('reason')),
    'proof_verified':value.get('proof_verified') is True,
    'calibration_accepted':value.get('calibration_accepted') is True,
    'holdout_count':value.get('holdout_count',value.get('verified_matured_holdout_count'))})
 report['proofs']=proofs
 report['status']='EVALUATED' if baselines else 'BLOCKED_NO_PERSISTED_BASELINE'
 report['semantics']='SUCCESS_PROBABILITY_CALIBRATION_ONLY_NOT_EXPECTED_RETURN_OR_SIZING'
except Exception as exc:
 report.update(status='EVALUATION_BLOCKED',error_type=type(exc).__name__)
print(json.dumps(report,ensure_ascii=False,indent=2))
print('Nenhum dado individual foi exportado. Nenhum arquivo do projeto foi alterado.')
PYCODE
