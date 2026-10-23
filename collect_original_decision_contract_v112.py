"""Read-only export of explicitly allowed original decision settings. Standard library only."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import math
import os
import zipfile

ROOT = Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2')
RULES = ('buy_min_promising', 'buy_min_entry', 'buy_max_risk', 'sell_structural_risk',
         'sell_max_promising', 'realize_min_pnl_pct', 'realize_max_promising',
         'realize_reversal_risk', 'realize_min_asymmetry', 'realize_risk',
         'hold_min_promising', 'hold_max_risk')
METRICS = ('promising_pct', 'entry', 'risk', 'asymmetry', 'reversal_risk',
           'opportunity', 'regime', 'momentum_quality', 'relative_strength',
           'liquidity', 'accumulation')
ACTIONS = {'COMPRE', 'VENDA', 'REALIZE', 'MANTENHA', 'ACOMPANHE'}


def number(value):
    return value if type(value) in (int, float) and math.isfinite(value) else None


def read(root, relative):
    path = root / relative
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('SYMLINK_REFUSED')
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('OUTSIDE_PROJECT')
    with path.open('rb') as stream:
        before = os.fstat(stream.fileno())
        raw = stream.read(64 * 1024 * 1024 + 1)
        after = os.fstat(stream.fileno())
    if len(raw) > 64 * 1024 * 1024:
        raise ValueError('SIZE_LIMIT')
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
        raise ValueError('CHANGED_DURING_READ')
    return raw


def collect(root):
    root = Path(root)
    out = {'schema': 'porquinho.original-decision-contract/1.0',
           'read_only': True, 'models_modified': False, 'financial_mutation': False,
           'recommendation_created': False, 'files': {}}
    parsed = {}
    for relative in ('config.json', 'results/model_params.json', 'results/latest.json'):
        try:
            raw = read(root, relative)
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError('OBJECT_REQUIRED')
            parsed[relative] = value
            # No hash of config.json: it can contain credentials.
            out['files'][relative] = {'status': 'READ'}
        except Exception as exc:
            out['files'][relative] = {'status': 'UNAVAILABLE', 'error_type': type(exc).__name__}
    cfg = parsed.get('config.json', {})
    rules = cfg.get('action_rules')
    rules = rules if isinstance(rules, dict) else {}
    sizing = cfg.get('position_sizing')
    sizing = sizing if isinstance(sizing, dict) else {}
    out['original_settings'] = {
        'action_rules': {k: number(rules.get(k)) for k in RULES},
        'max_positions': number(cfg.get('max_positions')),
        'position_sizing': {'max_position_pct': number(sizing.get('max_position_pct'))},
        'discovery_top_n': number(cfg.get('discovery_top_n')),
    }
    model = parsed.get('results/model_params.json', {})
    weights = model.get('kpi_weights')
    out['calibration'] = {
        k: model.get(k) if type(model.get(k)) is bool else None
        for k in ('trained', 'calibration_usable')}
    out['calibration']['kpi_weights'] = (
        weights if isinstance(weights, list) and len(weights) == 5
        and all(number(v) is not None for v in weights) else None)
    snap = parsed.get('results/latest.json', {})
    if isinstance(snap.get('snapshot'), dict):
        snap = snap['snapshot']
    scores = snap.get('scores')
    scores = scores if isinstance(scores, list) else []
    out['score_count'] = len(scores)
    out['scores'] = []
    counts = {}
    for row in scores[:10000]:
        if not isinstance(row, dict):
            continue
        raw_action = row.get('action')
        action = raw_action if isinstance(raw_action, str) and raw_action in ACTIONS else 'UNRECOGNIZED'
        counts[action] = counts.get(action, 0) + 1
        # No free-form identifiers, notes, arbitrary nested data or credential fields.
        out['scores'].append({'index': len(out['scores']), 'action': action,
                              **{k: number(row.get(k)) for k in METRICS}})
    out['action_counts'] = counts
    out['scores_truncated'] = len(scores) > 10000
    for relative in ('porquinho.py', 'brain/execution_intelligence.py',
                     'universal_portfolio/universal_runtime_composition.py'):
        try:
            raw = read(root, relative)
            out['files'][relative] = {'status': 'HASHED', 'sha256': hashlib.sha256(raw).hexdigest()}
        except Exception as exc:
            out['files'][relative] = {'status': 'UNAVAILABLE', 'error_type': type(exc).__name__}
    return out


def main():
    if not (ROOT / 'porquinho.py').is_file():
        raise SystemExit('PROJETO_NAO_ENCONTRADO')
    report = collect(ROOT)
    report['collected_at'] = dt.datetime.now(dt.timezone.utc).isoformat()
    downloads = Path.home() / 'Downloads'
    downloads.mkdir(exist_ok=True)
    target = downloads / ('PORQUINHO_MOTOR_ORIGINAL_V112_' + dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.zip')
    # Exclusive creation with private permissions from the first byte.
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'wb') as stream:
        with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('original_decision_contract.json', json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('ZIP_INTEGRITY_FAILED')
    print('ACOES_ORIGINAIS=' + json.dumps(report['action_counts'], ensure_ascii=False))
    print('SOMENTE_LEITURA; SEM_REDE; SEM_CICLO; SEM_ALTERACAO_FINANCEIRA_OU_DE_MODELOS')
    print('ENVIAR=' + str(target))


if __name__ == '__main__':
    main()
