#!/bin/bash
set -euo pipefail
umask 077
"$HOME/anaconda3/bin/python" -I -B - <<'PYTHON'
import datetime,hashlib,json,os,pathlib,re,urllib.request,urllib.error,urllib.parse,zipfile
from html.parser import HTMLParser
class Links(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.href=None;self.words=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.href=dict(attrs).get('href');self.words=[]
 def handle_data(self,data):
  if self.href:self.words.append(data)
 def handle_endtag(self,tag):
  if tag=='a' and self.href:self.rows.append((self.href,' '.join(self.words)));self.href=None
allowed={'nubank.com.br','www.nubank.com.br','n26.com','www.n26.com','support.n26.com'}
def safe(url):
 p=urllib.parse.urlsplit(url)
 return p.scheme=='https' and p.hostname in allowed and not p.username and not p.password and not p.query
class Redirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  if not safe(newurl):raise ValueError('REDIRECT_OUTSIDE_PUBLIC_SCOPE')
  return super().redirect_request(req,fp,code,msg,headers,newurl)
opener=urllib.request.build_opener(Redirect())
seeds=['https://nubank.com.br/nu/investimentos','https://n26.com/en-de']
queue=[(u,0) for u in seeds];seen=set();documents=[];payloads={};total=0
while queue and len(documents)<10 and total<12*1024*1024:
 url,depth=queue.pop(0)
 if url in seen or not safe(url):continue
 seen.add(url);row={'requested_url':url,'fetched_at':datetime.datetime.now(datetime.timezone.utc).isoformat()};documents.append(row)
 print('FONTE_PUBLICA:',url,flush=True)
 try:
  request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (public-document-research)','Accept':'text/html,application/pdf'})
  with opener.open(request,timeout=20) as response:
   body=response.read(2*1024*1024+1);final=response.geturl();ctype=response.headers.get('Content-Type','')
   if len(body)>2*1024*1024:raise ValueError('DOCUMENT_SIZE_LIMIT')
   if not safe(final):raise ValueError('FINAL_URL_OUTSIDE_SCOPE')
   row.update(status=response.status,final_url=final,content_type=ctype,sha256=hashlib.sha256(body).hexdigest(),bytes=len(body))
  total+=len(body);name='documentos/'+str(len(documents)).zfill(2)+('.pdf' if 'pdf' in ctype else '.html');row['archive_path']=name;payloads[name]=body
  if depth>=3 or 'html' not in ctype:continue
  parser=Links();parser.feed(body.decode('utf-8','replace'));candidates=[]
  for href,label in parser.rows:
   link=urllib.parse.urljoin(final,href).split('#')[0]
   if not safe(link) or link in seen:continue
   text=(urllib.parse.unquote(link)+' '+label).lower()
   crypto=any(t in text for t in ('cripto','crypto','bitcoin'))
   fee=any(t in text for t in ('taxa','tarifa','preco','preço','fee','pricing','gebühr','gebuehr','kosten'))
   if crypto:candidates.append((10+5*fee,link))
   elif depth>0 and fee:candidates.append((8,link))
  selected=[]
  for score,link in sorted(set(candidates),key=lambda x:(-x[0],len(x[1]),x[1])):
   if link not in selected:selected.append(link)
   if len(selected)>=3:break
  queue.extend((link,depth+1) for link in selected)
 except urllib.error.HTTPError as exc:row.update(status=exc.code,error_type='HTTPError')
 except Exception as exc:row['error_type']=type(exc).__name__
report={'schema':'porquinho.public-crypto-source-collection/1.0','documents':documents,'execution_authorized':False,'financial_mutation':False,'models_modified':False,'tariffs_applied':False,'note':'Public documents only; a successful download does not validate account applicability or tariff completeness.'}
folder=pathlib.Path.home()/'Downloads';folder.mkdir(exist_ok=True);out=folder/('PORQUINHO_FONTES_CRIPTO_V100_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+os.urandom(3).hex()+'.zip')
with out.open('xb') as stream:
 os.chmod(out,0o600)
 with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('relatorio.json',json.dumps(report,ensure_ascii=False,indent=2))
  for name,body in payloads.items():z.writestr(name,body)
print('SOMENTE_FONTES_PUBLICAS; PROJETO_E_MODELOS_NAO_ALTERADOS')
print('ENVIAR='+str(out))
PYTHON
