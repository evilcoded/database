#!/bin/bash
set -euo pipefail
umask 077
"$HOME/anaconda3/bin/python" -I -B - <<'PYTHON'
from pathlib import Path
import base64,hashlib,datetime,shutil,os,tempfile
ROOT=Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2')
FILES={'start_web.command': 'IyEvYmluL2Jhc2gKc2V0IC1ldW8gcGlwZWZhaWwKUk9PVD0iJChjZCAiJChkaXJuYW1lICIkMCIpIiAmJiBwd2QgLVApIgpFWFBFQ1RFRF9ST09UPSIvQXBwbGljYXRpb25zL0JyaWRnZV9Db21wYW5pb24vcG9ycXVpbmhvX3YzM193ZWJfZm91bmRhdGlvbi0yIgppZiBbICIkUk9PVCIgIT0gIiRFWFBFQ1RFRF9ST09UIiBdOyB0aGVuCiAgZWNobyAiSU5JQ0lBTElaQURPUl9MT0NBTDogdXNlIGEgY29waWEgZW0gJEVYUEVDVEVEX1JPT1QiCiAgZXhpdCAxCmZpCmNkICIkUk9PVCIKUFlUSE9OX0JJTj0iJFJPT1QvLnZlbnZfcmVjb3ZlcnlfMjAyNjEwMjFfMDE0MDQ5L2Jpbi9weXRob24iCmlmIFsgISAteCAiJFBZVEhPTl9CSU4iIF07IHRoZW4KICBlY2hvICJBTUJJRU5URV9SRUNVUEVSQURPX0FVU0VOVEU6IG5lbmh1bWEgaW5zdGFsYWNhbyBhdXRvbWF0aWNhIGV4ZWN1dGFkYS4iCiAgZXhpdCAxCmZpCnBpZHM9IiQobHNvZiAtdGlUQ1A6ODc2NSAtc1RDUDpMSVNURU4gMj4vZGV2L251bGwgfHwgdHJ1ZSkiCmlmIFsgLW4gIiRwaWRzIiBdOyB0aGVuCiAgZm9yIHBpZCBpbiAkcGlkczsgZG8KICAgIHByb2Nlc3NfZGlyPSIkKGxzb2YgLWEgLXAgIiRwaWQiIC1kIGN3ZCAtRm4gfCBzZWQgLW4gJ3MvXm4vL3AnKSIKICAgIGlmIFsgIiRwcm9jZXNzX2RpciIgIT0gIiRST09UIiBdOyB0aGVuCiAgICAgIGVjaG8gIlBPUlRBX09DVVBBREFfRk9SQV9ERV9BUFBMSUNBVElPTlM6ICRwcm9jZXNzX2RpciIKICAgICAgZXhpdCAxCiAgICBmaQogIGRvbmUKICBpZiBjdXJsIC0tbm9wcm94eSAnKicgLS1mYWlsIC0tc2lsZW50IC0tc2hvdy1lcnJvciAtLW1heC10aW1lIDEwIGh0dHA6Ly8xMjcuMC4wLjE6ODc2NS8gPi9kZXYvbnVsbDsgdGhlbgogICAgb3BlbiBodHRwOi8vMTI3LjAuMC4xOjg3NjUvCiAgICBleGl0IDAKICBmaQogIGVjaG8gIlBST0NFU1NPX0xPQ0FMX1NFTV9SRVNQT1NUQTogbmVuaHVtYSBzZWd1bmRhIGluc3RhbmNpYSBpbmljaWFkYS4iCiAgZXhpdCAxCmZpCiMgT3BlbiB0aGUgYnJvd3NlciBvbmx5IGFmdGVyIGEgbG9jYWwgSFRUUCByZXNwb25zZTsgbGVhdmUgc2VydmVyIGluIGZvcmVncm91bmQuCigKICBmb3IgYXR0ZW1wdCBpbiB7MS4uNjB9OyBkbwogICAgaWYgY3VybCAtLW5vcHJveHkgJyonIC0tZmFpbCAtLXNpbGVudCAtLW1heC10aW1lIDIgaHR0cDovLzEyNy4wLjAuMTo4NzY1LyA+L2Rldi9udWxsOyB0aGVuCiAgICAgIG9wZW4gaHR0cDovLzEyNy4wLjAuMTo4NzY1LwogICAgICBleGl0IDAKICAgIGZpCiAgICBzbGVlcCAxCiAgZG9uZQogIGVjaG8gIlNlcnZpZG9yIGFpbmRhIHNlbSByZXNwb3N0YSBIVFRQOyBjb25zdWx0ZSBlc3RhIGphbmVsYS4iCikgJgpCUk9XU0VSX1dBSVRFUj0kIQpjbGVhbnVwKCkgeyBraWxsICIkQlJPV1NFUl9XQUlURVIiIDI+L2Rldi9udWxsIHx8IHRydWU7IH0KdHJhcCBjbGVhbnVwIEVYSVQKIiRQWVRIT05fQklOIiAtQiAtbSB3ZWJhcHAuc2VydmVyCg=='}
assert (ROOT/'webapp/server.py').is_file(), 'PROJETO_NAO_ENCONTRADO'
assert not ROOT.is_symlink(), 'SYMLINK_RECUSADO'
prepared=[]
for name,encoded in FILES.items():
 p=ROOT/name
 assert not any(a.is_symlink() for a in [p,*p.parents]), 'SYMLINK_RECUSADO'
 assert p.parent.is_dir(), 'PASTA_AUSENTE: '+name
 body=base64.b64decode(encoded,validate=True)
 if p.is_file() and p.read_bytes()==body: continue
 assert not p.exists() or p.is_file(), 'DESTINO_INVALIDO'
 prepared.append((name,p,body))
backup=ROOT/('.recovery_local_launcher_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
if prepared:
 backup.mkdir(mode=0o700)
 for name,p,body in prepared:
  if p.exists():
   dest=backup/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 for name,p,body in prepared:
  fd,tmp=tempfile.mkstemp(prefix='.recovery-',dir=p.parent)
  try:
   with os.fdopen(fd,'wb') as f: f.write(body)
   os.chmod(tmp,0o700);os.replace(tmp,p)
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
 print('BACKUP='+str(backup))
for name,encoded in FILES.items():
 expected=base64.b64decode(encoded,validate=True)
 assert (ROOT/name).read_bytes()==expected
 print('VERIFICADO '+name+' '+hashlib.sha256(expected).hexdigest())
print('INICIALIZADOR_APPLICATIONS_CONFIGURADO; SERVICOS_NAO_INICIADOS; DADOS_E_MODELOS_NAO_ALTERADOS')
PYTHON
