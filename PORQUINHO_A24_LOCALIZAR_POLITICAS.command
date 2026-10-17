#!/bin/bash
# macOS Bash 3.2; read-only configuration inventory, no app imports.
set -euo pipefail
umask 077
ROOT="${PORQUINHO_ROOT:-$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2}"
PYTHON_BIN="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON_BIN="$ROOT/.venv/bin/python"; fi
"$PYTHON_BIN" -I -B - "$ROOT" "${PORQUINHO_REPORT_DIRECTORY:-$HOME/Downloads}" <<'POLICY_INVENTORY_PY'
import sys
if sys.version_info < (3,10):raise SystemExit('Python 3.10+ necessário; projeto preservado.')
"""Bounded local configuration inventory; exports field counts, never values."""
import hashlib
import json
import os
import re
import stat
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

MAX_BYTES = 8 * 1024 * 1024
MAX_TOTAL = 32 * 1024 * 1024
MAX_FILES = 150
MAX_NODES = 100000
KNOWN = (
    'data/investment_plans.json', 'data/planning_budgets.json',
    'data/delegated_authority_policies.json',
    'results/governed_economic_components_a24.json',
    'config.json', 'settings.json', 'data/config.json', 'data/settings.json',
    'data/risk_policies.json', 'data/liquidity_policies.json',
    'data/concentration_policies.json',
)
FIELDS = frozenset('''risk_policy liquidity_policy concentration_policy threshold
    metric_semantics scale unit horizon metric_family observation_window constraints
    metric operator account_id source_account_id currency plan_id policy_id version
    source effective_from effective_until validated provenance validation_ref
    risk_evidence liquidity_evidence current_exposure counterfactual_exposure
    scenario_reference_amount risk_effective_until liquidity_effective_until
    concentration_effective_until action_policy_inputs_a24 assessments
    planning_budget_id planning_budget_amount period strategy allowed_asset_classes
    execution_mode status authority policy_versions policy_payload approval_mode
    max_per_transaction max_per_day weekly_budget budget_currency
    max_position_weight max_concentration risk_limit risk_tolerance risk_profile
    liquidity_limit concentration_limit risk_threshold liquidity_threshold
    concentration_threshold'''.split())
SECRET = re.compile(r'credential|secret|password|token|api.?key|oauth|provider_items', re.I)
NAME = re.compile(r'polic|risk|liquid|concentr|config|setting|profile|plan|budget', re.I)


class InventoryError(ValueError):
    pass


def safe_path(root, relative):
    p = root / relative
    if any(x.is_symlink() for x in (p, *p.parents)):
        raise InventoryError('SYMLINK_REFUSED')
    if not p.resolve().is_relative_to(root):
        raise InventoryError('OUTSIDE_PROJECT_REFUSED')
    return p


def signature(s):
    return s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns


def read(root, relative):
    p = safe_path(root, relative)
    # Nonblocking + nofollow also prevents hanging on special files or link swaps.
    fd = os.open(p, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise InventoryError('REGULAR_FILE_REQUIRED')
        if before.st_size > MAX_BYTES:
            raise InventoryError('SOURCE_TOO_LARGE')
        raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise InventoryError('SOURCE_TOO_LARGE')
        if signature(before) != signature(os.fstat(stream.fileno())):
            raise InventoryError('SOURCE_CHANGED_DURING_READ')
    if signature(before) != signature(p.stat()):
        raise InventoryError('SOURCE_REPLACED_DURING_READ')
    def reject_constant(_):
        raise InventoryError('NONFINITE_JSON_REFUSED')
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise InventoryError('DUPLICATE_JSON_KEY_REFUSED')
            result[key] = value
        return result
    return json.loads(raw, parse_constant=reject_constant, object_pairs_hook=pairs), len(raw), signature(before)


def describe(value):
    counts = Counter()
    shapes = Counter()
    stack = [value]
    nodes = 0
    while stack:
        node = stack.pop()
        nodes += 1
        if nodes > MAX_NODES:
            raise InventoryError('JSON_NODE_LIMIT')
        if isinstance(node, list):
            stack.extend(node)
        elif isinstance(node, dict):
            # These are structural candidates only. No builder is called and no
            # declared validation flag becomes a finding of validity.
            keys = set(node)
            if {'threshold', 'metric_semantics', 'scale', 'unit', 'horizon'} <= keys:
                shapes['risk_policy_shaped_objects'] += 1
            if {'threshold', 'metric_family', 'metric_semantics', 'observation_window'} <= keys:
                shapes['liquidity_policy_shaped_objects'] += 1
            if {'constraints', 'policy_id', 'account_id', 'currency'} <= keys:
                shapes['concentration_policy_shaped_objects'] += 1
            if {'max_per_transaction', 'max_per_day', 'weekly_budget'} <= keys:
                shapes['execution_budget_policy_shaped_objects'] += 1
            if {'planning_budget_id', 'strategy', 'allowed_asset_classes'} <= keys:
                shapes['investment_plan_shaped_objects'] += 1
            for key, child in node.items():
                if SECRET.search(key):
                    continue
                if key in FIELDS:
                    counts[key] += 1
                stack.append(child)
    return {'recognized_field_occurrence_counts': dict(sorted(counts.items())),
            'structural_candidate_counts': dict(sorted(shapes.items())),
            'numeric_values_exported': False, 'candidate_validity_assessed': False}


def inventory(root):
    root = Path(root).expanduser().resolve(strict=True)
    if not (root / 'webapp/server.py').is_file():
        raise InventoryError('EXPECTED_PROJECT_REQUIRED')
    paths = set(KNOWN)
    # Only shallow JSON configuration candidates. No ledger, snapshot history,
    # memory, model files, provider credential stores or recursive data scan.
    discovery_issues = []
    for directory in ('config', 'settings', 'data'):
        try:
            folder = safe_path(root, directory)
            if folder.is_dir():
                for index, p in enumerate(folder.iterdir()):
                    if index >= 5000:
                        raise InventoryError('DIRECTORY_ENTRY_LIMIT')
                    if p.suffix.lower() == '.json' and not SECRET.search(p.name) and (
                        directory != 'data' or NAME.search(p.name)
                    ):
                        paths.add(str(p.relative_to(root)))
                    if len(paths) > MAX_FILES:
                        raise InventoryError('SOURCE_FILE_LIMIT')
        except FileNotFoundError:
            pass
        except (OSError, InventoryError) as exc:
            discovery_issues.append({'directory': directory, 'reason': str(exc) if isinstance(exc, InventoryError) else type(exc).__name__})
    rows = []
    total = 0
    stamps = []
    for relative in sorted(paths)[:MAX_FILES]:
        row = {'source': relative if relative in KNOWN else 'ADDITIONAL_CONFIGURATION_CANDIDATE',
               'source_path_sha256': hashlib.sha256(relative.encode()).hexdigest()}
        try:
            data, size, stamp = read(root, relative)
            total += size
            if total > MAX_TOTAL:
                raise InventoryError('TOTAL_SOURCE_SIZE_LIMIT')
            row.update(describe(data))
            row['status'] = 'FIELD_STRUCTURE_INSPECTED_NOT_VALIDATED'
            stamps.append((relative, stamp))
        except FileNotFoundError:
            row['status'] = 'MISSING'
        except Exception as exc:
            row['status'] = 'NOT_INSPECTED'
            row['reason'] = str(exc) if isinstance(exc, InventoryError) else type(exc).__name__
        rows.append(row)
        if total > MAX_TOTAL:
            discovery_issues.append({'reason': 'TOTAL_SOURCE_SIZE_LIMIT'})
            break
    stable = True
    for relative, stamp in stamps:
        try:
            stable = stable and signature(safe_path(root, relative).stat()) == stamp
        except Exception:
            stable = False
    incomplete = bool(discovery_issues) or any(r['status'] == 'NOT_INSPECTED' for r in rows)
    return {'validation': 'A24_EXISTING_POLICY_CONFIGURATION_INVENTORY_READ_ONLY',
            'status': 'INVENTORY_INCOMPLETE' if incomplete or not stable else 'INVENTORY_COMPLETE_WITHIN_SURVEYED_SCOPE',
            'sources': rows, 'discovery_issues': discovery_issues,
            'source_files_stable_during_survey': stable,
            'scope': 'KNOWN_STORES_AND_SHALLOW_JSON_CONFIGURATION_CANDIDATES_ONLY',
            'absence_is_not_proof_no_policy_exists_elsewhere': True,
            'planning_strategy_is_not_numeric_risk_limit': True,
            'execution_budget_is_not_risk_liquidity_or_concentration_policy': True,
            'financial_values_exported': False, 'identifiers_exported': False,
            'policy_values_exported': False, 'policy_validity_certified': False,
            'project_mutation': False, 'training_requested': False,
            'network_requests': 0, 'services_restarted': False,
            'automatic_execution_authorized': False,
            'canonical_publication_authorized': False}


def save(root, output):
    root = Path(root).expanduser().resolve(strict=True)
    output = Path(output).expanduser().resolve(strict=True)
    if output.is_relative_to(root):
        raise InventoryError('OUTPUT_MUST_BE_OUTSIDE_PROJECT')
    report = inventory(root)
    # Filename chosen by us; exclusive open preserves all existing files.
    import uuid
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    path = output / ('PORQUINHO_A24_CONFIGURACOES_POLITICAS_' + stamp + '_' + uuid.uuid4().hex[:8] + '.json')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    return path, report


if __name__ == '__main__':
    import sys
    try:
        path, report = save(sys.argv[1], sys.argv[2])
        print(json.dumps({k: v for k, v in report.items() if k != 'sources'}, ensure_ascii=False, indent=2))
        print('RELATORIO_PARA_COMPARTILHAR=' + str(path))
        print('Projeto preservado. Relatório contém apenas contagens de campos, sem valores de políticas ou dados financeiros.')
    except Exception as exc:
        raise SystemExit('INVENTARIO_NAO_CONCLUIDO:' + (str(exc) if isinstance(exc, InventoryError) else type(exc).__name__))

POLICY_INVENTORY_PY
