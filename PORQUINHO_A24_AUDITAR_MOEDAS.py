"""Read-only, bounded currency audit. No application imports or attribution writes."""
import ast,csv,hashlib,io,json,os,re,sys
from collections import Counter,defaultdict
from decimal import Decimal,InvalidOperation
from pathlib import Path
MAX=64*1024*1024

def label(x):return x if isinstance(x,str) and re.fullmatch(r'[A-Za-z0-9_.:-]{1,120}',x) else 'UNSPECIFIED'
def currency(x):return x if isinstance(x,str) and x.isascii() and x.isalpha() and x.isupper() and len(x)<=16 else None
class Audit:
 last_source=None
 def __init__(self,root):self.root=Path(root).resolve(strict=True);self.seen={};self.total=0;self.current_source=None
 def path(self,rel):
  Audit.last_source=str(rel)
  p=self.root/rel
  if p.is_symlink() or any(a.is_symlink() for a in p.parents if a!=self.root.parent):raise ValueError('SYMLINK_REFUSED')
  if not p.resolve().is_relative_to(self.root):raise ValueError('OUTSIDE_ROOT')
  return p
 def raw(self,rel):
  self.current_source=str(rel);p=self.path(rel)
  if not p.is_file():return None
  size=p.stat().st_size
  if size>MAX:raise ValueError('SOURCE_SIZE_LIMIT')
  if self.total+size>256*1024*1024:raise ValueError('TOTAL_READ_LIMIT')
  raw=p.read_bytes();self.total+=len(raw)
  self.seen[str(rel)]=hashlib.sha256(raw).hexdigest();return raw
 def json(self,rel):
  raw=self.raw(rel);return json.loads(raw,parse_float=Decimal) if raw is not None else None
 def stable(self):return all(hashlib.sha256(self.path(p).read_bytes()).hexdigest()==h for p,h in self.seen.items())

def decimal(x):
 try:
  n=Decimal(str(x));return n if n.is_finite() else None
 except (InvalidOperation,ValueError):return None

def walk(value):
 stack=[value];nodes=0
 while stack:
  v=stack.pop();nodes+=1
  if nodes>1000000:raise ValueError('JSON_NODE_LIMIT')
  if isinstance(v,dict):yield v;stack.extend(v.values())
  elif isinstance(v,list):stack.extend(v)

def summarize_json(value):
 counts=Counter();quotes=Counter();operational=Counter();matured=Counter();matured_quotes=Counter();eur_names=Counter();families=Counter()
 for row in walk(value):
  q=currency(row.get('quote_currency'));c=currency(row.get('currency'))
  iid=row.get('instrument_id',row.get('canonical_instrument_id'))
  if isinstance(iid,str):families['BRAZIL_EXPLICIT_ID_PREFIX' if iid.startswith('BR:') else 'CRYPTO_EXPLICIT_ID_SCOPE' if ':CRYPTO:' in iid else 'OTHER_EXPLICIT_ID']+=1
  if q:quotes[q]+=1
  if c:operational[c]+=1
  for k in row:
   if isinstance(k,str) and k.lower().endswith('_eur') and re.fullmatch('[A-Za-z0-9_]{1,80}',k):eur_names[k]+=1
  price=any(k in row for k in ('price','price_eur','reference_price_eur','maturity_price_eur','entry_price_eur','current_price'))
  if price:counts['price_bearing_objects']+=1;counts['price_objects_with_explicit_quote' if q else 'price_objects_without_explicit_quote']+=1
  status=row.get('status',row.get('outcome_status',row.get('maturity_status')))
  if status=='MATURED':matured['objects_with_stored_matured_status']+=1;matured_quotes[q or 'QUOTE_NOT_EXPLICIT_ON_OBJECT']+=1
 return {'object_currency_declarations':dict(operational),'object_quote_declarations':dict(quotes),'explicit_identity_scope_object_counts':dict(families),'coverage':dict(counts),'eur_named_field_counts':dict(eur_names),'stored_matured_status_counts':dict(matured),'stored_matured_object_quote_counts':dict(matured_quotes),'semantics':'OBJECT_COUNTS_NOT_UNIQUE_TRADES; currency_IS_NOT_AUTOMATICALLY_quote_currency; NO_PARENT_QUOTE_INHERITANCE'}

def code_contract(a):
 out={}
 for rel in ('tools/fetch_history.py','porquinho.py'):
  raw=a.raw(rel)
  if raw is None:out[rel]={'status':'MISSING'};continue
  tree=ast.parse(raw);eur_requests=0;default_eur=False;read_legacy=False
  for n in ast.walk(tree):
   if isinstance(n,ast.Dict):
    for k,v in zip(n.keys,n.values):
     if isinstance(k,ast.Constant) and k.value=='vs_currency' and isinstance(v,ast.Constant) and v.value=='eur':eur_requests+=1
   if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='quote' for t in n.targets) and isinstance(n.value,ast.IfExp) and isinstance(n.value.body,ast.Constant) and n.value.body.value=='EUR':default_eur=True
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='get' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='price_eur':read_legacy=True
  out[rel]={'sha256':hashlib.sha256(raw).hexdigest(),'literal_eur_request_dictionary_count':eur_requests,'default_quote_eur_branch_present':default_eur,'legacy_price_eur_reads_present':read_legacy,'historical_row_provenance_proven':False}
 return out


REASONS={'SYMLINK_REFUSED','OUTSIDE_ROOT','SOURCE_SIZE_LIMIT','TOTAL_READ_LIMIT','JSON_NODE_LIMIT','DIRECTORY_FILE_LIMIT','PARTIAL_JOURNAL_LINE','JOURNAL_BODY_INVALID','JOURNAL_CHAIN_INVALID','JOURNAL_RECORD_LIMIT','JOURNAL_FRAMING_INVALID'}
def reason(exc):
 return str(exc) if type(exc) is ValueError and str(exc) in REASONS else type(exc).__name__

def journal(raw):
 text=raw.decode('utf-8');decoder=json.JSONDecoder();pos=0;previous='GENESIS';bodies=[];framing=Counter()
 while pos<len(text):
  while pos<len(text) and text[pos] in ' \t\r\n':pos+=1
  if pos==len(text):break
  item,end=decoder.raw_decode(text,pos)
  if text.startswith('\r\n',end):pos=end+2;framing['CRLF']+=1
  elif text.startswith('\n',end):pos=end+1;framing['LF']+=1
  elif text.startswith('\\n',end):pos=end+2;framing['LEGACY_LITERAL_BACKSLASH_N']+=1
  elif end==len(text):raise ValueError('PARTIAL_JOURNAL_LINE')
  else:raise ValueError('JOURNAL_FRAMING_INVALID')
  if not isinstance(item,dict) or not isinstance(item.get('body'),dict):raise ValueError('JOURNAL_BODY_INVALID')
  body=item['body'];expected=hashlib.sha256((previous+'|'+json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)).encode()).hexdigest()
  if item.get('previous_hash')!=previous or item.get('hash')!=expected:raise ValueError('JOURNAL_CHAIN_INVALID')
  previous=expected;bodies.append(body)
  if len(bodies)>100000:raise ValueError('JOURNAL_RECORD_LIMIT')
 return bodies,dict(framing)

def summarize_directory(a,directory,limit=20000):
 p=a.path(directory)
 if not p.is_dir():return {'status':'MISSING_OR_EMPTY','scanned_file_count':0}
 counters={};scanned=0;encountered=0;issues=[]
 for f in p.glob('*.json'):
  encountered+=1
  if scanned>=limit:
   issues.append({'source':directory,'reason':'DIRECTORY_FILE_LIMIT','configured_file_limit':limit});break
  rel=str(f.relative_to(a.root))
  try:
   value=a.json(rel);summary=summarize_json(value)
  except (ValueError,TypeError,OSError) as exc:
   issues.append({'source':rel,'reason':reason(exc)})
   if reason(exc)=='TOTAL_READ_LIMIT':break
   # Stop this directory rather than omitting arbitrarily many invalid records.
   break
  scanned+=1
  for key,values in summary.items():
   if isinstance(values,dict):counters.setdefault(key,Counter()).update(values)
 return {'status':'PARTIAL_DIRECTORY_INSPECTION' if issues else 'READ' if scanned else 'MISSING_OR_EMPTY',
         'scanned_file_count':scanned,'encountered_file_count':encountered,'configured_file_limit':limit,
         'issues':issues,**{k:dict(v) for k,v in counters.items()},
         'semantics':'AGGREGATED_OBJECT_COUNTS_NOT_UNIQUE_TRADES; NO_PARENT_QUOTE_INHERITANCE; NO_CURRENCY_ASSIGNED'}

def audit(root):
 a=Audit(root);report={'validation':'A24_CURRENCY_MATURATION_DOUBLE_CHECK_READ_ONLY','source_code_contracts':code_contract(a),'sections':{}}
 market=a.raw('data/database/market_daily.csv');rows=list(csv.DictReader(io.StringIO(market.decode('utf-8-sig'),newline=''))) if market is not None else []
 index=defaultdict(list);quotes=Counter();missing=0
 for row in rows:
  q=currency(row.get('quote_currency'));quotes[q or 'UNSPECIFIED']+=1
  if not q:missing+=1
  index[(row.get('asset'),row.get('date'))].append(row)
 report['market']={'row_count':len(rows),'quote_declaration_counts':dict(quotes),'rows_without_explicit_quote':missing,'currency_inferred_from_suffix':False}
 def match(asset,date,price):
  possible=index.get((asset,date),[]);matches=[r for r in possible if decimal(r.get('price_eur')) is not None and decimal(r.get('price_eur'))==decimal(price)]
  if len(possible)>1:return 'AMBIGUOUS_ASSET_DATE_ROWS'
  if len(matches)!=1:return 'NO_EXACT_LEGACY_PRICE_MATCH'
  q=currency(matches[0].get('quote_currency'))
  return 'MATCHED_DECLARED_'+q if q else 'MATCHED_MARKET_ROW_WITHOUT_EXPLICIT_QUOTE'
 for rel in ('results/latest.json','results/prediction_lab.json','data/brain_experimental_episodes/outcomes_latest.json'):
  value=a.json(rel);report['sections'][rel]={'status':'MISSING'} if value is None else {'status':'READ',**summarize_json(value)}
  if rel.endswith('outcomes_latest.json') and value is not None:
   episodes=value if isinstance(value,list) else next((value[k] for k in ('episodes','outcomes','episode_outcomes') if isinstance(value,dict) and isinstance(value.get(k),list)),[])
   counts=Counter();assets=defaultdict(Counter)
   for e in episodes:
    if not isinstance(e,dict):continue
    asset=e.get('asset');name=label(asset);ref=match(asset,e.get('reference_date'),e.get('reference_price_eur')) if 'reference_price_eur' in e else 'REFERENCE_PRICE_NOT_PRESENT'
    assets[name]['episode_count']+=1;counts['reference_'+ref]+=1
    hs=e.get('horizons',[]);hs=hs.values() if isinstance(hs,dict) else hs
    if not isinstance(hs,(list,type({}.values()))):continue
    for h in hs:
     if not isinstance(h,dict):continue
     if h.get('status')=='MATURED':
      mat=match(asset,h.get('maturity_date'),h.get('maturity_price_eur'));counts['matured_'+mat]+=1;assets[name]['stored_matured_horizon_count']+=1
      if ref.startswith('MATCHED_DECLARED_') and mat.startswith('MATCHED_DECLARED_'):
       counts['matured_same_declared_quote' if ref==mat else 'matured_conflicting_declared_quotes']+=1
      else:counts['matured_quote_pair_unresolved']+=1
   report['episode_market_cross_check']={'counts':dict(counts),'by_asset_label':{k:dict(v) for k,v in sorted(assets.items())},'join_semantics':'LEGACY_ASSET_DATE_PRICE_ONLY_NOT_IDENTITY_PROOF; NO_CURRENCY_ASSIGNED'}
 for rel in ('results/p35e_research_forecast_issuance.jsonl','results/p35h_capture_context.jsonl'):
  raw=a.raw(rel)
  if raw is None:report['sections'][rel]={'status':'MISSING'};continue
  try:
   bodies,framing=journal(raw)
   report['sections'][rel]={'status':'LOCAL_CHAIN_VERIFIED_NOT_INDEPENDENT_ATTESTATION','record_count':len(bodies),'separator_counts':framing,**summarize_json(bodies)}
  except (ValueError,TypeError,KeyError) as exc:
   report['sections'][rel]={'status':'JOURNAL_NOT_VERIFIED','error_type':type(exc).__name__,'reason':reason(exc),'source_modified':False}
   report.setdefault('issues',[]).append({'source':rel,'reason':reason(exc)})
 # Observe additional maturity tracks without executing their reconciliators.
 for directory in ('data/brain/shadow/outcomes','data/brain/prospective/buy_forecasts','data/brain/prospective/buy_outcome_joins'):
  summary=summarize_directory(a,directory)
  report['sections'][directory]=summary
  for issue in summary.get('issues',[]):report.setdefault('issues',[]).append(issue)
 stable=a.stable();report.update(status=('PARTIAL_INSPECTION_NOT_CERTIFIED' if report.get('issues') else 'INSPECTED_NOT_CERTIFIED') if stable else 'SOURCE_CHANGED_RETRY_REQUIRED',source_files_stable_during_read=stable,
  project_mutation=False,financial_values_exported=False,training_requested=False,services_restarted=False,currency_attribution_performed=False,canonical_publication_authorized=False,
  limitations=['CURRENT_CODE_CONTRACT_IS_NOT_HISTORICAL_ATTESTATION','NO_SYMBOL_TO_CANONICAL_IDENTITY_BINDING','ACCOUNT_CURRENCY_AND_QUOTE_CURRENCY_ARE_DIFFERENT','SCANNED_PATHS_ONLY_NOT_ALL_SNAPSHOT_HISTORY'])
 if not stable:report={'validation':report['validation'],'status':'SOURCE_CHANGED_RETRY_REQUIRED','project_mutation':False}
 return report

if __name__=='__main__':
 root=Path(sys.argv[1]).resolve(strict=True)
 def guard(event,args):
  if event=='open':
   mode,flags=args[1:3]
   if (isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)):raise RuntimeError('READ_ONLY_WRITE_REFUSED')
  if event in {'os.remove','os.rename','os.mkdir','os.rmdir','os.chmod','os.truncate','os.link','os.symlink','subprocess.Popen','os.system','socket.connect','socket.bind'}:raise RuntimeError('READ_ONLY_SIDE_EFFECT_REFUSED')
 sys.addaudithook(guard)
 try:out=audit(root)
 except Exception as exc:out={'validation':'A24_CURRENCY_MATURATION_DOUBLE_CHECK_READ_ONLY','status':'INSPECTION_NOT_COMPLETED','error_type':type(exc).__name__,'reason':reason(exc),'source':Audit.last_source,'project_mutation':False}
 print(json.dumps(out,ensure_ascii=False,indent=2))
