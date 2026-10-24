const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=process.env.PORQUINHO_PROJECT||process.cwd(),ctx={console,Date,Map,Set,Number,String,Array,Math,JSON,Intl};vm.createContext(ctx);
vm.runInContext(`var a24CockpitState={currency:'BRL',account:'',query:''},a24ExplicitFilters=true,v37State={days:90},v35PopupStore=new Map(),v35State={},lastStatus={};
function esc(x){return String(x??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;')}
function a24UiFacts(d){return d.universal_portfolio} function a24UiScope(r){return (!a24CockpitState.currency||r.currency===a24CockpitState.currency)&&(!a24CockpitState.account||r.account_id===a24CockpitState.account)}
function a24UiSearch(r){return !a24CockpitState.query||JSON.stringify(r).includes(a24CockpitState.query)}
function a24PlotNumber(x){return x===null||x===undefined||x===''?null:Number.isFinite(Number(x))?Number(x):null}
function a24UiMoney(n,q){return a24PlotNumber(n)===null?'Indisponível':new Intl.NumberFormat('pt-PT',{style:'currency',currency:q||'BRL'}).format(n)}
function a24UiPercent(n){return n+'%'} function a24UiAccount(a,q){return a+' · '+q}
function v95CostReferences(){return '<p>Custos por fonte</p>'} function v60CashPlans(){return '<p>Planos existentes</p>'}
function a24PlotSeries(){return []} function v35Render(){} function a24UiMount(){}
`,ctx);
function load(file){const lines=fs.readFileSync(path.join(root,'static',file),'utf8').split('\n');for(let i=0;i<lines.length;i++){if(!/^function \w+\(/.test(lines[i]))continue;for(let j=i;j<lines.length;j++){let script;try{script=new vm.Script(lines.slice(i,j+1).join('\n'))}catch{continue}script.runInContext(ctx);i=j;break}}}
load('dashboard_universal_v35.js');load('experience_panels_v37.js');load('blue_experience_v38.js');load('balance_accounts_v41.js');
const pnl=fs.readFileSync(path.join(root,'static/balance_accounts_v41.js'),'utf8').split('\n');for(let j=0,i=pnl.findIndex(l=>l.startsWith('v40Pnl=function'));i>=0&&i+j<pnl.length;j++){try{new vm.Script(pnl.slice(i,i+j+1).join('\n')).runInContext(ctx);break}catch(e){if(e.name!=='SyntaxError')throw e}}
ctx.d={universal_portfolio:{positions:[{instrument_id:'TEST:ASSET',account_id:'Conta A',currency:'BRL',display_label:'Ativo A',reference_pnl:'-15',reference_market_value:'485',cost_basis:'500',context_status:'EXACT_REGISTERED_CONTEXT',reference_quote_at:new Date().toISOString()},{instrument_id:'TEST:UNKNOWN',account_id:'Conta B',currency:'BRL',display_label:'Sem cotação'}],cash:[],catalog:[]},cockpit_panels:{schema:'porquinho.experience-panels-a24/1.0',execution_authorized:false,global_finance:{current:[{currency:'BRL',account_id:null,pnl:'-15',value:'4985',cash:'4500',invested:'485',pnl_position_count:1,position_count:2,valued_position_count:1,pnl_complete:false,wealth_complete:false,quote_at:new Date().toISOString()}]},global_rule_readings:{rows:[{instrument_id:'TEST:ASSET',account_id:'Conta A',currency:'BRL',action:'VENDA',status:'CURRENT_RULE_READING_NOT_SIZED_RECOMMENDATION'}]},weekly_goal:{},wealth_history:{series:[]}},analysis_coverage:{rows:[{instrument_id:'TEST:ASSET',account_id:'Conta A',currency:'BRL',observation_count:85,research_status:'RESEARCH_FORECAST_COMPUTED_NOT_VALIDATED'}]}};
const run=s=>vm.runInContext(s,ctx);
assert(run('v40Pnl(d)').includes('P/L parcial'));assert(run('v40Pnl(d)').includes('15,00'));
assert(run('v56PositionDecisionPanel(d)').includes('VENDA'));assert(run('v56PositionDecisionPanel(d)').includes('EM ANÁLISE'));
assert(run('v80AnalysisCoverage(d)').includes('data-v35-popup'));assert(run('v38Goal(d)').includes('Meta semanal numérica ainda não publicada'));
run("a24CockpitState.account='Conta B'");assert(!run('v41CurrentPnl(d)'));
run("a24CockpitState.account='';a24CockpitState.currency='EUR'");assert(!run('v41CurrentPnl(d)'));run("a24CockpitState.currency='BRL'");
const html=run("'<div class=\"v37-top\">'+v37Wealth(d)+v38Goal(d)+v40Pnl(d)+'</div><div class=\"v38-main\">'+v37Evolution(d)+v56PositionDecisionPanel(d)+'</div>'+v80AnalysisCoverage(d)");
if(process.env.V118_SCREENSHOT_HTML){const css=['dashboard_universal_v35.css','experience_panels_v37.css','blue_experience_v38.css','balance_accounts_v41.css'].map(p=>fs.readFileSync(path.join(root,'static',p),'utf8')).join('\n');fs.writeFileSync(process.env.V118_SCREENSHOT_HTML,`<html><meta name="viewport" content="width=device-width,initial-scale=1"><style>${css}body{font-family:Arial;background:#031613;color:#cbeafa;margin:16px}button{color:inherit} .v37-top{display:grid;grid-template-columns:1fr 1.3fr 1fr;gap:14px}@media(max-width:650px){.v37-top{grid-template-columns:1fr}}</style><body class="v38-blue"><main class="v38-dashboard">${html}</main></body></html>`)}
console.log('GLOBAL_DASHBOARD_SCOPE_PARTIAL_PNL_EXPLICIT_ACTION_TILES_OK');
