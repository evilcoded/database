#!/bin/bash
# macOS Bash 3.2; standalone, read-only preflight.
set -euo pipefail
umask 077
ROOT="${PORQUINHO_ROOT:-$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2}"
PYTHON_BIN="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON_BIN="$ROOT/.venv/bin/python"; fi
"$PYTHON_BIN" -I -B - "$ROOT" <<'PREFLIGHT_PY'
import sys
if sys.version_info < (3,10):raise SystemExit('Python 3.10+ necessário; projeto não alterado.')
"""Read-only A24 preflight. Never imports application modules or creates evidence."""
import ast
import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

HORIZONS = (30, 60, 90, 180)
MAX_BYTES = 32 * 1024 * 1024
MAX_FILES = 20000


def code(value):
    return value if isinstance(value, str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_.:-]{0,119}', value) else 'UNKNOWN'


def instant(value):
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return parsed.astimezone(timezone.utc) if parsed.tzinfo else None
    except (TypeError, ValueError, OverflowError):
        return None


def local(root, rel):
    path = root / rel
    if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
        raise ValueError('SYMLINK_SOURCE_REJECTED')
    if not path.resolve().is_relative_to(root):
        raise ValueError('SOURCE_OUTSIDE_PROJECT')
    return path


def read_json(root, rel):
    path = local(root, rel)
    if not path.is_file():
        return None
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('SOURCE_TOO_LARGE')
    return json.loads(path.read_text(encoding='utf-8'))


def json_records(root, rel):
    directory = local(root, rel)
    if not directory.exists():
        return [], {'status': 'MISSING', 'file_count': 0}
    if not directory.is_dir():
        raise ValueError('SOURCE_DIRECTORY_REQUIRED')
    paths = sorted(directory.glob('*.json'))
    if len(paths) > MAX_FILES:
        raise ValueError('TOO_MANY_SOURCE_FILES')
    rows = []
    total = 0
    for path in paths:
        if path.name in ('index.json', 'summary.json', 'outcome_contract.json', 'outcomes_latest.json'):
            continue
        local(root, path.relative_to(root))
        total += path.stat().st_size
        if total > 128 * 1024 * 1024:
            raise ValueError('SOURCE_POPULATION_TOO_LARGE')
        value = read_json(root, path.relative_to(root))
        if not isinstance(value, dict):
            raise ValueError('SOURCE_RECORD_MAPPING_REQUIRED')
        rows.append(value)
    return rows, {'status': 'PRESENT' if rows else 'EMPTY', 'file_count': len(rows)}


def horizon_rows(episode):
    rows = episode.get('horizons')
    if isinstance(rows, list):
        return [(x.get('horizon_days'), x) for x in rows if isinstance(x, dict)]
    if isinstance(rows, dict):
        return [(k, v) for k, v in rows.items() if isinstance(v, dict)]
    return []


def summarize_maturity(episodes, now):
    result = {str(h): Counter() for h in HORIZONS}
    malformed = duplicate = 0
    other = Counter()
    for episode in episodes:
        if not isinstance(episode, dict):
            malformed += 1
            continue
        seen = set()
        for raw_h, row in horizon_rows(episode):
            try:
                if isinstance(raw_h, bool): raise ValueError()
                h = int(raw_h)
                if str(h) != str(raw_h): raise ValueError()
            except (ValueError, TypeError):
                malformed += 1
                continue
            if h in seen:
                duplicate += 1
            seen.add(h)
            if h not in HORIZONS:
                other[str(h)] += 1
                continue
            counts = result[str(h)]
            counts['records'] += 1
            counts['stored_status_' + code(row.get('status'))] += 1
            due = instant(row.get('due_at'))
            if due is None:
                counts['due_time_unknown'] += 1
            elif now < due:
                counts['calendar_not_due'] += 1
            else:
                counts['calendar_due'] += 1
                if row.get('status') in ('PENDING', 'NOT_MATURED'):
                    counts['calendar_due_but_stored_pending'] += 1
            if row.get('status') == 'MATURED':
                counts['stored_matured'] += 1
                # An explicit zero is present; a missing number is not zero.
                present = row.get('return_pct') is not None
                if 'assets' in row:
                    assets = row.get('assets')
                    present = isinstance(assets, list) and bool(assets) and all(
                        isinstance(a, dict) and a.get('return_pct') is not None for a in assets)
                counts['matured_with_return_fields_present' if present else 'matured_without_return_fields'] += 1
    return {'by_horizon_days': {k: dict(v) for k, v in result.items()},
            'other_reported_horizons': dict(other), 'malformed_horizon_records': malformed,
            'duplicate_episode_horizons': duplicate,
            'semantics': 'STORED_DESCRIPTIVE_STATUS_AND_CALENDAR_ONLY_NOT_VALIDATED_FORECASTS'}


def coverage(rows):
    rows = [x for x in rows if isinstance(x, dict)]
    return {'row_count': len(rows), **{
        field + '_present': sum(isinstance(x.get(field), str) and bool(x[field].strip()) for x in rows)
        for field in ('instrument_id', 'canonical_instrument_id', 'account_id', 'currency', 'quote_currency')
    }, 'eur_named_field_count': len({k for x in rows for k in x if isinstance(k, str) and k.lower().endswith('_eur')})}


def journal_summary(root, rel):
    path = local(root, rel)
    if not path.is_file():
        return {'status': 'MISSING', 'record_count': 0}
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('JOURNAL_TOO_LARGE')
    previous = 'GENESIS'; records = []; dates = []; states = Counter()
    with path.open(encoding='utf-8') as stream:
        for n, line in enumerate(stream, 1):
            if n > 200000: raise ValueError('JOURNAL_TOO_MANY_RECORDS')
            if not line.endswith('\n'): raise ValueError('PARTIAL_JOURNAL_LINE')
            wrapper = json.loads(line); body = wrapper.get('body')
            if not isinstance(body, dict): raise ValueError('JOURNAL_BODY_REQUIRED')
            canonical = json.dumps(body, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
            digest = hashlib.sha256((previous + '|' + canonical).encode()).hexdigest()
            if wrapper.get('previous_hash') != previous or wrapper.get('hash') != digest:
                raise ValueError('JOURNAL_CHAIN_INVALID')
            previous = digest; records.append(body)
            states[code(body.get('identity_status'))] += 1
            stamp = instant(body.get('issued_at'))
            if stamp: dates.append(stamp)
    return {'status': 'LOCAL_CHAIN_VERIFIED_NOT_INDEPENDENT_ATTESTATION',
            'record_count': len(records), 'coverage': coverage(records),
            'identity_status_counts': dict(states),
            'first_issued_at': min(dates).isoformat() if dates else None,
            'last_issued_at': max(dates).isoformat() if dates else None,
            'independent_archive_verified': False}


def source_summary(root, rel):
    path = local(root, rel)
    if not path.is_file(): return {'status': 'MISSING'}
    if path.stat().st_size > MAX_BYTES: raise ValueError('SOURCE_TOO_LARGE')
    content = path.read_bytes(); tree = ast.parse(content, filename=rel)
    fields = set(); horizons = {}; hooks = set(); constants = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*_eur', node.value, flags=re.I): fields.add(node.value)
        if isinstance(node, ast.ImportFrom) and node.module and (
                'prospective' in node.module or 'universal_runtime_composition' in node.module or 'p35' in node.module):
            hooks.add(node.module)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('HORIZONS', 'ALLOWED_HORIZONS', 'SUPPORTED_HORIZONS'):
                    try:
                        v = ast.literal_eval(node.value)
                        if isinstance(v, (list, tuple)) and all(type(x) is int for x in v): horizons[target.id] = list(v)
                    except (ValueError, TypeError): pass
                if isinstance(target, ast.Name) and target.id in ('MODEL_STATE', 'ROLE', 'AUTHORITY'):
                    try: constants[target.id] = code(ast.literal_eval(node.value))
                    except (ValueError, TypeError): pass
    return {'status': 'PARSED_NOT_IMPORTED', 'sha256': hashlib.sha256(content).hexdigest(),
            'eur_named_contract_fields': sorted(fields), 'declared_horizons': horizons,
            'imported_prospective_hooks': sorted(hooks), 'declared_constants': constants}


def inspect(root, now=None):
    root = Path(root).resolve(strict=True); now = now or datetime.now(timezone.utc)
    report = {'schema': 'PORQUINHO_A24_GLOBAL_MATURITY_PREFLIGHT_V1',
              'as_of_utc': now.isoformat(), 'project_read_only': True,
              'services_restarted': False, 'training_performed': False,
              'financial_operations': False, 'issues': [], 'sections': {}}
    sections = report['sections']
    def section(name, fn):
        try: sections[name] = fn()
        except Exception as exc:
            reason = str(exc) if isinstance(exc, ValueError) and re.fullmatch('[A-Z_]{1,80}', str(exc)) else type(exc).__name__
            sections[name] = {'status': 'UNREADABLE_OR_UNSUPPORTED', 'reason': reason}
            report['issues'].append(name + ':' + reason)
    def episodes():
        value = read_json(root, 'data/brain_experimental_episodes/outcomes_latest.json')
        if value is None: return {'status': 'MISSING'}
        if isinstance(value, dict):
            value = next((value[k] for k in ('episodes', 'outcomes', 'episode_outcomes') if isinstance(value.get(k), list)), None)
        if not isinstance(value, list): raise ValueError('OUTCOME_LIST_REQUIRED')
        return {'status': 'PRESENT', 'episode_count': len(value), **summarize_maturity(value, now)}
    section('canonical_episode_outcomes', episodes)
    def shadow():
        journals, js = json_records(root, 'data/brain/shadow/journal')
        outcomes, os_ = json_records(root, 'data/brain/shadow/outcomes')
        schedule = {str(h): Counter() for h in HORIZONS}
        valid_stamps = []
        ids = []; invalid = 0
        for row in journals:
            cid = row.get('cycle_id')
            if isinstance(cid, str) and cid: ids.append(cid)
            else: invalid += 1
            start = instant(row.get('recorded_at'))
            if not start:
                invalid += 1; continue
            valid_stamps.append(start)
            for h in HORIZONS:
                schedule[str(h)]['calendar_due' if now >= start + timedelta(days=h) else 'calendar_not_due'] += 1
        outcome_ids = [row.get('cycle_id') for row in outcomes if isinstance(row.get('cycle_id'), str)]
        return {'journal_store': js, 'outcome_store': os_, 'invalid_journal_records': invalid,
                'duplicate_journal_cycle_ids': len(ids) - len(set(ids)),
                'duplicate_outcome_cycle_ids': len(outcome_ids) - len(set(outcome_ids)),
                'journals_without_outcome_file': len(set(ids) - set(outcome_ids)),
                'outcomes_without_journal': len(set(outcome_ids) - set(ids)),
                'oldest_recorded_at': min(valid_stamps).isoformat() if valid_stamps else None,
                'latest_recorded_at': max(valid_stamps).isoformat() if valid_stamps else None,
                'calendar_schedule_days': {k: dict(v) for k,v in schedule.items()},
                'stored_outcomes': summarize_maturity(outcomes, now),
                'semantics': 'SHADOW_CYCLES_NOT_AUTOMATICALLY_CANONICAL_DECISIONS'}
    section('longitudinal_cycles', shadow)
    def capture():
        boundary = read_json(root, 'data/brain/prospective/buy_forecasts_activation_boundary.json')
        stores = {}
        for name in ('buy_forecasts', 'buy_outcome_joins', 'buy_calibration_baselines_v2'):
            rows, status = json_records(root, 'data/brain/prospective/' + name)
            nested = [r.get('forecast') for r in rows if isinstance(r.get('forecast'), dict)]
            status.update(probabilistic_forecast_count=sum(type(x.get('forecast_probability')) in (int,float) for x in nested),
                          no_probability_count=sum(x.get('forecast_probability') is None for x in nested))
            stores[name] = status
        return {'boundary_status': 'PRESENT' if isinstance(boundary, dict) else 'MISSING_OR_INVALID',
                'historical_backfill_explicitly_forbidden': boundary.get('historical_backfill_allowed') is False if isinstance(boundary,dict) else None,
                'preexisting_episode_count': len(boundary.get('preexisting_episode_ids', [])) if isinstance(boundary,dict) and isinstance(boundary.get('preexisting_episode_ids'),list) else None,
                'stores': stores}
    section('prospective_episode_capture', capture)
    section('p35_expected_return_issuance', lambda: journal_summary(root, 'results/p35e_research_forecast_issuance.jsonl'))
    for name, rel in [('latest_snapshot', 'results/latest.json'), ('prediction_lab', 'results/prediction_lab.json')]:
        def snapshot(rel=rel):
            value = read_json(root, rel)
            if value is None: return {'status': 'MISSING'}
            if not isinstance(value,dict): raise ValueError('SNAPSHOT_MAPPING_REQUIRED')
            out = {'status': 'PRESENT', 'schema': code(value.get('schema')),
                   'generated_at': instant(value.get('timestamp', value.get('generated_at'))).isoformat() if instant(value.get('timestamp', value.get('generated_at'))) else None,
                   'eur_named_top_level_fields': sorted(k for k in value if re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*_eur',k,flags=re.I)),
                   'economic_envelope_present': 'governed_economic_alternatives' in value}
            for k in ('scores','predictions','ensemble_predictions'):
                if isinstance(value.get(k),list): out[k] = coverage(value[k])
            if isinstance(value.get('training'), dict): out['trained_flag'] = value['training'].get('trained') is True
            return out
        section(name, snapshot)
    def market_header():
        path = local(root, 'data/database/market_daily.csv')
        if not path.is_file(): return {'status':'MISSING'}
        with path.open(encoding='utf-8-sig',newline='') as f: header=next(csv.reader(f),[])
        return {'status':'HEADER_READ_ONLY', 'has_instrument_id':'instrument_id' in header,
                'has_currency':'currency' in header, 'has_quote_currency':'quote_currency' in header,
                'has_account_id':'account_id' in header,
                'eur_named_columns': sorted(k for k in header if re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*_eur',k,flags=re.I)),
                'maturity_unit_warning':'P35_USES_30_SUBSEQUENT_OBSERVATIONS_NOT_30_CALENDAR_DAYS'}
    section('market_history_contract', market_header)
    sources = ['porquinho.py','webapp/server.py','brain/prospective_buy_forecast.py',
               'brain/prospective_buy_forecast_live_hook.py','brain/prospective_buy_outcome_auto_persist.py',
               'brain/outcome_evaluation_v3898.py','brain/prospective_buy_statistical_readiness_contract.py',
               'brain/evolution/p35e_prospective_issuance.py','brain/evolution/p35f_outcome_reconciliation.py',
               'brain/evolution/prediction_lab.py','universal_portfolio/governed_forward_return_estimator.py',
               'universal_portfolio/universal_observation_bridge.py','universal_portfolio/universal_runtime_composition.py']
    sections['source_contracts'] = {}
    for rel in sources:
        try: sections['source_contracts'][rel] = source_summary(root,rel)
        except Exception as exc:
            sections['source_contracts'][rel]={'status':'UNREADABLE_OR_UNSUPPORTED','error_type':type(exc).__name__}
            report['issues'].append('source_contract_unreadable:'+rel)
    ep = sections.get('canonical_episode_outcomes',{})
    canonical = ep.get('by_horizon_days',{})
    matured = sum(canonical.get(str(h),{}).get('stored_matured',0) for h in (30,60,90))
    records = sum(canonical.get(str(h),{}).get('records',0) for h in (30,60,90))
    due_pending = sum(canonical.get(str(h),{}).get('calendar_due_but_stored_pending',0) for h in (30,60,90))
    report['findings'] = {
        'episode_30_60_90_stored_matured_horizon_count':matured if records else None,
        'episode_30_60_90_due_but_stored_pending':due_pending if records else None,
        'no_matured_cycles_claim_supported':False,
        'matured_returns_imply_model_approval':False,
        'none_in_cold_capture_implies_entire_brain_untrained':False,
        'currency_inferred_from_eur_suffix':False,
        'canonical_publication_authorized':False,
        'note':'INTERPRET_PER_TRACK_AND_HORIZON; PRESERVE_IDENTITY_AND_ORIGINAL_CURRENCY'}
    report['status'] = 'PREFLIGHT_COMPLETE' if not report['issues'] else 'PREFLIGHT_PARTIAL'
    return report


def main():
    root = Path(sys.argv[1]).expanduser().resolve(strict=True)
    if not (root/'universal_portfolio').is_dir(): raise SystemExit('Projeto Porquinho não encontrado.')
    # Deny all project mutation, network and child processes, including accidental calls.
    def guard(event,args):
        if event in ('socket.connect','socket.bind','subprocess.Popen','os.system','os.exec','os.fork','os.posix_spawn'):
            raise PermissionError('PREFLIGHT_NETWORK_OR_PROCESS_DENIED')
        if event=='open':
            path,mode,flags=args
            writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            if writing and isinstance(path,(str,bytes,os.PathLike)) and Path(os.fsdecode(path)).resolve().is_relative_to(root):
                raise PermissionError('PREFLIGHT_PROJECT_WRITE_DENIED')
        if event in ('os.remove','os.rename','os.rmdir','os.mkdir','os.chmod','os.chown','os.truncate','os.link','os.symlink','os.utime'):
            for arg in args:
                if isinstance(arg,(str,bytes,os.PathLike)) and Path(os.fsdecode(arg)).resolve().is_relative_to(root):
                    raise PermissionError('PREFLIGHT_PROJECT_MUTATION_DENIED')
    sys.addaudithook(guard)
    report=inspect(root)
    # Only the sanitized report is saved outside the project; no original data/source.
    output=Path.home()/'Downloads'
    if output.resolve().is_relative_to(root):raise SystemExit('Diretório de saída deve ficar fora do projeto.')
    output.mkdir(parents=True,exist_ok=True)
    import tempfile,zipfile
    fd, filename=tempfile.mkstemp(prefix='PORQUINHO_A24_PREFLIGHT_GLOBAL_',suffix='.zip',dir=output)
    os.close(fd)
    try:
        with zipfile.ZipFile(filename,'w',compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('PREFLIGHT_GLOBAL_MATURACAO.json',json.dumps(report,ensure_ascii=False,indent=2))
            archive.writestr('LEIA.txt','Preflight somente leitura. Relatório agregado; não contém preços, saldos, posições, previsões individuais ou fontes originais.\nMaturação descritiva não é aprovação econômica. Dias corridos e observações são unidades distintas.\n')
        with zipfile.ZipFile(filename) as archive:
            if archive.testzip() is not None:raise RuntimeError('ZIP_INTEGRITY_FAILED')
    except BaseException:
        Path(filename).unlink(missing_ok=True)
        raise
    print(json.dumps({'status':report['status'],'findings':report['findings'],'issues':report['issues']},ensure_ascii=False,indent=2))
    print('ZIP_PARA_COMPARTILHAR='+filename)
    print('Projeto preservado; nenhum ciclo, treinamento, operação financeira ou reinício executado.')

if __name__=='__main__':main()

PREFLIGHT_PY
