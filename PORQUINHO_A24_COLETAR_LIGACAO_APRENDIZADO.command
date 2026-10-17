#!/bin/bash
# macOS Bash 3.2; explicit Brain source collection, no application execution.
set -euo pipefail
umask 077
ROOT="${PORQUINHO_ROOT:-$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2}"
PYTHON_BIN="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON_BIN="$ROOT/.venv/bin/python"; fi
"$PYTHON_BIN" -I -B - "$ROOT" "${PORQUINHO_REPORT_DIRECTORY:-$HOME/Downloads}" <<'BRAIN_LINK_PY'
import sys
if sys.version_info < (3,10):raise SystemExit('Python 3.10+ necessário; projeto preservado.')
"""Collect explicitly listed Brain source files, never application state."""
import ast
import hashlib
import json
import os
import re
import stat
import uuid
import zipfile
from pathlib import Path

SOURCES = (
    'brain/memory/store.py', 'brain/memory/store/__init__.py',
    'brain/memory/conversation.py', 'brain/memory/__init__.py',
    'brain/core/brain.py', 'brain/core/self_model.py', 'brain/core/cognitive.py',
    'brain/research/engine.py', 'brain/evolution/optimizer.py',
    'brain/evolution/validator.py', 'brain/evolution/self_scan.py',
    'brain/evolution/hypothesis_engine.py', 'brain/evolution/learning_audit.py',
    'brain/evolution/learning_cycle.py', 'brain/evolution/quantitative_evolution.py',
    'brain/evolution/prediction_lab.py', 'brain/learning_promotion_governance.py',
    'brain/evolution/global_existing_lab_a24.py',
    'universal_portfolio/economic_action_policy_a24.py',
    'universal_portfolio/account_action_policy_store_a24.py',
    'universal_portfolio/universal_observation_bridge.py',
    'universal_portfolio/universal_runtime_composition.py',
    'porquinho.py', 'webapp/server.py',
)
MAX_FILE = 2 * 1024 * 1024
MAX_TOTAL = 12 * 1024 * 1024
CALLS = frozenset(('MemoryStore', 'ingest_snapshot', '_learn', 'run_prediction_next',
                   'run_next', 'evolve', 'experiment', 'event', 'assess', 'load_model',
                   'score_asset', 'target_weights', 'compose_shadow_cycle'))
SECRET = re.compile(r'(^|_)(password|secret|api_key|access_token|refresh_token|client_secret)($|_)', re.I)


class CollectError(ValueError):
    pass


def signature(info):
    return info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns


def local(root, rel):
    p = root / rel
    if any(x.is_symlink() for x in (p, *p.parents)) or not p.resolve().is_relative_to(root):
        raise CollectError('SYMLINK_OR_EXTERNAL_SOURCE_REFUSED')
    return p


def source(root, rel):
    p = local(root, rel)
    fd = os.open(p, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise CollectError('REGULAR_SOURCE_FILE_REQUIRED')
        if before.st_size > MAX_FILE:
            raise CollectError('SOURCE_SIZE_LIMIT')
        raw = stream.read(MAX_FILE + 1)
        if len(raw) > MAX_FILE or signature(before) != signature(os.fstat(stream.fileno())):
            raise CollectError('SOURCE_CHANGED_OR_SIZE_LIMIT')
    if signature(before) != signature(p.stat()):
        raise CollectError('SOURCE_REPLACED_DURING_READ')
    tree = ast.parse(raw, filename=rel)
    # Do not export directly assigned literal credentials. No config files or
    # environment values are inspected. This check is not a complete secret scan.
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str) and node.value.value.strip():
                if any(isinstance(t, ast.Name) and SECRET.search(t.id) for t in targets):
                    raise CollectError('LITERAL_CREDENTIAL_CANDIDATE_SOURCE_NOT_EXPORTED')
        if isinstance(node, ast.Dict):
            if any(isinstance(k, ast.Constant) and isinstance(k.value, str) and SECRET.search(k.value)
                   and isinstance(v, ast.Constant) and isinstance(v.value, str) and v.value.strip()
                   for k, v in zip(node.keys, node.values)):
                raise CollectError('LITERAL_CREDENTIAL_CANDIDATE_SOURCE_NOT_EXPORTED')
    calls = {name: 0 for name in CALLS}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else None
            if name in calls:
                calls[name] += 1
    return raw, signature(before), {k: v for k, v in sorted(calls.items()) if v}


def collect(root, output):
    root = Path(root).expanduser().resolve(strict=True)
    output = Path(output).expanduser().resolve(strict=True)
    if output.is_relative_to(root):
        raise CollectError('OUTPUT_MUST_BE_OUTSIDE_PROJECT')
    if not (root / 'webapp/server.py').is_file():
        raise CollectError('EXPECTED_PROJECT_REQUIRED')
    report = {'validation': 'A24_BRAIN_LEARNING_DECISION_SOURCE_CHAIN_READ_ONLY',
              'sources': {}, 'issues': [], 'project_mutation': False,
              'memory_database_exported': False, 'model_files_exported': False,
              'snapshots_exported': False, 'financial_data_files_exported': False,
              'configuration_files_exported': False, 'source_code_exported': True,
              'application_modules_imported': False, 'training_requested': False,
              'network_requests': 0, 'services_restarted': False,
              'learning_functionality_proven': False, 'execution_authorized': False,
              'canonical_publication_authorized': False}
    bodies = {}
    stamps = {}
    total = 0
    for rel in SOURCES:
        try:
            raw, stamp, calls = source(root, rel)
            total += len(raw)
            if total > MAX_TOTAL:
                raise CollectError('TOTAL_SOURCE_SIZE_LIMIT')
            bodies[rel] = raw
            stamps[rel] = stamp
            report['sources'][rel] = {'status': 'SOURCE_COPIED_NOT_EXECUTED',
                'sha256': hashlib.sha256(raw).hexdigest(), 'recognized_static_call_counts': calls}
        except FileNotFoundError:
            report['sources'][rel] = {'status': 'MISSING_IN_SELECTED_PROJECT'}
        except Exception as exc:
            reason = str(exc) if isinstance(exc, CollectError) else type(exc).__name__
            report['sources'][rel] = {'status': 'NOT_EXPORTED', 'reason': reason}
            report['issues'].append({'source': rel, 'reason': reason})
        if total > MAX_TOTAL:
            break
    stable = True
    for rel, stamp in stamps.items():
        try:
            if signature(local(root, rel).stat()) != stamp:
                stable = False
        except Exception:
            stable = False
    report['source_files_stable_during_collection'] = stable
    report['status'] = 'SOURCE_PACKAGE_CREATED_NOT_RUNTIME_VALIDATED' if stable and not report['issues'] else 'PARTIAL_SOURCE_PACKAGE_NOT_RUNTIME_VALIDATED'
    path = output / ('PORQUINHO_A24_LIGACAO_APRENDIZADO_' + uuid.uuid4().hex[:12] + '.zip')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('RELATORIO.json', json.dumps(report, ensure_ascii=False, indent=2))
                for rel, raw in bodies.items():
                    archive.writestr('project/' + rel, raw)
                archive.writestr('LEIA.txt', 'Fontes privadas do projeto para revisar a ligação aprendizado-decisão. Não publicar este ZIP.\nNenhum banco de memória, modelo, snapshot, configuração ou arquivo financeiro foi copiado.\nA análise estática não comprova funcionamento em execução.\n')
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise CollectError('ZIP_INTEGRITY_FAILED')
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return path, report


if __name__ == '__main__':
    import sys
    try:
        path, report = collect(sys.argv[1], sys.argv[2])
        print(json.dumps({k: v for k, v in report.items() if k != 'sources'}, ensure_ascii=False, indent=2))
        print('FONTES_COPIADAS=' + str(sum(r['status'] == 'SOURCE_COPIED_NOT_EXECUTED' for r in report['sources'].values())))
        print('ZIP_PARA_COMPARTILHAR=' + str(path))
        print('Projeto preservado; nenhum módulo do aplicativo executado. O ZIP contém fontes privadas: compartilhe somente nesta conversa.')
    except Exception as exc:
        raise SystemExit('COLETA_NAO_CONCLUIDA:' + (str(exc) if isinstance(exc, CollectError) else type(exc).__name__))

BRAIN_LINK_PY
