#!/bin/bash
set -euo pipefail
"$HOME/anaconda3/bin/python" -I -B - "$@" <<'PY'
import datetime as dt,hashlib,json,sys,urllib.request,urllib.error,urllib.parse,zipfile,time
from pathlib import Path
urls=sys.argv[1:]
if not 1<=len(urls)<=8:raise SystemExit('Informe entre 1 e 8 URLs públicas HTTPS como argumentos.')
for url in urls:
 p=urllib.parse.urlsplit(url)
 if p.scheme!='https' or not p.hostname or p.username or p.password or p.query or p.fragment:raise SystemExit('URL pública HTTPS sem credenciais, consulta ou fragmento obrigatória.')
class HTTPSRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  if urllib.parse.urlsplit(newurl).scheme!='https':raise ValueError('Redirecionamento sem HTTPS recusado')
  return super().redirect_request(req,fp,code,msg,headers,newurl)
opener=urllib.request.build_opener(HTTPSRedirect())
folder=Path.home()/'Downloads';folder.mkdir(exist_ok=True)
output=folder/('PORQUINHO_FONTES_CAIXA_CUSTOS_V90_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip')
report={'schema':'porquinho.public-cash-cost-sources/1.0','sources':[],
 'account_applicability_confirmed':False,'cash_yield_assumed_zero':False,'rates_extracted':False,
 'application_files_modified':False,'models_modified':False,'training_requested':False,'execution_authorized':False}
with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED) as archive:
 for i,url in enumerate(dict.fromkeys(urls),1):
  print('CONSULTANDO:',url,flush=True);row={'requested_url':url,'fetched_at':dt.datetime.now(dt.timezone.utc).isoformat()};started=time.monotonic()
  try:
   request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 Porquinho-Public-Source-Collector/1.0','Accept':'text/html,application/pdf;q=0.9,*/*;q=0.5'})
   try:response=opener.open(request,timeout=25)
   except urllib.error.HTTPError as exc:response=exc
   with response:
    body=response.read(4*1024*1024+1)
    row.update(http_status=response.code,final_url=response.geturl(),headers={k:response.headers[k] for k in ('Content-Type','Last-Modified','ETag') if k in response.headers})
   if len(body)>4*1024*1024:row['status']='DOCUMENT_SIZE_LIMIT_NO_PARTIAL_DOCUMENT_SAVED'
   else:
    name=f'sources/{i:02d}.bin';archive.writestr(name,body)
    row.update(status='PUBLIC_RESPONSE_SAVED_NOT_APPLICABILITY_VALIDATION' if row['http_status']==200 else 'HTTP_ERROR_RESPONSE_SAVED',archive_path=name,sha256=hashlib.sha256(body).hexdigest(),bytes=len(body))
  except Exception as exc:row.update(status='SOURCE_FETCH_FAILED',error_type=type(exc).__name__,error=str(exc)[:300])
  row['elapsed_seconds']=round(time.monotonic()-started,3);report['sources'].append(row)
  print('RESULTADO:',row['status'],'HTTP:',row.get('http_status'),flush=True)
 archive.writestr('sources_report.json',json.dumps(report,ensure_ascii=False,indent=2))
print('COLETA_PUBLICA_CONCLUIDA; PORQUINHO_E_BRAIN_NAO_ALTERADOS')
print('ENVIAR='+str(output))
PY
