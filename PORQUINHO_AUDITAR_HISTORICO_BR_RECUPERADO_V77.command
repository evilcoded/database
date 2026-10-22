#!/bin/bash
set -euo pipefail
umask 077
"$HOME/anaconda3/bin/python" -I -B - <<'PY'
import datetime as dt,hashlib,json,math,pathlib,zipfile
ROOT=pathlib.Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2').resolve(strict=True)
assert (ROOT/'webapp/server.py').is_file(),'PROJETO_NAO_LOCALIZADO'
report={'schema':'porquinho.recovered-br-history-audit/1.0','collected_at':dt.datetime.now(dt.timezone.utc).isoformat(),'files':[],'network_requests':0,'model_execution_performed':False,'project_mutation':False}
metadata=('schema','version','status','source','provider','provider_id','instrument_id','currency','quote_currency','usedRange','usedInterval','requestedRange','reason','generated_at','updated_at','method')
paths={'data/equities/historical/daily/ohlcv.json','data/equities/price_history.json','data/equities/learning_latest.json','data/equities/decision_latest.json','data/br_equity_brain/history_refresh_latest.json','data/br_equity_brain_experimental_latest.json'}
# Search only known backup locations and exact historical file paths; no disk-wide scan.
for pattern in ('patch_backups/*/data/equities/historical/daily/ohlcv.json','recovery_backups/*/data/equities/historical/daily/ohlcv.json','.patch_backups/*/data/equities/historical/daily/ohlcv.json'):
 for p in ROOT.glob(pattern):
  paths.add(str(p.relative_to(ROOT)))
  if len(paths)>64:raise SystemExit('HISTORY_CANDIDATE_LIMIT')

def number(value):
 if isinstance(value,bool):return False
 try:return math.isfinite(float(value)) and float(value)>0
 except (ValueError,TypeError,OverflowError):return False

def day(value):
 try:
  if isinstance(value,(float,int)) and not isinstance(value,bool):return dt.datetime.fromtimestamp(value,dt.timezone.utc).date().isoformat()
  stamp=dt.datetime.fromisoformat(str(value).replace('Z','+00:00'));return stamp.date().isoformat()
 except (ValueError,TypeError,OverflowError,OSError):return None

size_total=0
for rel in sorted(paths):
 p=ROOT/rel;row={'path':rel};report['files'].append(row)
 if p.is_symlink() or any(x.is_symlink() for x in p.parents) or ROOT not in p.resolve().parents:row['read_status']='SYMLINK_OR_OUTSIDE_PROJECT';continue
 if not p.exists():row['read_status']='MISSING';continue
 try:
  stat=p.stat();size_total+=stat.st_size
  if stat.st_size>32*1024*1024 or size_total>64*1024*1024:row['read_status']='SIZE_LIMIT';continue
  raw=p.read_bytes();obj=json.loads(raw)
  if (p.stat().st_size,p.stat().st_mtime_ns)!=(stat.st_size,stat.st_mtime_ns):row['read_status']='CHANGED_DURING_READ';continue
  row.update(read_status='READ',sha256=hashlib.sha256(raw).hexdigest())
  if not isinstance(obj,dict):row['root_type']=type(obj).__name__;continue
  row['metadata']={k:obj[k] for k in metadata if k in obj and isinstance(obj[k],(str,int,float,bool,type(None)))}
  series=obj.get('series');row['series_shape']=type(series).__name__
  if isinstance(series,dict):
   summaries=[]
   for key,payload in sorted(series.items()):
    if not isinstance(payload,dict):continue
    points=payload.get('points')
    if not isinstance(points,list):continue
    valid=[r for r in points if isinstance(r,dict) and day(r.get('date')) and number(r.get('close'))]
    dates=sorted({day(r['date']) for r in valid})
    summaries.append({'stored_key':key,'point_count':len(points),'valid_close_point_count':len(valid),'unique_daily_close_count':len(dates),'first_date':dates[0] if dates else None,'last_date':dates[-1] if dates else None,'adjusted_close_present_count':sum(number(r.get('adjustedClose')) for r in valid),'volume_present_count':sum(r.get('volume') is not None for r in valid),'metadata':{k:payload[k] for k in metadata if k in payload and isinstance(payload[k],(str,int,float,bool,type(None)))},'historical_identity_attested_by_audit':False,'historical_currency_attested_by_audit':False})
   row['series']=summaries
  # Report structure/counts only for legacy result stores, never weights or financial amounts.
  row['collection_counts']={k:len(v) for k,v in obj.items() if isinstance(v,(list,dict)) and k in ('assets','evaluations','models','results','symbols','episodes')}
 except Exception as exc:row.update(read_status='READ_FAILED',error_type=type(exc).__name__)
output=pathlib.Path.home()/'Downloads'/('PORQUINHO_HISTORICO_BR_RECUPERADO_V77_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip')
with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED) as z:z.writestr('historico_recuperado.json',json.dumps(report,ensure_ascii=False,indent=2))
for r in report['files']:
 print(r['read_status'],r['path'],'| séries:',len(r.get('series',[])))
print('SOMENTE_LEITURA; SEM_REDE; HISTORICOS_E_MODELOS_NAO_ALTERADOS')
print('ENVIAR='+str(output))
PY
