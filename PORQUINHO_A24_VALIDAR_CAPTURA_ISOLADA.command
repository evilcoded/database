#!/bin/bash
set -euo pipefail
umask 077
ROOT="${PORQUINHO_ROOT:-$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2}"
PYTHON_BIN="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON_BIN="$ROOT/.venv/bin/python"; fi
"$PYTHON_BIN" -I -B - "$ROOT" <<'A24_ISOLATED_TEST_PY'
import sys
if sys.version_info < (3,10):raise SystemExit('Python 3.10+ necessário.')
"""Replay a real local episode in disposable storage; never live backfill."""
import hashlib,json,os,re,socket,subprocess,sys,tempfile
from pathlib import Path
from datetime import datetime,timedelta,timezone


EXPECTED = {'brain/__init__.py': 'b712772a4999d2207e73fb20ad8eb6ad182ff9b2ea49b1f2ea404205badff721', 'brain/prospective_buy_forecast.py': 'b6d90078e45c57f60a1dfbebf39e87bac544f5bb2795cdc49e8780936eb3ab82', 'brain/prospective_buy_forecast_store.py': 'b0377cb8a25169d07090d17d59eadb640c0f391e45db58fa89cb4d0b4e6394eb', 'brain/prospective_buy_forecast_live_hook.py': 'eec4dd4aa6e5fb95463ab0de5318fac8319c359e82b6fc1d91fa4d4b590b6467'}


def read(root,path):
    if path.is_symlink() or not path.resolve().is_relative_to(root):raise ValueError('SOURCE_PATH_UNSUPPORTED')
    if path.stat().st_size>4*1024*1024:raise ValueError('SOURCE_TOO_LARGE')
    value=json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value,dict):raise ValueError('SOURCE_MAPPING_REQUIRED')
    return value


def digest(record,key,ensure_ascii=True):
    body={k:v for k,v in record.items() if k!=key}
    return hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=ensure_ascii).encode()).hexdigest()


def stamp(value):
    d=datetime.fromisoformat(str(value).replace('Z','+00:00'))
    if d.tzinfo is None:raise ValueError('EXPLICIT_TIMEZONE_REQUIRED')
    return d.astimezone(timezone.utc)


def main(root):
    root=Path(root).expanduser().resolve(strict=True)
    for rel,expected in EXPECTED.items():
        p=root/rel
        if p.is_symlink() or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
            raise RuntimeError('INSTALLED_SOURCE_HASH_MISMATCH:'+rel)
    def guard(event,args):
        if event in ('socket.connect','socket.bind','subprocess.Popen','os.system','os.exec','os.fork','os.posix_spawn'):
            raise PermissionError('ISOLATED_TEST_NETWORK_OR_PROCESS_DENIED')
        if event=='open':
            path,mode,flags=args
            writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            if writing and isinstance(path,(str,bytes,os.PathLike)) and Path(os.fsdecode(path)).resolve().is_relative_to(root):
                raise PermissionError('LIVE_PROJECT_WRITE_DENIED')
        if event in ('os.remove','os.rename','os.rmdir','os.mkdir','os.chmod','os.chown','os.truncate','os.link','os.symlink','os.utime'):
            for value in args:
                if isinstance(value,(str,bytes,os.PathLike)) and Path(os.fsdecode(value)).resolve().is_relative_to(root):
                    raise PermissionError('LIVE_PROJECT_MUTATION_DENIED')
    sys.addaudithook(guard)
    sys.path.insert(0,str(root))
    from brain.prospective_buy_forecast_live_hook import run,BOUNDARY
    from brain.prospective_buy_forecast_store import OUTDIR
    directory=root/'data/brain_experimental_episodes'
    if directory.is_symlink():raise RuntimeError('SOURCE_DIRECTORY_SYMLINK')
    paths=sorted(p for p in directory.glob('*.json') if re.fullmatch('[0-9a-f]{64}',p.stem))
    if len(paths)>20000:raise RuntimeError('SOURCE_POPULATION_TOO_LARGE')
    selected=None;rejections=0
    for path in paths:
        try:
            ep=read(root,path)
            if ep.get('brain_action')!='COMPRE':continue
            if ep.get('schema')!='porquinho.brain-experimental-episode/1.0':raise ValueError('EPISODE_SCHEMA')
            if ep.get('episode_id')!=path.stem or ep.get('episode_sha256')!=digest(ep,'episode_sha256'):raise ValueError('EPISODE_DIGEST')
            oid=ep.get('first_observation_id')
            if not isinstance(oid,str) or not re.fullmatch('[0-9a-f]{64}',oid):raise ValueError('OBSERVATION_ID')
            source=root/'data/brain_experimental_journal'/(oid+'.json');obs=read(root,source)
            if (obs.get('observation_id')!=oid or obs.get('record_sha256')!=digest(obs,'record_sha256',False)
                    or obs.get('schema')!='porquinho.brain-experimental-observation/1.0'
                    or obs.get('asset')!=ep.get('asset') or obs.get('brain_action')!='COMPRE'
                    or stamp(obs.get('observed_at'))!=stamp(ep.get('started_at'))):raise ValueError('SOURCE_BINDING')
            selected=(path,source,ep,obs);break
        except (ValueError,TypeError,OSError,KeyError):rejections+=1
    if selected is None:
        print(json.dumps({'validation':'A24_ISOLATED_REPLAY_NOT_LIVE_CAPTURE',
                          'status':'NO_VERIFIABLE_LOCAL_BUY_EPISODE','rejected_candidates':rejections,
                          'test_writes_to_live_project':False},indent=2))
        raise SystemExit(1)
    ep_path,obs_path,ep,obs=selected
    originals={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ep_path,obs_path)}
    summary={'schema':'porquinho.brain-experimental-episodes-summary/1.0'}
    with tempfile.TemporaryDirectory(prefix='porquinho_a24_isolated_capture_') as temp:
        isolated=Path(temp).resolve()
        if isolated.is_relative_to(root):raise RuntimeError('TEST_DIRECTORY_INSIDE_PROJECT')
        for rel,value in [('data/brain_experimental_episodes/'+ep_path.name,ep),
                          ('data/brain_experimental_journal/'+obs_path.name,obs),
                          (BOUNDARY,{'historical_backfill_allowed':False,'preexisting_episode_ids':[]})]:
            p=isolated/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value))
        # Use the original observation time only in this isolated replay. The
        # records created here are tests and are deleted with the temp directory.
        a=run(isolated,summary,'ISOLATED_REPLAY_TEST_ONLY',observed_at=ep['started_at'])
        folder=isolated/OUTDIR
        files=list(folder.glob('*.json'))
        captured={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        b=run(isolated,summary,'ISOLATED_REPLAY_TEST_ONLY',observed_at=ep['started_at'])
        after_repeat={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.json')}
        later=(stamp(ep['started_at'])+timedelta(seconds=1)).isoformat()
        c=run(isolated,summary,'LATER_TEST_OBSERVATION',observed_at=later)
        (isolated/BOUNDARY).write_text(json.dumps({'historical_backfill_allowed':False,'preexisting_episode_ids':[ep['episode_id']]}))
        d=run(isolated,summary,'ISOLATED_REPLAY_TEST_ONLY',observed_at=ep['started_at'])
        horizons=[];cold=True;no_authority=True
        for p in files:
            value=json.loads(p.read_text());f=value['forecast'];horizons.append(f['horizon_days'])
            cold=cold and f.get('forecast_probability') is None
            no_authority=no_authority and f.get('execution_authorized') is False and f.get('automatic_promotion') is False
        checks={
            'real_source_copy_captured_four_horizons':a['state']=='CAPTURE_CHECKED' and a['created']==4 and sorted(horizons)==[30,60,90,180],
            'repeat_is_idempotent':b['state']=='CAPTURE_CHECKED' and b['created']==0 and b['existing']==4 and captured==after_repeat,
            'later_observation_cannot_backfill':c['state']=='CAPTURE_CHECKED' and c['created']==0 and c['skipped_noncurrent_episodes']==1,
            'historical_boundary_excludes_episode':d['state']=='CAPTURE_CHECKED' and d['created']==0 and d['existing']==0,
            'no_probability_fabricated':cold,
            'no_financial_authority_created':no_authority,
            'original_episode_and_observation_unchanged':all(hashlib.sha256(p.read_bytes()).hexdigest()==v for p,v in originals.items())}
    report={'validation':'A24_ISOLATED_REPLAY_NOT_LIVE_CAPTURE',
            'status':'PASSED' if all(checks.values()) else 'FAILED',
            'source':'VERIFIED_LOCAL_EPISODE_AND_FIRST_OBSERVATION_COPIED_TO_TEMP',
            'checks':checks,'temporary_test_records_removed':True,
            'hook_results':{name:{k:value.get(k) for k in
                ('state','created','existing','skipped_noncurrent_episodes','sanitized_error_count','errors')}
                for name,value in [('initial',a),('repeat',b),('later_observation',c),('historical_boundary',d)]},
            'test_writes_to_live_project':False,'services_restarted':False,
            'real_prospective_capture_proven':False,'model_validation_proven':False,
            'canonical_publication_authorized':False}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':
    try:main(sys.argv[1])
    except Exception as exc:
        print(json.dumps({'status':'TEST_BLOCKED','error_type':type(exc).__name__,
                          'reason':str(exc) if isinstance(exc,RuntimeError) else 'SOURCE_OR_TEST_PRECONDITION_FAILED'},indent=2))
        raise SystemExit(1)

A24_ISOLATED_TEST_PY
