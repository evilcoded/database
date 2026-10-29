import ast,base64,tempfile,shutil,hashlib,os
from pathlib import Path
s=(Path(__file__).resolve().parent/'PORQUINHO_CAPTURA_GLOBAL_V138.command').read_text();code=s.split("<<'PYTHON'\n",1)[1].split('\nPYTHON',1)[0]
files=ast.literal_eval(next(l[6:] for l in code.splitlines() if l.startswith('FILES=')))
old=Path(os.environ.get('V138_BASELINE_DIR','/tmp/v138-old'))
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp)/'app';shutil.copytree(old,root)
 for rel in ['data/ledger.json','models/sentinel','config.json','data/brain/legacy/sentinel']:
  p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'PRESERVE')
 run=code.replace("ROOT=Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2')",'ROOT=Path('+repr(str(root))+')')
 exec(compile(run,'installer','exec'),{})
 backups=list(root.glob('.a24*'));exec(compile(run,'installer','exec'),{});assert list(root.glob('.a24*'))==backups
 for rel in ['data/ledger.json','models/sentinel','config.json','data/brain/legacy/sentinel']:assert (root/rel).read_bytes()==b'PRESERVE'
 for name,body in files.items():assert (root/name).read_bytes()==base64.b64decode(body)
 # Divergence must reject before creating any new dependency or modifying old files.
 other=Path(tmp)/'divergent';shutil.copytree(old,other);(other/'webapp/server.py').write_text('LOCAL CHANGE')
 before={str(p.relative_to(other)):p.read_bytes() for p in other.rglob('*') if p.is_file()}
 try:exec(compile(run.replace(str(root),str(other)),'installer','exec'),{})
 except AssertionError as e:assert 'BASE_DIVERGENTE' in str(e)
 else:raise AssertionError('divergence accepted')
 assert before=={str(p.relative_to(other)):p.read_bytes() for p in other.rglob('*') if p.is_file()}
print('INSTALLER_4_FILES_IDEMPOTENCE_PREFLIGHT_DIVERGENCE_AND_FINANCIAL_MODEL_PRESERVATION_OK')
