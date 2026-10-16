#!/bin/bash
# Explicit isolated research fitting; no restart, network or legacy history writes.
set -euo pipefail
umask 077
ROOT="${PORQUINHO_ROOT:-$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2}"
PYTHON_BIN="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON_BIN="$ROOT/.venv/bin/python"; fi
"$PYTHON_BIN" -I -B - "$ROOT" <<'A24_REUSE_BATCH_PY'
import datetime as dt,hashlib,json,os,subprocess,sys
from pathlib import Path
root=Path(sys.argv[1]).expanduser().resolve(strict=True)
EXPECTED={'brain/evolution/global_existing_lab_a24.py': '5750f94d189a74c5b6a91ab06b4f2e54ef58ea28cc4790aba971e55e7dbead92', 'tools/run_global_existing_lab_a24.py': '095ed645df9590450b819e46fa45a79ca85e4a396e35b068d4ea311d45c22474', 'brain/evolution/prediction_lab.py': '4ffb7e5065a5f174427a3afd95df4b881e677671536218216d556a377d9c6b40', 'brain/evolution/global_market_frame_a24.py': '69c8ffad548b7f3a507c9cac73f0c978bd0778dce0b8532ee0c3493c3aa58f9d', 'universal_portfolio/global_history_source_a24.py': 'b8d3c700a6afe86e0af863d2f747c07b8442325d0d825060d5d06c0e45cd0355', 'brain/evolution/global_research_lab_a24.py': '629040ff74f5e0b625e734085686c62156446749571916817448e2200852074c'}
for rel,want in EXPECTED.items():
 p=root/rel
 if p.is_symlink() or any(a.is_symlink() for a in p.parents) or hashlib.sha256(p.read_bytes()).hexdigest()!=want:raise SystemExit('BATCH_SOURCE_HASH_MISMATCH: '+rel)
downloads=Path(os.environ.get('PORQUINHO_ACTIVATOR_DIRECTORY',str(Path.home()/'Downloads'))).expanduser();downloads.mkdir(exist_ok=True)
if downloads.resolve().is_relative_to(root):raise SystemExit('BATCH_REPORT_MUST_BE_OUTSIDE_PROJECT')
report=downloads/('PORQUINHO_A24_LAB_GLOBAL_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.json')
print('PROCESSANDO_LABORATORIO_GLOBAL_ISOLADO: até 20 experiências; pode levar alguns minutos. Sem rede ou escrita no histórico anterior.',flush=True)
with report.open('xb') as stream:
 result=subprocess.run([sys.executable,'-I','-B',str(root/'tools/run_global_existing_lab_a24.py'),'--root',str(root),'--max-jobs','20'],cwd=root,stdout=stream,check=False)
print('RELATORIO_PARA_COMPARTILHAR='+str(report),flush=True)
if result.returncode:raise SystemExit('BATCH_NOT_COMPLETED: consulte o relatório; não execute operações ou refresh para corrigir.')
try:
 data=json.loads(report.read_text());summary=data['summary'];batch=data['batch']
 print(json.dumps({'validation':data['validation'],'status':batch['status'],'experiments_created':batch['experiments_created'],'completed_experiment_count':summary.get('completed_experiment_count'),'planned_experiment_count':summary.get('planned_experiment_count'),'legacy_write_guard_active':data['legacy_write_guard_active'],'financial_mutation':False,'canonical_publication_authorized':False},ensure_ascii=False,indent=2))
except Exception as exc:raise SystemExit('BATCH_REPORT_UNAVAILABLE: '+type(exc).__name__)

A24_REUSE_BATCH_PY
