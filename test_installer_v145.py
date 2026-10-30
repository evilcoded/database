"""Installer payload verification with synthetic sentinels; never uses a live app."""
import ast,base64,hashlib,shutil,subprocess,sys,tempfile
from pathlib import Path
repo=Path(__file__).resolve().parent
script=(repo/'PORQUINHO_CONSOLIDACAO_SUGESTOES_V145.command').read_text()
code=script.split("<<'PYTHON'\n",1)[1].split('\nPYTHON',1)[0]
files=ast.literal_eval(next(l[6:] for l in code.splitlines() if l.startswith('FILES=')))
# V144 public payloads are the exact authorized baselines. History and planning
# modules unchanged in V144 are recovered from the pre-edit fixture in this test.
old=Path('/tmp/v145-old');project=Path('/workspace/porquinho-a24/project')
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp)/'app';shutil.copytree(old,root)
 for n in ('brain/__init__.py','brain/knowledge/__init__.py','webapp/server.py'):
  p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('')
 shutil.copy2(project/'brain/knowledge/system_registry.py',root/'brain/knowledge/system_registry.py')
 for rel in ('data/ledger.json','models/sentinel','config.json','data/brain/legacy/sentinel'):
  p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'PRESERVE')
 def run(target):
  c=code.replace("ROOT=Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2')",'ROOT=Path('+repr(str(target))+')')
  return subprocess.run([sys.executable,'-I','-B','-'],input=c,text=True,capture_output=True)
 divergent=Path(tmp)/'divergent';shutil.copytree(root,divergent)
 (divergent/'universal_portfolio/global_operational_plan_a24.py').write_text('LOCAL EDIT')
 before={p.relative_to(divergent):p.read_bytes() for p in divergent.rglob('*') if p.is_file()}
 failure=run(divergent);assert failure.returncode and 'BASE_DIVERGENTE' in failure.stderr
 assert before=={p.relative_to(divergent):p.read_bytes() for p in divergent.rglob('*') if p.is_file()}
 result=run(root);assert result.returncode==0,result.stderr
 assert 'PATCH_CONSOLIDACAO_SUGESTOES_V145_OK' in result.stdout
 for n,b in files.items():assert (root/n).read_bytes()==base64.b64decode(b)
 before={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
 assert run(root).returncode==0
 assert before=={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
 for rel in ('data/ledger.json','models/sentinel','config.json','data/brain/legacy/sentinel'):assert (root/rel).read_bytes()==b'PRESERVE'
print('V145_SEVEN_PAYLOADS_IDEMPOTENT_KNOWLEDGE_CURRENT_DIVERGENCE_REFUSED_FINANCIAL_MODELS_PRESERVED_OK')
