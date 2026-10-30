import ast,base64,tempfile,shutil,hashlib,os
from pathlib import Path
s=(Path(__file__).resolve().parent/'PORQUINHO_PROTECAO_CONHECIMENTO_V144.command').read_text();code=s.split("<<'PYTHON'\n",1)[1].split('\nPYTHON',1)[0]
files=ast.literal_eval(next(l[6:] for l in code.splitlines() if l.startswith('FILES=')))
old=Path(os.environ.get('V144_BASELINE_DIR','/tmp/v144-old'))
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp)/'app';shutil.copytree(old,root);(root/'webapp').mkdir(exist_ok=True);(root/'webapp/server.py').write_text('SERVER_SENTINEL')
 for init in ('brain/__init__.py','brain/knowledge/__init__.py'):(root/init).write_text('')
 for rel in ['data/ledger.json','models/sentinel','config.json','data/brain/legacy/sentinel']:
  p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'PRESERVE')
 run=code.replace("ROOT=Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2')",'ROOT=Path('+repr(str(root))+')')
 exec(compile(run,'installer','exec'),{})
 registry=(root/'data/brain/system_knowledge/registry.json').read_bytes()
 assert b'DESCRIPTIVE_CODE_AND_UI_ONLY' in registry
 backups=list(root.glob('.a24*'));exec(compile(run,'installer','exec'),{});assert list(root.glob('.a24*'))==backups
 assert (root/'data/brain/system_knowledge/registry.json').read_bytes()==registry
 for rel in ['data/ledger.json','models/sentinel','config.json','data/brain/legacy/sentinel']:assert (root/rel).read_bytes()==b'PRESERVE'
 for name,body in files.items():assert (root/name).read_bytes()==base64.b64decode(body)
 # Divergence must reject before creating any new dependency or modifying old files.
 other=Path(tmp)/'divergent';shutil.copytree(old,other);(other/'webapp').mkdir(exist_ok=True);(other/'webapp/server.py').write_text('SERVER_SENTINEL');(other/'universal_portfolio/experience_panels_a24.py').write_text('LOCAL CHANGE')
 before={str(p.relative_to(other)):p.read_bytes() for p in other.rglob('*') if p.is_file()}
 try:exec(compile(run.replace(str(root),str(other)),'installer','exec'),{})
 except AssertionError as e:assert 'BASE_DIVERGENTE' in str(e)
 else:raise AssertionError('divergence accepted')
 assert before=={str(p.relative_to(other)):p.read_bytes() for p in other.rglob('*') if p.is_file()}
print('INSTALLER_13_CAPITAL_KNOWLEDGE_FILES_IDEMPOTENCE_PREFLIGHT_DIVERGENCE_AND_FINANCIAL_MODEL_PRESERVATION_OK')
