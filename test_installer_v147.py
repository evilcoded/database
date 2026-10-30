"""Four-file presentation install; synthetic dependencies and financial sentinels."""
import ast,base64,shutil,subprocess,sys,tempfile
from pathlib import Path
repo=Path(__file__).resolve().parent;project=Path('/workspace/porquinho-a24/project')
s=(repo/'PORQUINHO_DASHBOARD_GLOBAL_V147.command').read_text();code=s.split("<<'PYTHON'\n",1)[1].split('\nPYTHON',1)[0]
files=ast.literal_eval(next(l[6:] for l in code.splitlines() if l.startswith('FILES=')))
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp)/'app';shutil.copytree('/tmp/v147-old',root)
 for rel in ['brain/__init__.py','brain/knowledge/__init__.py','universal_portfolio/__init__.py','webapp/server.py']:
  p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('')
 for rel in ['universal_portfolio/global_action_readings_a24.py','universal_portfolio/universal_action_rules_a24.py','universal_portfolio/global_dashboard_observations_a24.py','universal_portfolio/operational_decision_core_a24.py','universal_portfolio/explicit_market_bindings_a24.py','universal_portfolio/suggestion_consolidation_a24.py','universal_portfolio/global_operational_plan_a24.py','universal_portfolio/consolidation_validation_a24.py','brain/execution_intelligence.py']:
  p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(project/rel,p)
 for rel in ['data/ledger.json','models/sentinel','config.json','data/brain/legacy/sentinel']:
  p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'PRESERVE')
 def run(target):
  body=code.replace("ROOT=Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2')",'ROOT=Path('+repr(str(target))+')')
  return subprocess.run([sys.executable,'-I','-B','-'],input=body,capture_output=True,text=True)
 divergence=Path(tmp)/'divergence';shutil.copytree(root,divergence);(divergence/'templates/index.html').write_text('LOCAL EDIT')
 before={p.relative_to(divergence):p.read_bytes() for p in divergence.rglob('*') if p.is_file()}
 r=run(divergence);assert r.returncode and 'BASE_DIVERGENTE' in r.stderr,r.stderr
 assert before=={p.relative_to(divergence):p.read_bytes() for p in divergence.rglob('*') if p.is_file()}
 backend={p.relative_to(root):p.read_bytes() for p in (root/'universal_portfolio').glob('*.py')}
 r=run(root);assert r.returncode==0,r.stderr
 assert 'CINCO_FLUXOS_VALIDADOS' in r.stdout and 'PATCH_DASHBOARD_GLOBAL_V147_OK' in r.stdout
 for rel,b in files.items():assert (root/rel).read_bytes()==base64.b64decode(b)
 before={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
 r=run(root);assert r.returncode==0,r.stderr
 assert before=={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
 for rel,data in backend.items():assert (root/rel).read_bytes()==data
 for rel in ['data/ledger.json','models/sentinel','config.json','data/brain/legacy/sentinel']:assert (root/rel).read_bytes()==b'PRESERVE'
print('V147_FOUR_PAYLOADS_BACKUP_IDEMPOTENCE_PREFLIGHT_KNOWLEDGE_AND_DECISION_FINANCIAL_MODEL_PRESERVATION_OK')
