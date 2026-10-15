#!/bin/bash
set -euo pipefail
ROOT="${PORQUINHO_ROOT:-$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2}"
PYTHON_BIN="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON_BIN="$ROOT/.venv/bin/python"; fi
"$PYTHON_BIN" -I -B - "$ROOT" <<'A24_ORIGIN_PY'
import sys
if sys.version_info < (3,10):raise SystemExit('Python 3.10+ necessário.')
"""Read-only acquisition/binding survey. Never imports the application or binds IDs."""
import csv,hashlib,json,math,os,sys,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

CODE=('tools/fetch_history.py','tools/import_history.py','webapp/server.py',
      'universal_portfolio/universal_observation_bridge.py','universal_portfolio/universal_domain_discovery.py',
      'universal_portfolio/market_provider_identity_resolution.py','universal_portfolio/market_universe_binding_bridge.py',
      'unified/universal_instrument_catalog.py')
SOURCES=('data/universal_instrument_catalog.json','data/instruments/manual_instruments.json',
         'data/unified_br_equity_market_latest.json','results/latest.json')

def present(v):return isinstance(v,str) and bool(v) and v==v.strip()
def number(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)

def path_in(root,rel):
 p=root/rel
 if p.is_symlink() or any(a.is_symlink() for a in p.parents if a!=root.parent):raise ValueError('SYMLINK_SOURCE')
 if not p.resolve().is_relative_to(root):raise ValueError('SOURCE_OUTSIDE_ROOT')
 return p

def load(root,rel):
 p=path_in(root,rel)
 if not p.exists():return None
 if p.stat().st_size>32*1024*1024:raise ValueError('JSON_SIZE_LIMIT')
 before=p.stat();value=json.loads(p.read_text(encoding='utf-8'));after=p.stat()
 if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise ValueError('SOURCE_CHANGED_DURING_READ')
 return value

def records(value,depth=0):
 if depth>40:raise ValueError('JSON_DEPTH_LIMIT')
 if isinstance(value,dict):
  # A record may provide origin directly or through existing universe metadata.
  if 'instrument_id' in value or 'provider_id' in value:
   yield value
  for k,v in value.items():
   if k!='metadata':yield from records(v,depth+1)
 elif isinstance(value,list):
  for v in value:yield from records(v,depth+1)

def survey_source(value):
 counts=Counter();shapes=Counter();claims=[]
 for row in records(value):
  counts['candidate_records']+=1
  if counts['candidate_records']>200000:raise ValueError('CANDIDATE_LIMIT')
  meta=row.get('metadata') if isinstance(row.get('metadata'),dict) else {}
  def field(k):return row[k] if k in row else meta.get(k)
  iid=row.get('instrument_id');p=field('provider');pid=field('provider_id');quote=field('quote_currency')
  if present(iid):counts['with_instrument_id']+=1;shapes[str(len(iid.split(':')))]+=1
  if present(p) and present(pid):counts['with_explicit_provider_key']+=1
  if present(quote):counts['with_explicit_quote_currency']+=1
  # Report declarations, never accept a boolean as independent verification.
  claimed=field('provider_binding_attested') is True
  if claimed:counts['declared_provider_binding_attested']+=1
  if present(iid) and present(p) and present(pid):
   counts['complete_identity_provider_claims']+=1
   claims.append((p.lower(),pid,iid,claimed))
  if present(iid) and present(p) and present(pid) and present(quote):counts['complete_identity_origin_quote_claims']+=1
  if present(row.get('currency')) and not present(quote):counts['currency_present_without_quote_currency']+=1
 by={}
 for p,pid,iid,claim in claims:by.setdefault((p,pid),set()).add(iid)
 counts['conflicting_provider_keys']=sum(len(ids)>1 for ids in by.values())
 counts['complete_provider_claims_declaring_attestation']=sum(claim for p,pid,iid,claim in claims)
 return {'counts':dict(counts),'instrument_id_component_counts':dict(shapes)},claims

def inspect(root,now=None):
 root=Path(root).resolve(strict=True);now=time.time() if now is None else now
 out={'validation':'A24_ACQUISITION_BINDING_PREFLIGHT_READ_ONLY','status':'PREFLIGHT_COMPLETE','source_code':{},'candidate_sources':{},
      'project_mutation':False,'network_requested':False,'services_restarted':False,
      'identity_binding_created':False,'canonical_publication_authorized':False,
      'scope':'SURVEYED_PATHS_ONLY; DECLARED_ATTESTATION_IS_NOT_INDEPENDENT_VERIFICATION'}
 for rel in CODE:
  p=path_in(root,rel)
  out['source_code'][rel]={'status':'PRESENT','sha256':hashlib.sha256(p.read_bytes()).hexdigest()} if p.is_file() else {'status':'MISSING'}
 all_claims=[]
 for rel in SOURCES:
  try:
   value=load(root,rel)
   if value is None:out['candidate_sources'][rel]={'status':'MISSING'};continue
   report,claims=survey_source(value);all_claims+=claims
   out['candidate_sources'][rel]={'status':'INSPECTED_DECLARATIONS_ONLY',**report}
  except (OSError,ValueError,TypeError,RecursionError) as e:out['candidate_sources'][rel]={'status':'UNREADABLE_OR_CHANGED','error':type(e).__name__}
 by={}
 for p,pid,iid,claim in all_claims:by.setdefault((p,pid),set()).add(iid)
 out['cross_source_claims']={'distinct_provider_keys':len(by),'conflicting_provider_keys':sum(len(v)>1 for v in by.values()),
     'registry_assumed_or_created':False,'ids_reformatted':False}
 history=load(root,'brain/reports/history_fetch.json');p=path_in(root,'brain/reports/history_fetch.json')
 if history is None:out['history_refresh']={'status':'REPORT_MISSING'}
 elif isinstance(history,dict):
  scheduler=history.get('scheduler') or {};scheduler=scheduler if isinstance(scheduler,dict) else {}
  age=max(0,now-p.stat().st_mtime)
  cadence_verified=out['source_code']['webapp/server.py'].get('sha256')=='1137a8572b9db42ff8720e31b5c76cf7589d2f6a93b00ec43f77c1e50ce3ae06'
  out['history_refresh']={'status':'REPORT_PRESENT','report_age_seconds':round(age),
     'source_contract_interval_seconds':21600 if cadence_verified else None,
     'cadence_source_hash_verified':cadence_verified,'due_by_existing_mtime_gate':age>=21600 if cadence_verified else None,
     'counts':{k:history[k] for k in ('daily_added','intraday_added') if number(history.get(k))},
     'asset_report_count':len(history['assets']) if isinstance(history.get('assets'),list) else None,
     'error_count':len(history['errors']) if isinstance(history.get('errors'),list) else None,
     'processed_daily':scheduler.get('processed_daily') if number(scheduler.get('processed_daily')) else None,
     'interval_is_source_contract_not_a_forced_refresh':True}
 market=path_in(root,'data/database/market_daily.csv')
 if market.is_file():
  before=market.stat();counts=Counter();latest=None;latestcounts=Counter();n=0
  with market.open(newline='',encoding='utf-8') as f:
   reader=csv.DictReader(f);fields=set(reader.fieldnames or [])
   for row in reader:
    n+=1
    if n>2000000:raise ValueError('CSV_ROW_LIMIT')
    missing=[k for k in ('instrument_id','provider','provider_id','quote_currency') if not present(row.get(k))]
    counts.update(missing)
    try:day=datetime.strptime(row.get('date',''),'%Y-%m-%d').date()
    except (ValueError,TypeError):continue
    if latest is None or day>latest:latest=day;latestcounts=Counter()
    if day==latest:latestcounts.update(missing)
  after=market.stat();stable=(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
  out['market']={'status':'STABLE_READ' if stable else 'CHANGED_DURING_READ',
       'rows':n if stable else None,'latest_date':latest.isoformat() if latest and stable else None,
       'missing_fields':dict(counts) if stable else {},'latest_missing_fields':dict(latestcounts) if stable else {},
       'neutral_price_column_present':'price' in fields,'legacy_price_eur_column_present':'price_eur' in fields}
 else:out['market']={'status':'MISSING'}
 out['next_patch_constraints']={'no_retrospective_attribution':True,'no_symbol_binding':True,
    'quote_currency_not_account_currency':True,'preserve_identity_format':True,
    'cadence_and_new_date_gate_can_explain_unchanged_csv':True}
 return out

def main():
 root=Path(sys.argv[1]).expanduser().resolve(strict=True)
 def guard(event,args):
  if event=='open':
   mode,flags=args[1:3]
   if (isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)):raise RuntimeError('READ_ONLY_WRITE_REFUSED')
  if event in {'os.remove','os.rename','os.mkdir','os.rmdir','os.chmod','os.truncate','os.link','os.symlink','subprocess.Popen','os.system','socket.connect','socket.bind'}:raise RuntimeError('READ_ONLY_SIDE_EFFECT_REFUSED')
 sys.addaudithook(guard)
 try:result=inspect(root)
 except Exception as e:result={'validation':'A24_ACQUISITION_BINDING_PREFLIGHT_READ_ONLY','status':'FAILED_CLOSED','error':type(e).__name__,'project_mutation':False}
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

A24_ORIGIN_PY
