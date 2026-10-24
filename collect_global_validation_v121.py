"""One read-only validation bundle from the active local app; no cycles or training."""
from pathlib import Path
import datetime as dt,hashlib,json,os,re,urllib.request,zipfile
ROOT=Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2')
MONITOR_KEYS=('schema','status','observed_at','issues','universal_portfolio','cockpit_panels','analysis_coverage','research_economic_components','action_research_handoff','action_component_validation','economic_action_policy','economic_action_evidence','economic_action_plan','learned_policy_economic_basis','learned_policy_account_context','learned_allocation_policy','global_existing_lab','global_model_evaluation','global_research_lab','global_history_source','account_cost_evidence','observed_manual_trade_costs','official_bank_cost_references','official_exchange_fee_references','cash_documentary_cost_summary','reported_pretrade_preview_summary','action_cost_visibility','cash_plan_visibility','cash_plan_assessment')
FILES=('porquinho.py','static/experience_panels_v37.js','static/balance_accounts_v41.js','webapp/server.py','universal_portfolio/global_dashboard_observations_a24.py','universal_portfolio/global_action_readings_a24.py','universal_portfolio/universal_action_rules_a24.py','universal_portfolio/action_research_handoff_a24.py','universal_portfolio/economic_source_producer_a24.py','universal_portfolio/research_economic_components_a24.py')
SCORE_KEYS=('asset','account_id','instrument_id','provider','provider_id','currency','quote_currency','quote_currency_source','quote_observed_at','quote_freshness','metric_contract','metric_unit','action','promising_pct','entry','risk','reversal_risk','asymmetry','daily_sell_confirmation','daily_sell_confirmation_currency')
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None

def scrub(value):
 if isinstance(value,dict):return {k:('[REDACTED]' if re.search(r'token|password|secret|api.?key|authorization|credential',k,re.I) else scrub(v)) for k,v in value.items()}
 if isinstance(value,list):return [scrub(v) for v in value]
 if isinstance(value,str):return re.sub(r'([?&](?:token|apikey|api_key|key)=)[^&#\s]+',r'\1[REDACTED]',value,flags=re.I)
 return value

def get(route):
 try:
  request=urllib.request.Request('http://127.0.0.1:8765'+route,headers={'Cache-Control':'no-cache'})
  with urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect).open(request,timeout=120) as response:raw=response.read(64*1024*1024+1)
  if len(raw)>64*1024*1024:raise ValueError('RESPONSE_SIZE_LIMIT')
  return {'read_ok':True,'body':json.loads(raw)}
 except Exception as exc:return {'read_ok':False,'error_type':type(exc).__name__}

def status_projection(result):
 if not result['read_ok']:return result
 b=result['body'];p=b.get('portfolio') or {}
 return {'read_ok':True,'snapshot':b.get('snapshot'), 'portfolio':{k:p[k] for k in ('timestamp','total_wealth_eur','total_pnl_eur','cash_eur','portfolio_value_eur','calibration') if k in p},'scores':[{k:r[k] for k in SCORE_KEYS if k in r} for r in p.get('scores',[])], 'manual_recommendation_publication':b.get('manual_recommendation_publication')}

def journal(root):
 result=[];folder=root/'data/observability/global_dashboard_a24'
 if not folder.exists():return result
 for p in sorted(folder.glob('????-??-??.jsonl'),reverse=True)[:2]:
  try:
   if any(x.is_symlink() for x in (p,*p.parents)):raise ValueError('SYMLINK_REFUSED')
   with p.open('rb') as f:
    size=os.fstat(f.fileno()).st_size;start=max(0,size-1024*1024);f.seek(start);raw=f.read(1024*1024+1)
   lines=raw.splitlines();lines=lines[1:] if start else lines;records=[]
   for line in lines[-16:]:
    try:
     item=json.loads(line);b=item['body'];sha=hashlib.sha256(json.dumps(b,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
     records.append({'sha256_valid':sha==item.get('sha256'),'observed_at':b.get('observed_at'),'points':b.get('points')})
    except (ValueError,KeyError,TypeError):records.append({'invalid_or_partial_line':True})
   result.append({'file':str(p.relative_to(root)),'size':size,'tail_records':records,'partial_tail':not raw.endswith(b'\n')})
  except Exception as exc:result.append({'file':p.name,'error_type':type(exc).__name__})
 return result

def collect(root,getter=get):
 before=status_projection(getter('/api/status'));monitor=getter('/api/research/monitor-consolidation');manual=getter('/api/recommendations/manual');after=status_projection(getter('/api/status'))
 if monitor['read_ok']:monitor={'read_ok':True,'body':{k:monitor['body'][k] for k in MONITOR_KEYS if k in monitor['body']}}
 hashes={}
 for n in FILES:
  p=root/n
  try:
   if any(x.is_symlink() for x in (p,*p.parents)):raise ValueError('SYMLINK_REFUSED')
   if p.stat().st_size>8*1024*1024:raise ValueError('FILE_SIZE_LIMIT')
   hashes[n]=hashlib.sha256(p.read_bytes()).hexdigest()
  except Exception as exc:hashes[n]={'error_type':type(exc).__name__}
 try:
  p=root/'config.json'
  if p.is_symlink() or p.stat().st_size>4*1024*1024:raise ValueError('CONFIG_READ_REFUSED')
  rules=json.loads(p.read_bytes()).get('action_rules')
 except Exception as exc:rules={'error_type':type(exc).__name__}
 return scrub({'schema':'porquinho.global-flow-validation-bundle/1.0','collected_at':dt.datetime.now(dt.timezone.utc).isoformat(),'status_before':before,'monitor':monitor,'manual_publication':manual,'status_after':after,'snapshot_unchanged_during_collection':before.get('read_ok') is True and after.get('read_ok') is True and before.get('snapshot')==after.get('snapshot'),'source_sha256':hashes,'configured_action_rules':rules,'observed_history':journal(root),'read_only':True,'cycle_requested':False,'training_requested':False,'models_modified':False,'financial_mutation':False})

def main():
 print('VALIDANDO_ESTADO_ATUAL; SOMENTE_LEITURA; SEM_CICLO_OU_TREINAMENTO',flush=True)
 report=collect(ROOT);out=Path.home()/'Downloads'/('PORQUINHO_VALIDACAO_GLOBAL_V121_'+dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip')
 with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED) as z:z.writestr('validation.json',json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False))
 manual=report['manual_publication'];body=manual.get('body') or {}
 print(json.dumps({'publication_status':body.get('status'),'recommendation_count':len(body.get('recommendations') or []),'blocking_reason_counts':body.get('blocking_reason_counts'),'monitor_read_ok':report['monitor'].get('read_ok'),'snapshot_unchanged_during_collection':report['snapshot_unchanged_during_collection']},ensure_ascii=False,indent=2))
 print('ENVIAR='+str(out))
if __name__=='__main__':main()
