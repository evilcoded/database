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
EXPECTED_PAYLOAD_SHA256 = "e49c2001e3c72545b9b780732a554be9d26c1e32c98ba5a2ce2082401c9bfeae"
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
 (backup/'APPLIED_OK.txt').write_text('A24 local case review applied; 351 offline Python tests passed in staging.\n')
 print('PATCH_APPLIED_A24_CASE_REVIEW')
 print('BACKUP='+str(backup))
 print('REGRESSION_OK: 351 testes Python; fixtures sintéticas.')
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
