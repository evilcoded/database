#!/bin/bash
# macOS / Bash 3.2. Source patch only; no services or financial operations.
set -euo pipefail
umask 077
ROOT="${PORQUINHO_ROOT:-$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2}"
PYTHON_BIN="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON_BIN="$ROOT/.venv/bin/python"; fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
 printf 'FAIL_CLOSED: Python 3.10+ não encontrado; nenhum arquivo alterado.\n'; exit 1
fi
"$PYTHON_BIN" -I -B - "$ROOT" <<'A24_PYTHON'
import sys
if sys.version_info < (3,10):
 raise SystemExit('FAIL_CLOSED: Python 3.10+ necessário; nenhum arquivo alterado.')
from pathlib import Path
import base64,hashlib,io,json,os,shutil,stat,subprocess,tempfile,zipfile
from datetime import datetime
PAYLOAD = "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"
EXPECTED_PAYLOAD_SHA256 = "821ad525476751c546735391e4eecda235f1d370881730390566b97310d4d0f6"
raw=base64.b64decode(PAYLOAD,validate=True)
if hashlib.sha256(raw).hexdigest()!=EXPECTED_PAYLOAD_SHA256:
 raise SystemExit('FAIL_CLOSED: integridade do pacote inválida.')
root=Path(sys.argv[1]).expanduser().resolve(strict=True)
if not (root/'universal_portfolio').is_dir():
 raise SystemExit('FAIL_CLOSED: diretório ativo do Porquinho não encontrado.')

def digest_file(path):
 return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def target(rel):
 p=root/rel
 if p.is_symlink() or any(a.is_symlink() for a in p.parents if a!=root.parent):
  raise RuntimeError('FAIL_CLOSED: symlink no caminho '+rel)
 if not p.resolve().is_relative_to(root):
  raise RuntimeError('FAIL_CLOSED: caminho fora do projeto')
 if p.exists() and not p.is_file():
  raise RuntimeError('FAIL_CLOSED: alvo não é arquivo '+rel)
 return p

with zipfile.ZipFile(io.BytesIO(raw)) as package:
 metadata=json.loads(package.read('PATCH_MANIFEST.json'))
 entries=metadata['files']
 for rel in entries:target(rel)
 for rel,expected in metadata['test_baselines'].items():
  if digest_file(target(rel))!=expected:
   raise SystemExit('FAIL_CLOSED: teste existente diverge do pacote coletado: '+rel+'; nenhum arquivo alterado.')
 current={rel:digest_file(target(rel)) for rel in entries}
 already=all(current[rel]==spec['after'] for rel,spec in entries.items())
 if not already:
  for rel,spec in entries.items():
   if current[rel]!=spec['before']:
    raise SystemExit('FAIL_CLOSED: arquivo diverge do estado verificado pelo preflight: '+rel+'; nenhum arquivo alterado.')
 files={rel:package.read(rel) for rel in entries}
 for rel,content in files.items():
  if hashlib.sha256(content).hexdigest()!=entries[rel]['after']:
   raise SystemExit('FAIL_CLOSED: hash interno inválido: '+rel)
 with tempfile.TemporaryDirectory(prefix='porquinho_a24_validation_') as tmp:
  stage=Path(tmp)
  # Copy sources only. Do not copy data/results/models/history or start the app.
  for p in [*(root/'universal_portfolio').rglob('*.py'), *(root/'brain').rglob('*.py')]:
   if p.is_symlink() or any(a.is_symlink() for a in p.parents if a!=root.parent):
    raise SystemExit('FAIL_CLOSED: symlink em fontes de dependência.')
   rel=p.relative_to(root);dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True)
   shutil.copy2(p,dst)
  for rel in metadata['test_baselines']:
   dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target(rel),dst)
  for rel,content in files.items():
   dst=stage/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(content)
  (stage/'run_regressions.py').write_bytes(package.read('run_regressions.py'))
  print('VALIDATING_IN_TEMPORARY_SOURCE_COPY',flush=True)
  subprocess.run([sys.executable,'-I','-B',str(stage/'run_regressions.py')],cwd=stage,check=True)
 if already:
  print('ALREADY_APPLIED: hashes A24 e regressões confirmados; nenhuma alteração.')
  raise SystemExit(0)
 # Recheck after staging to avoid overwriting changes made during validation.
 for rel in entries:
  if digest_file(target(rel))!=current[rel]:
   raise SystemExit('FAIL_CLOSED: arquivo mudou durante a validação: '+rel)
 backup=root/('.porquinho_a24_review_backup_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
 backup.mkdir(mode=0o700)
 for rel in entries:
  p=target(rel)
  if p.exists():
   dst=backup/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
   if digest_file(dst)!=current[rel]:
    raise SystemExit('FAIL_CLOSED: backup divergente; código não alterado.')
 (backup/'PATCH_MANIFEST.json').write_text(json.dumps(metadata,indent=2))
 applied=[]
 def replace_bytes(path,content,mode):
  fd,name=tempfile.mkstemp(prefix='.a24_',dir=path.parent)
  try:
   with os.fdopen(fd,'wb') as h:
    h.write(content);h.flush();os.fsync(h.fileno())
   os.chmod(name,mode);os.replace(name,path)
  finally:
   if os.path.exists(name):os.unlink(name)
 try:
  for rel,content in files.items():
   p=target(rel)
   if digest_file(p)!=current[rel]:raise RuntimeError('Arquivo mudou durante aplicação: '+rel)
   mode=stat.S_IMODE(p.stat().st_mode) if p.exists() else 0o600
   replace_bytes(p,content,mode);applied.append(rel)
  for rel,spec in entries.items():
   if digest_file(target(rel))!=spec['after']:raise RuntimeError('Pós-check divergente: '+rel)
 except BaseException:
  for rel in reversed(applied):
   p=target(rel)
   if digest_file(p)!=entries[rel]['after']:
    print('ROLLBACK_REQUIRES_REVIEW: arquivo mudou externamente: '+rel,flush=True);continue
   old=backup/rel
   if old.is_file():replace_bytes(p,old.read_bytes(),stat.S_IMODE(old.stat().st_mode))
   else:p.unlink()
  print('APPLY_FAILED: rollback tentado; backups preservados em '+str(backup),flush=True)
  raise
 (backup/'APPLIED_OK.txt').write_text('A24 local case review applied; 349 offline Python tests passed in staging.\n')
 print('PATCH_APPLIED_A24_CASE_REVIEW')
 print('BACKUP='+str(backup))
 print('REGRESSION_OK: 349 testes Python; fixtures sintéticas.')
 print('CANONICAL_PROMOTION=BLOCKED_UNTIL_VERIFIED_PRODUCER')
 print('FINANCIAL_OPERATIONS=NONE; SERVICE_RESTARTS=NONE')
 print('O instalador preservou dados, modelos, memória e histórico existentes.')
 print('Ficha local por instrumento e moeda; fontes e evidências exigem revisão explícita, sem seleção automática.')
 print('Nenhum vínculo foi criado. Não é necessário reiniciar serviços para abrir a ficha de revisão.')
 print('Fontes revisadas permanecem RESEARCH_ONLY; nenhuma ordem, treinamento ou publicação canônica foi autorizada.')
 print('PREPARING_LOCAL_CASE_REVIEW',flush=True)
 try:
  subprocess.run([sys.executable,'-I','-B','-c',"import sys,os,json,datetime\nfrom pathlib import Path\nroot=Path(sys.argv[1]).resolve(strict=True)\nbase=Path(os.environ.get('PORQUINHO_REVIEW_DIRECTORY',str(Path.home()/'Downloads'))).expanduser().resolve(strict=True)\nsys.path.insert(0,str(root))\ndef guard(event,args):\n if event=='open':\n  mode,flags=args[1:3]\n  writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))\n  if writing and (not isinstance(args[0],(str,bytes,os.PathLike)) or not Path(os.fsdecode(args[0])).resolve().is_relative_to(base)):raise RuntimeError('REVIEW_WRITE_OUTSIDE_DOWNLOADS_REFUSED')\n if event=='os.mkdir' and not Path(args[0]).resolve().is_relative_to(base):raise RuntimeError('REVIEW_MKDIR_REFUSED')\n if event in {'os.remove','os.rename','os.rmdir','os.truncate','os.link','os.symlink','subprocess.Popen','os.system','socket.connect','socket.bind'}:raise RuntimeError('REVIEW_SIDE_EFFECT_REFUSED')\nsys.addaudithook(guard)\nfrom tools.review_funded_bindings_a24 import export\nfolder=base/('PORQUINHO_A24_REVISAO_CASOS_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d_%H%M%S_%f'))\nprint(json.dumps(export(root,folder),ensure_ascii=False,indent=2))\n",str(root)],cwd=root,check=True,timeout=120)
 except subprocess.SubprocessError as exc:
  print('PATCH_APPLIED; REVIEW_EXPORT_NOT_COMPLETED:'+type(exc).__name__)
A24_PYTHON
