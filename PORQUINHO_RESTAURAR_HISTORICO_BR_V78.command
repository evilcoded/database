#!/bin/bash
set -euo pipefail
umask 077
"$HOME/anaconda3/bin/python" -I -B - "$@" <<'PY'
import datetime as dt,hashlib,json,math,os,pathlib,sys,tempfile,zipfile
from decimal import Decimal
ROOT=pathlib.Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2').resolve(strict=True)
assert (ROOT/'webapp/server.py').is_file(),'PROJETO_NAO_LOCALIZADO'
assert len(sys.argv)==3,'USE_CAMINHO_DO_OHLCV_E_SHA256'
source=pathlib.Path(sys.argv[1]).expanduser()
assert source.is_file() and not source.is_symlink(),'ARQUIVO_RECUPERADO_NAO_LOCALIZADO_OU_SYMLINK'
assert source.stat().st_size<=32*1024*1024,'SOURCE_SIZE_LIMIT'
raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
assert sha==sys.argv[2],'HASH_DO_ARQUIVO_RECUPERADO_DIVERGENTE'
obj=json.loads(raw)
assert obj.get('schema')=='porquinho.equity-historical/1.0' and isinstance(obj.get('series'),dict),'HISTORY_SCHEMA_INVALID'
report={'schema':'porquinho.recovered-br-history-restore/1.0','recovered_source_sha256':sha,'restored_at':dt.datetime.now(dt.timezone.utc).isoformat(),'series':[],'overlap_checks':[],'issues':[],'automatic_merge_performed':False,'financial_mutation':False,'model_execution_performed':False,'network_requests':0}
lookup={}
for symbol,payload in sorted(obj['series'].items()):
 assert isinstance(payload,dict) and isinstance(payload.get('points'),list),'HISTORY_SERIES_INVALID'
 days={};stamps=set()
 for row in payload['points']:
  assert isinstance(row,dict),'HISTORY_POINT_INVALID'
  at=row.get('date');assert isinstance(at,(int,float)) and not isinstance(at,bool) and math.isfinite(at),'HISTORY_DATE_INVALID'
  day=dt.datetime.fromtimestamp(at,dt.timezone.utc).date().isoformat()
  assert at not in stamps and day not in days,'HISTORY_DUPLICATE_DAY'
  stamps.add(at)
  vals=[row.get(k) for k in ('open','high','low','close')]
  assert all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and v>0 for v in vals),'HISTORY_OHLC_INVALID'
  o,h,l,c=vals;assert h>=max(o,l,c) and l<=min(o,h,c),'HISTORY_OHLC_INCONSISTENT'
  days[day]=Decimal(str(c))
 lookup[symbol]=days;ordered=sorted(days)
 report['series'].append({'stored_key':symbol,'observation_count':len(days),'first_date':ordered[0] if ordered else None,'last_date':ordered[-1] if ordered else None,'source':payload.get('source'),'historical_currency_explicit':payload.get('currency') or payload.get('quote_currency'),'historical_identity_explicit':payload.get('instrument_id'),'historical_identity_attested_by_restore':False,'historical_currency_attested_by_restore':False})

def safe(rel):
 p=ROOT/rel
 assert not any(v.is_symlink() for v in [p,*p.parents]),'SYMLINK_REFUSED'
 assert ROOT in p.resolve().parents,'OUTSIDE_PROJECT'
 return p

def store_exact(path,body):
 path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():
  assert path.is_file(),'DESTINATION_NOT_FILE'
  return 'IDENTICAL_PRESERVED' if path.read_bytes()==body else 'DIFFERENT_PRESERVED'
 fd,tmp=tempfile.mkstemp(prefix='.recovered-history-',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as stream:stream.write(body);stream.flush();os.fsync(stream.fileno())
  try:os.link(tmp,path);return 'CREATED_EXACT_COPY'
  except FileExistsError:return 'IDENTICAL_PRESERVED' if path.read_bytes()==body else 'DIFFERENT_PRESERVED'
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
archive=safe('data/recovered_market_sources_a24/'+sha+'/ohlcv.json')
assert store_exact(archive,raw)!='DIFFERENT_PRESERVED','RECOVERY_ARCHIVE_CONFLICT'
target=safe('data/equities/historical/daily/ohlcv.json')
report['restoration_status']=store_exact(target,raw)
report['original_source_bytes_preserved']=source.read_bytes()==raw
# Compare raw daily closes only; matching values are not historical identity/FX attestation.
try:
 sys.path.insert(0,str(ROOT))
 from universal_portfolio import global_history_source_a24 as history
 directory=safe(history.STORE+'/bundles');paths=sorted(directory.glob('*/*.json')) if directory.exists() else []
 assert len(paths)<=4096 and sum(p.stat().st_size for p in paths)<=64*1024*1024,'HISTORY_READ_LIMIT'
 latest={}
 for path in paths:
  p=safe(str(path.relative_to(ROOT)));body=history.validate_bundle(history.read_sealed(p),p)
  b=body['binding'];symbol=b['provider_id']
  if b['provider'].lower()!='brapi' or symbol not in lookup or obj['series'][symbol].get('source')!='brapi.dev':continue
  iid=b['instrument_id'];old=latest.get(iid)
  if old is None or body['fetched_at']>old['fetched_at']:latest[iid]=body
 for iid,body in sorted(latest.items()):
  b=body['binding'];past=lookup[b['provider_id']];recent={r['observation_date']:Decimal(r['price']) for r in body['observations']}
  common=sorted(set(past)&set(recent));different=[day for day in common if past[day]!=recent[day]]
  report['overlap_checks'].append({'instrument_id':iid,'provider_id':b['provider_id'],'current_quote_currency':b['quote_currency'],'historical_currency_attested':False,'same_provider_namespace_claim_only':True,'common_day_count':len(common),'equal_close_day_count':len(common)-len(different),'different_close_day_count':len(different),'first_difference_dates':different[:5],'first_common_date':common[0] if common else None,'last_common_date':common[-1] if common else None,'automatic_merge_authorized':False})
except Exception as exc:report['issues'].append({'overlap_inspection_error_type':type(exc).__name__})
manifest=safe('data/recovered_market_sources_a24/'+sha+'/recovery_manifest.json')
if not manifest.exists():store_exact(manifest,(json.dumps({'schema':report['schema'],'source_sha256':sha,'source_kind':'USER_SUPPLIED_RECOVERED_COPY','independent_attestation':False,'original_schema':obj['schema']},sort_keys=True)+'\n').encode())
output=pathlib.Path.home()/'Downloads'/('PORQUINHO_RESTAURACAO_BR_V78_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip')
with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED) as z:z.writestr('restauracao.json',json.dumps(report,ensure_ascii=False,indent=2))
print('RESTAURACAO:',report['restoration_status'])
print('SERIES:',len(report['series']),'OBSERVACOES:',sum(r['observation_count'] for r in report['series']))
print('COMPARACOES_DE_SOBREPOSICAO:',len(report['overlap_checks']))
print('MODELOS_NAO_EXECUTADOS; SEM_REDE; SEM_UNIAO_AUTOMATICA')
print('ENVIAR='+str(output))
PY
