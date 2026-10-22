#!/bin/bash
set -euo pipefail
umask 077
"$HOME/anaconda3/bin/python" -I -B - <<'PY'
import concurrent.futures as futures
import datetime as dt
import hashlib
import json
import pathlib
import sys
import zipfile
ROOT=pathlib.Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2')
assert (ROOT/'webapp/server.py').is_file(), 'PROJETO_NAO_LOCALIZADO'
sys.path.insert(0,str(ROOT))
from universal_portfolio.global_radar_a24 import catalog
from universal_portfolio.explicit_market_bindings_a24 import load
from market_data.gateway import get_json
rows,issues=catalog(ROOT)
bound={r['instrument_id'] for r in load(ROOT)['bindings']}
missing=[r for r in rows if r['instrument_id'] not in bound]
report={'schema':'porquinho.global-source-discovery/1.0','collected_at':dt.datetime.now(dt.timezone.utc).isoformat(),'issues':issues,'rows':[], 'registry_mutation':False,'model_mutation':False,'binding_created':False}

def selected(row,fields):return {k:row.get(k) for k in fields if k in row}
def inspect(row):
 out=selected(row,('instrument_id','symbol','name','asset_class','market','jurisdiction','currency','catalog_status'))
 out.update(status='DISCOVERY_ADAPTER_REQUIRED',candidates=[],identity_confirmed=False)
 if row['catalog_status']!='GLOBAL_CATALOG_REGISTERED':out['status']=row['catalog_status'];return out
 symbol=row.get('symbol')
 if row.get('market')!='B3' or not isinstance(symbol,str) or not symbol:return out
 try:
  listing=get_json('https://brapi.dev/api/quote/list',{'search':symbol},token_env='BRAPI_TOKEN',provider_id='brapi',timeout=5)
  if not isinstance(listing,dict) or not isinstance(listing.get('stocks'),list):
   out['status']='PROVIDER_LIST_SCHEMA_UNRECOGNIZED';return out
  candidates=[v for v in listing['stocks'] if isinstance(v,dict) and v.get('stock')==symbol]
  # Matching a reported symbol is a source claim, not an identity binding.
  out['candidates']=[selected(v,('stock','name','type','sector','currency','exchange','isin')) for v in candidates]
  out['listing_response_sha256']=hashlib.sha256(json.dumps(listing,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
  if len(candidates)!=1:
   out['status']='SOURCE_SYMBOL_NOT_FOUND' if not candidates else 'AMBIGUOUS_SOURCE_CANDIDATES';return out
  from urllib.parse import quote
  response=get_json('https://brapi.dev/api/quote/'+quote(symbol,safe=''),token_env='BRAPI_TOKEN',provider_id='brapi',timeout=5)
  quotes=response.get('results') if isinstance(response,dict) else None
  if not isinstance(quotes,list):out['status']='PROVIDER_QUOTE_SCHEMA_UNRECOGNIZED';return out
  matches=[v for v in quotes if isinstance(v,dict) and v.get('symbol')==symbol]
  out['quote_claims']=[selected(v,('symbol','shortName','longName','currency','regularMarketPrice','regularMarketTime','exchange','fullExchangeName','isin')) for v in matches]
  out['status']='SOURCE_CLAIMS_COLLECTED_REVIEW_REQUIRED' if len(matches)==1 else 'QUOTE_NOT_FOUND_OR_AMBIGUOUS'
 except Exception as exc:
  # Never export exception messages: upstream errors may contain credentials.
  out['status']='DISCOVERY_FAILED';out['error_type']=type(exc).__name__
 return out

print('Consultando fontes dos instrumentos sem vínculo. Nenhum cadastro será alterado.',flush=True)
with futures.ThreadPoolExecutor(max_workers=4) as pool:
 tasks={pool.submit(inspect,r):r for r in missing}
 for task in futures.as_completed(tasks):
  result=task.result();report['rows'].append(result)
  print(result['instrument_id']+': '+result['status'],flush=True)
report['rows'].sort(key=lambda r:r['instrument_id'])
output=pathlib.Path.home()/'Downloads'/('PORQUINHO_FONTES_GLOBAIS_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip')
with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED) as archive:
 archive.writestr('fontes_globais.json',json.dumps(report,ensure_ascii=False,indent=2))
print('SOMENTE_LEITURA; VINCULOS_DADOS_E_BRAIN_NAO_ALTERADOS')
print('ENVIAR='+str(output))
PY
