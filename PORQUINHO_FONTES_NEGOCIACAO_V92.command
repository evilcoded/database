#!/bin/bash
set -euo pipefail
"$HOME/anaconda3/bin/python" -I -B - "$@" <<'PY'
import datetime as dt,hashlib,heapq,json,re,sys,urllib.request,urllib.error,urllib.parse,zipfile
from html.parser import HTMLParser
from pathlib import Path
MAX_PAGES=12;MAX_TOTAL=12*1024*1024;MAX_DOCUMENT=3*1024*1024
seeds=list(dict.fromkeys(sys.argv[1:]))
if not 1<=len(seeds)<=4:raise SystemExit('Informe de 1 a 4 URLs públicas HTTPS como argumentos.')
def clean(url):
 p=urllib.parse.urlsplit(url)
 if p.scheme!='https' or not p.hostname or p.username or p.password or p.query:return None
 return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path or '/',p.query,''))
if any(clean(u) is None for u in seeds):raise SystemExit('URLs HTTPS públicas sem credenciais ou query obrigatórias.')
seeds=[clean(u) for u in seeds];allowed={urllib.parse.urlsplit(u).hostname for u in seeds}
class Links(HTMLParser):
 def __init__(self):super().__init__();self.href=None;self.text=[];self.found=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
  if t=='a' and not self.skip:self.href=dict(a).get('href');self.text=[]
 def handle_data(self,data):
  if self.href and not self.skip:self.text.append(data)
 def handle_endtag(self,t):
  if t=='a' and self.href:self.found.append((self.href,' '.join(self.text)));self.href=None;self.text=[]
  if t in ('script','style') and self.skip:self.skip-=1
 def handle_startendtag(self,t,a):pass
class Redirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  if not clean(newurl):raise ValueError('Redirecionamento não público HTTPS recusado')
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def priority(url,label):
 text=(url+' '+label).casefold()
 weights=[('tarifa',5),('tributa',5),('renda-variavel',18),('renda variável',18),('acoes',20),('ações',20),('a-vista',12),('à vista',12),('emolumento',20),('liquida',8),('negocia',8)]
 score=sum(w for word,w in weights if word in text)
 if not score:return 0
 if '.pdf' in text:score+=10
 if any(word in text for word in ('futuros','opcoes','opções','balcao','balcão','criptomoeda')):score-=30
 return score
queue=[];counter=0
for u in seeds:heapq.heappush(queue,(-1000,counter,0,u,None));counter+=1
seen=set();total=0;records=[];edges=[]
opener=urllib.request.build_opener(Redirect())
folder=Path.home()/'Downloads';folder.mkdir(exist_ok=True)
output=folder/('PORQUINHO_FONTES_NEGOCIACAO_V92_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip')
with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED) as archive:
 while queue and len(records)<MAX_PAGES and total<MAX_TOTAL:
  _,_,depth,url,parent=heapq.heappop(queue)
  if url in seen:continue
  seen.add(url);row={'requested_url':url,'parent_url':parent,'depth':depth,'fetched_at':dt.datetime.now(dt.timezone.utc).isoformat()}
  print('CONSULTANDO:',url,flush=True)
  try:
   request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 Porquinho-Public-Source-Collector/2.0','Accept':'text/html,application/pdf;q=0.9,*/*;q=0.5'})
   try:response=opener.open(request,timeout=25)
   except urllib.error.HTTPError as exc:response=exc
   with response:
    body=response.read(min(MAX_DOCUMENT,MAX_TOTAL-total)+1);final=response.geturl();status=response.code;ctype=response.headers.get('Content-Type','')
   row.update(http_status=status,final_url=final,content_type=ctype)
   if len(body)>min(MAX_DOCUMENT,MAX_TOTAL-total):row['status']='SIZE_LIMIT_NO_PARTIAL_DOCUMENT_SAVED'
   else:
    name=f'sources/{len(records)+1:02d}.bin';archive.writestr(name,body);total+=len(body)
    row.update(status='PUBLIC_DOCUMENT_SAVED' if status==200 else 'HTTP_ERROR_RESPONSE_SAVED',archive_path=name,sha256=hashlib.sha256(body).hexdigest(),bytes=len(body))
    if status==200 and 'html' in ctype.lower() and depth<4:
     parser=Links();parser.feed(body.decode('utf-8',errors='replace'))
     # Links from a redirected seed remain scoped to that seed's observed host.
     host=urllib.parse.urlsplit(final).hostname
     for href,label in parser.found[:3000]:
      target=clean(urllib.parse.urljoin(final,href));score=priority(target or '',label)
      if not target or target in seen or score<=0:continue
      if urllib.parse.urlsplit(target).hostname not in allowed|{host}:continue
      if len(edges)>=3000:break
      edges.append({'parent_url':final,'url':target,'label':re.sub(r'\s+',' ',label).strip()[:200]})
      heapq.heappush(queue,(-score,counter,depth+1,target,final));counter+=1
  except Exception as exc:row.update(status='FETCH_FAILED',error_type=type(exc).__name__,error=str(exc)[:250])
  records.append(row);print('RESULTADO:',row['status'],'HTTP:',row.get('http_status'),flush=True)
 report={'schema':'porquinho.public-negotiation-sources/1.0','sources':records,'discovered_links':edges,'pending_url_count':len({x[3] for x in queue}-seen),'captured_bytes':total,'limits':{'documents':MAX_PAGES,'total_bytes':MAX_TOTAL,'document_bytes':MAX_DOCUMENT,'discovery_depth':4},'collection_is_exhaustive':False,'rates_extracted':False,'source_applicability_confirmed':False,'application_files_modified':False,'models_modified':False,'financial_mutation':False,'execution_authorized':False}
 archive.writestr('sources_report.json',json.dumps(report,ensure_ascii=False,indent=2))
print('COLETA_PUBLICA_CONCLUIDA; PORQUINHO_E_BRAIN_NAO_ALTERADOS')
print('ENVIAR='+str(output))
PY
