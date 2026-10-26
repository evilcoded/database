const fs=require('fs');
const source=fs.readFileSync('/workspace/database/test_global_dashboard_ui_v118.js','utf8');
const scaffold=source.slice(0,source.indexOf('ctx.d='));
new Function('require',scaffold+`
const run=s=>vm.runInContext(s,ctx);
ctx.d={cockpit_panels:{schema:'porquinho.experience-panels-a24/1.0',execution_authorized:false,
 global_opportunity_readings:{schema:'porquinho.global-opportunity-readings-a24/1.0',status:'GLOBAL_OPPORTUNITY_RULE_READINGS_INSPECTED',execution_authorized:false,rows:[]}}};
const rows=ctx.d.cockpit_panels.global_opportunity_readings.rows;
for(let i=0;i<8;i++)rows.push({instrument_id:'GLOBAL:'+i,asset:i===0?'SOL<script>':'BR'+i,account_id:i===7?'Other':'Nubank',currency:'BRL',position_held:i===0,action:i===1?'COMPRE':'ACOMPANHE',metric_values:{promising_pct:'62.8',risk:'44.2'},provider:'CoinGecko',provider_id:'solana',metric_at:new Date().toISOString(),rule_evaluation:{selected_action:'ACOMPANHE',position_held:true,criteria:[{criterion:'SELL_STRUCTURAL_RISK',matched:false,checks:[{metric:'risk',value:'44.2',threshold:'75',operator:'GE',passed:false}]}]}});
rows.push({instrument_id:'EURONLY',asset:'EUR ONLY',account_id:'N26',currency:'EUR',action:'VENDA'});
ctx.lastStatus={portfolio:{scores:[{asset:'UNSCOPED_LEGACY',action:'COMPRE'}]}};
let html=run('v37TopOpportunities(d)');assert(html.includes('Ver 8 leituras'));assert(!html.includes('EUR ONLY'));assert(!html.includes('UNSCOPED_LEGACY'));assert(html.includes('COMPRA'));assert(html.includes('SOL&lt;script&gt;'));assert(!html.includes('<script>'));
assert.equal((html.match(/class="v118-tile"/g)||[]).length,6);
let popup=run("v35PopupStore.get('v132-opportunity:0').html");assert(popup.includes('44.2'));assert(popup.includes('75'));assert(popup.includes('não atendido'));assert(popup.includes('desde o custo registrado'));assert(popup.includes('não define stop-loss'));assert(popup.includes('CoinGecko'));assert(popup.includes('não confirmada'));
assert.equal((run("v35PopupStore.get('v132-all-opportunities').html").match(/class="v118-tile"/g)||[]).length,8);
run("a24CockpitState.account='Other'");html=run('v37TopOpportunities(d)');assert(html.includes('Other'));assert(!html.includes('Nubank'));assert(!html.includes('Ver 8'));
run("a24CockpitState.account='';a24CockpitState.currency='EUR'");html=run('v37TopOpportunities(d)');assert(html.includes('EUR ONLY'));assert(!html.includes('Nubank'));
run("a24CockpitState.currency='BRL';a24CockpitState.query='NO_MATCH'");assert(run('v37TopOpportunities(d)').includes('Nenhuma alternativa vinculada'));
run("a24CockpitState.query='';a24CockpitState.currency='BRL'");for(const r of rows)r.metric_at=new Date(Date.now()-3600000).toISOString();assert(!run('v37TopOpportunities(d)').includes('COMPRA'));assert(run('v37TopOpportunities(d)').includes('EM ANÁLISE'));
ctx.d.cockpit_panels.global_opportunity_readings.status='UNAVAILABLE';assert(run('v37TopOpportunities(d)').includes('indisponíveis'));assert(!run('v37TopOpportunities(d)').includes('UNSCOPED_LEGACY'));
console.log('GLOBAL_OPPORTUNITY_NATIVE_SCOPE_CLICK_DETAILS_TRACE_NO_LEGACY_FALLBACK_OK');
`)(require);
