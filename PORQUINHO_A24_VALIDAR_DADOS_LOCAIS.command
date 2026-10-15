#!/bin/bash
set -euo pipefail
umask 077
ROOT="${PORQUINHO_ROOT:-$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2}"
PYTHON_BIN="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON_BIN="$ROOT/.venv/bin/python"; fi
"$PYTHON_BIN" -I -B - "$ROOT" <<'PYCODE'
import sys, json, hashlib, os, traceback
from pathlib import Path
from datetime import datetime, timezone
if sys.version_info < (3,10):
 raise SystemExit('FAIL_CLOSED: Python 3.10+ necessário.')
root=Path(sys.argv[1]).expanduser().resolve(strict=True)
expected={'universal_portfolio/universal_runtime_composition.py': '4965eb30800bd82f36fe009a0902a6800ebb0bbf0e8bcc2030c0908fbcf2edf4', 'universal_portfolio/universal_observation_bridge.py': '22a900ffc3c25abd44752f302d018d9a597b3061a9fc68d7be57d44421f97044', 'universal_portfolio/governed_comparison_producer_a2.py': '0ce26008946296acc50b119902b2f7544ced62aa699579ea3cb073e5746438c2', 'universal_portfolio/a2_economic_sizing_bridge.py': '42f1308058cc6ca64c1534f5f8dac0009b93e1ad7e6c482d3589eac67c2f5947', 'universal_portfolio/brain_economic_runtime_boundary_p32.py': '88f25921386ad806b3b9a3486533d46dcbb83d01da3a5e179a4f52ca73e20cae', 'webapp/server.py': '1137a8572b9db42ff8720e31b5c76cf7589d2f6a93b00ec43f77c1e50ce3ae06', 'static/app.js': '408b7ca9272a15fce5014a8078b082d27349e81f111e4526287182ce5e230692', 'universal_portfolio/governed_economic_input_transport_a24.py': 'bebc4f06d92c20131cda6e4b871adcefc60771d79949fe7afdc4f39a80a08c1d', 'tests/test_a24_governed_economic_integration.py': 'fa7187bbb3ddeca118d71dec2384686dadad9b99795cdcd76f0e0d0d94797900'}
for rel,digest in expected.items():
 p=root/rel
 if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
  raise SystemExit('FAIL_CLOSED: arquivo A24 ausente ou alterado: '+rel)
# Enforce read-only access inside the project, including during imports.
# No application startup, HTTP requests, subprocesses or network are permitted.
def audit(event,args):
 if event in ('socket.connect','socket.bind','subprocess.Popen','os.system','os.exec','os.fork','os.posix_spawn'):
  raise PermissionError('A24_READ_ONLY_OPERATION_DENIED')
 if event=='open':
  path,mode,flags=args
  if isinstance(path,(str,bytes,os.PathLike)):
   p=Path(os.fsdecode(path)).resolve()
   if p.is_relative_to(root):
    writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
    if writing:raise PermissionError('A24_PROJECT_WRITE_DENIED')
 if event in ('os.remove','os.rename','os.rmdir','os.mkdir','os.chmod','os.chown','os.truncate','os.link','os.symlink','os.utime'):
  # This runner has no need for mutations anywhere during evaluation.
  raise PermissionError('A24_FILESYSTEM_MUTATION_DENIED')
sys.addaudithook(audit)
sys.path.insert(0,str(root))
report={'validation':'A24_REAL_LOCAL_READ_ONLY','status':'NOT_COMPLETED',
        'fixtures':False,'services_restarted':False,'execution_authorized':False,
        'canonical_publication_operational':False}
try:
 from universal_portfolio.universal_runtime_composition import compose_shadow_cycle
 now=datetime.now(timezone.utc).isoformat()
 result=compose_shadow_cycle(root,observed_at=now,started_at=now,cycle_seed='A24_LOCAL_READ_ONLY_'+now)
 ui=result.economic_decision_ui_projection or {}
 proposal=ui.get('experimental_brain_proposal') or {}
 sizing=proposal.get('governed_sizing_evidence') or {}
 report.update(status='CYCLE_COMPLETED',
  observed_instrument_count=len(result.bridge.candidates),
  stages=[{'stage':s.stage,'status':s.status} for s in result.cycle.stages],
  comparison_intake=result.economic_comparison_intake,
  validated_comparison_count=len(result.economic_comparison_rows or ()),
  sizing_assessment_count=len(result.economic_sizing_assessments or ()),
  experimental_action=proposal.get('action'),
  sizing_verified_for_observed_identity=proposal.get('sizing_verified_for_observed_identity',False),
  sizing_status=sizing.get('status'),
  abstention_reasons=(ui.get('economic_abstention') or {}).get('reasons',()),
  canonical_missing_inputs=ui.get('canonical_production_missing_inputs',()),
  canonical_snapshot_count=len(result.cycle.recommendation_snapshots),
  financial_mutation=result.cycle.financial_mutation,
  history_write_performed=result.cycle.history_write_performed,
  execution_performed=result.cycle.execution_performed)
 if result.cycle.recommendation_snapshots or result.cycle.financial_mutation or result.cycle.history_write_performed or result.cycle.execution_performed:
  raise RuntimeError('READ_ONLY_INVARIANT_VIOLATION')
except Exception as exc:
 report.update(status='VALIDATION_BLOCKED',error_type=type(exc).__name__,
  failure_locations=[{'file':Path(f.filename).name,'function':f.name,'line':f.lineno}
                     for f in traceback.extract_tb(exc.__traceback__)][-6:])
 # Do not include exception messages or data payloads in the shareable report.
print(json.dumps(report,ensure_ascii=False,indent=2))
print('Nenhum serviço foi iniciado/reiniciado. Nenhuma operação financeira foi solicitada.')
print('Esta verificação avalia o código em processo separado; não comprova que a UI já carregou o A24.')
if report['status']!='CYCLE_COMPLETED':raise SystemExit(1)
PYCODE
