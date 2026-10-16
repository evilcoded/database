#!/bin/bash
# Verify confirmed provider pairs and register research bindings only.
set -euo pipefail
umask 077
ROOT="${PORQUINHO_ROOT:-$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2}"
PYTHON_BIN="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then PYTHON_BIN="$ROOT/.venv/bin/python"; fi
"$PYTHON_BIN" -I -B - "$ROOT" "$@" <<'A24_VERIFIED_SOURCE'
import sys
if sys.version_info<(3,10):raise SystemExit('Python 3.10+ necessário.')
"""Verify provider quotes, then append only explicitly confirmed research bindings."""
import datetime as dt,hashlib,json,re,sys
from decimal import Decimal
from pathlib import Path
SCHEMA='porquinho.confirmed-source-pairs-a24/1.0'
class VerificationError(ValueError):pass

def confirmed_pairs(document):
 if not isinstance(document,dict) or set(document)!={'schema','confirmed','provider','instruments'} or document.get('schema')!=SCHEMA or document.get('confirmed') is not True:raise VerificationError('EXPLICIT_MAPPING_CONFIRMATION_REQUIRED')
 if document['provider']!='CoinGecko':raise VerificationError('PROVIDER_ADAPTER_NOT_IMPLEMENTED')
 items=document['instruments']
 if not isinstance(items,list) or not 1<=len(items)<=50:raise VerificationError('CONFIRMATION_BATCH_LIMIT')
 pairs=[];keys=set();ids=set()
 for row in items:
  if not isinstance(row,dict) or set(row)!={'instrument_id','provider_id','quote_currencies'}:raise VerificationError('CONFIRMED_MAPPING_FIELDS_REQUIRED')
  iid,pid,quotes=(row[k] for k in ('instrument_id','provider_id','quote_currencies'))
  if not isinstance(iid,str) or not iid or iid!=iid.strip() or iid in ids:raise VerificationError('CONFIRMED_IDENTITY_INVALID_OR_DUPLICATED')
  ids.add(iid)
  if not isinstance(pid,str) or not re.fullmatch('[a-z0-9][a-z0-9_-]{0,127}',pid):raise VerificationError('PROVIDER_ID_INVALID')
  if not isinstance(quotes,list) or not 1<=len(quotes)<=16 or len(set(quotes))!=len(quotes):raise VerificationError('QUOTE_LIST_INVALID')
  for q in quotes:
   if not isinstance(q,str) or not q.isascii() or not q.isalpha() or not q.isupper() or len(q)>16:raise VerificationError('QUOTE_CODE_INVALID')
   if (pid,q) in keys:raise VerificationError('PROVIDER_QUOTE_CONFIRMED_FOR_MULTIPLE_IDENTITIES')
   keys.add((pid,q));pairs.append((iid,pid,q))
 if len(pairs)>100:raise VerificationError('CONFIRMATION_PAIR_LIMIT')
 return pairs

def positive(value):
 if isinstance(value,bool) or not isinstance(value,(int,float,Decimal)):return False
 try:v=Decimal(str(value));return v.is_finite() and v>0
 except Exception:return False

def verify_and_apply(root,document,*,transport=None,now=None,queue_reader=None):
 root=Path(root).resolve(strict=True);sys.path.insert(0,str(root))
 from universal_portfolio.explicit_market_bindings_a24 import SCHEMA as BS,load,digest,canonical
 from tools.market_provider_bindings_a24 import apply
 from tools.review_funded_bindings_a24 import current
 pairs=confirmed_pairs(document);queue_reader=queue_reader or current
 queue=queue_reader(root);registry=load(root)
 if queue.get('registry_digest')!=digest(registry):raise VerificationError('REGISTRY_CHANGED_BEFORE_REVIEW')
 cases={(r['instrument_id'],r['quote_currency']):r for r in queue['rows']}
 old=registry['bindings'];pending=[];present=0
 for iid,pid,q in pairs:
  case=cases.get((iid,q))
  if not case:raise VerificationError('CONFIRMED_PAIR_NOT_IN_CURRENT_FUNDED_DEMAND')
  same=[b for b in old if b['instrument_id']==iid and b['quote_currency']==q]
  if same:
   if len(same)!=1 or same[0]['provider'].lower()!='coingecko' or same[0]['provider_id']!=pid:raise VerificationError('EXISTING_SOURCE_CONFLICT_NOT_REWRITTEN')
   present+=1;continue
  if case['status']!='AWAITING_CASE_REVIEW':raise VerificationError('IDENTITY_OR_CASE_NOT_ELIGIBLE')
  pending.append((iid,pid,q))
 base={'confirmed_pair_count':len(pairs),'existing_confirmed_pair_count':present,'financial_mutation':False,'historical_records_relabelled':False,
       'training_requested':False,'services_restarted':False,'automatic_execution_authorized':False,'canonical_publication_authorized':False}
 if not pending:return {**base,'status':'CONFIRMED_BINDINGS_ALREADY_PRESENT','new_binding_count':0,'network_requests':0}
 owned=transport is None;calls=0
 try:
  if owned:
   from universal_portfolio.research_quote_acquisition_a24 import CoinGeckoTransport
   transport=CoinGeckoTransport(root)
  calls+=1;supported=transport.get_json('/simple/supported_vs_currencies',{},timeout=6)
  if not isinstance(supported,list) or not all(isinstance(q,str) for q in supported):raise VerificationError('PROVIDER_QUOTE_LIST_INVALID')
  qs=sorted({q.lower() for _,_,q in pending})
  if not set(qs).issubset(supported):raise VerificationError('REQUESTED_QUOTE_NOT_SUPPORTED_NO_BINDINGS_APPLIED')
  calls+=1;response=transport.get_json('/simple/price',{'ids':','.join(sorted({pid for _,pid,_ in pending})),'vs_currencies':','.join(qs),'include_last_updated_at':'true'},timeout=6)
  if not isinstance(response,dict):raise VerificationError('PROVIDER_RESPONSE_INVALID')
  fetched=now or dt.datetime.now(dt.timezone.utc)
  if fetched.tzinfo is None or fetched.utcoffset() is None:raise VerificationError('AWARE_TIME_REQUIRED')
  fetched=fetched.astimezone(dt.timezone.utc);evidence=[]
  for iid,pid,q in pending:
   row=response.get(pid)
   if not isinstance(row,dict) or not positive(row.get(q.lower())):raise VerificationError('EXACT_PROVIDER_QUOTE_PRICE_NOT_AVAILABLE_NO_BINDINGS_APPLIED')
   stamp=row.get('last_updated_at')
   if isinstance(stamp,bool) or not isinstance(stamp,(int,float,Decimal)):raise VerificationError('PROVIDER_TIMESTAMP_REQUIRED')
   try:observed=dt.datetime.fromtimestamp(float(stamp),dt.timezone.utc)
   except (ValueError,OverflowError,OSError):raise VerificationError('PROVIDER_TIMESTAMP_INVALID')
   if not -30<=(fetched-observed).total_seconds()<=1800:raise VerificationError('PROVIDER_QUOTE_STALE_OR_FUTURE_NO_BINDINGS_APPLIED')
   evidence.append({'instrument_id':iid,'provider_id':pid,'quote_currency':q,'provider_observed_at':observed.isoformat(),'quote_available':True})
  # Current context and registry must still agree; never apply to a stale review.
  if queue_reader(root)['queue_digest']!=queue['queue_digest']:raise VerificationError('REVIEW_CONTEXT_CHANGED_DURING_VERIFICATION')
  if digest(load(root))!=queue['registry_digest']:raise VerificationError('REGISTRY_CHANGED_DURING_VERIFICATION')
  response_hash=hashlib.sha256(json.dumps(response,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False,default=str).encode()).hexdigest()
  confirmation_hash=digest(document)
  confirmed_at=now or dt.datetime.now(dt.timezone.utc);confirmed_at=confirmed_at.astimezone(dt.timezone.utc)
  if (confirmed_at-fetched).total_seconds()>60 or confirmed_at<fetched:raise VerificationError('VERIFICATION_EXPIRED_NO_BINDINGS_APPLIED')
  new=[]
  for item in evidence:
   ref='CoinGecko:/simple/price;provider_id='+item['provider_id']+';quote='+item['quote_currency']+';checked_at='+fetched.isoformat()+';decoded_response_sha256='+response_hash+';user_confirmation_sha256='+confirmation_hash
   new.append({'instrument_id':item['instrument_id'],'provider':'CoinGecko','provider_id':item['provider_id'],'quote_currency':item['quote_currency'],
    'identity_source_ref':ref,'confirmed_by':'LOCAL_OPERATOR_EXPLICIT_MAPPING_CONFIRMATION','confirmed_at':confirmed_at.isoformat(),'effective_from':confirmed_at.date().isoformat()})
  merged={'schema':BS,'bindings':old+new}
  result=apply(merged,root=root,review_digest=digest(merged),expected_registry_digest=queue['registry_digest'],now=confirmed_at)
  return {**base,'status':'CONFIRMED_RESEARCH_BINDINGS_RECORDED_QUOTES_CHECKED','new_binding_count':len(new),'total_binding_count':result['binding_count'],
          'registry_digest':result['registry_digest'],'network_requests':calls,'source_quote_evidence':evidence,'decoded_response_sha256':response_hash,
          'confirmation_sha256':confirmation_hash,'independent_attestation':False,'provider_internal_fx_verified':False,'broker_eligibility_verified':False,
          'observations_written_by_command':False,'normal_cycle_acquisition_not_forced':True}
 finally:
  if owned and transport is not None:transport.close()

if __name__=='__main__':
 import os
 root=Path(sys.argv[1]).expanduser().resolve(strict=True)
 sys.path.insert(0,str(root))
 if len(sys.argv)!=4:raise SystemExit('Uso: comando arquivo_de_confirmacao sha256_do_arquivo')
 from universal_portfolio.explicit_market_bindings_a24 import local
 EXPECTED={'tools/review_funded_bindings_a24.py': '594712331b6bbf931a5fe2f63c879cb028f089443e7cbafa1727e7e4f472f37b', 'tools/market_provider_bindings_a24.py': 'e039590b76ba489a38752f3c38128b6391a9f073d5f65617a4bcfc73c0913a52', 'universal_portfolio/binding_review_queue_a24.py': '9763a4ca7ca404a0facbe2da02be9da1ed2fa2e58592306e381a8fe98c00ec7b', 'universal_portfolio/explicit_market_bindings_a24.py': '79a9e124fb6528325d47e05c50bd08849a8836d4d0f113df15049b92846145f7', 'universal_portfolio/research_quote_acquisition_a24.py': '86b1bfab03f9a842529dd704fa4c9e22fcbe266a5f63b32c1b01236634dda85c', 'universal_portfolio/funded_currency_research_a24.py': '96312739118a070574fbb18229fd74b690435d21cf4cbb6c078aa90e644d25c5'}
 for rel,expected in EXPECTED.items():
  p=local(root,rel)
  if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:raise SystemExit('SOURCE_HASH_MISMATCH:'+rel+'; nenhum vínculo aplicado.')
 confirmation=Path(sys.argv[2]).expanduser().resolve(strict=True);raw=confirmation.read_bytes()
 if len(raw)>1024*1024 or hashlib.sha256(raw).hexdigest()!=sys.argv[3]:raise SystemExit('CONFIRMATION_INTEGRITY_MISMATCH; nenhum vínculo aplicado.')
 try:report=verify_and_apply(root,json.loads(raw))
 except Exception as exc:
  message=str(exc)
  safe=message if re.fullmatch('[A-Z][A-Z0-9_]{0,160}',message) else type(exc).__name__
  report={'status':'SOURCE_CHECK_OR_REGISTRATION_NOT_COMPLETED','reason':safe,'error_type':type(exc).__name__,
          'financial_mutation':False,'historical_records_relabelled':False,'services_restarted':False,'canonical_publication_authorized':False}
 output=Path.home()/'Downloads';output.mkdir(exist_ok=True);output=output.resolve()
 if output.is_relative_to(root):raise SystemExit('REPORT_MUST_BE_OUTSIDE_PROJECT')
 path=output/('PORQUINHO_A24_FONTES_CONFIRMADAS_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S_%f')+'.json')
 with open(path,'x',encoding='utf-8',opener=lambda p,f:os.open(p,f,0o600)) as stream:json.dump(report,stream,ensure_ascii=False,indent=2);stream.write('\n')
 print(json.dumps(report,ensure_ascii=False,indent=2));print('RELATORIO_PARA_COMPARTILHAR='+str(path))
 print('Sem reinício, treino, refresh ou operação financeira. Os registros anteriores não foram reatribuídos.')
 if report['status']=='SOURCE_CHECK_OR_REGISTRATION_NOT_COMPLETED':raise SystemExit(1)

A24_VERIFIED_SOURCE
