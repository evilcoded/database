const fs=require('fs');
const source=fs.readFileSync('/workspace/database/test_review_click_dom_v130.js','utf8');
new Function('require',source.slice(0,source.indexOf('const tick='))+`
const s=setup();s.run("v35Init()");
s.run(
 "a24CockpitState.currency='BRL';a24CockpitState.account='';var globalTest={cockpit_panels:{schema:'porquinho.experience-panels-a24/1.0',execution_authorized:false,global_opportunity_readings:{schema:'porquinho.global-opportunity-readings-a24/1.0',status:'GLOBAL_OPPORTUNITY_RULE_READINGS_INSPECTED',execution_authorized:false,rows:[{instrument_id:'SOL',asset:'SOL',account_id:'A',currency:'BRL',position_held:true,action:'ACOMPANHE',metric_values:{promising_pct:'62.8',risk:'44.2'},provider:'CoinGecko',provider_id:'solana',metric_at:new Date().toISOString(),rule_evaluation:{selected_action:'ACOMPANHE',position_held:true,criteria:[{criterion:'SELL_STRUCTURAL_RISK',matched:false,checks:[{metric:'risk',value:'44.2',threshold:'75',operator:'GE',passed:false}]}]}}]}}};v35Modal('Global opportunities',v37TopOpportunities(globalTest));"
);
assert.equal(s.run('v37TopOpportunities===v39TopOpportunities'),true,'Test the real override loaded after the new renderer');
const button=s.w.document.querySelector('.v118-tile[data-v35-popup]');assert(button,'The full script stack must render the native opportunity card');assert(button.textContent.includes('SOL'));button.click();
assert(s.w.document.body.textContent.includes('Venda por risco'));assert(s.w.document.body.textContent.includes('não define stop-loss'));const criterion=[...s.w.document.querySelectorAll('button[data-v35-popup]')].find(b=>b.textContent.includes('Venda por risco'));assert(criterion);criterion.click();assert(s.w.document.body.textContent.includes('44.2'));assert(s.w.document.body.textContent.includes('75'));assert(s.w.document.body.textContent.includes('não atendido'));
assert.equal(s.requests.filter(r=>r.options?.method==='POST').length,0);assert.deepEqual(s.errors,[]);
s.run('v39Back();v39Back()');assert(s.w.document.querySelector('.v118-tile[data-v35-popup]'),'Back returns to the scoped cards');s.dom.window.close();
console.log('FULL_SCRIPT_NATIVE_OPPORTUNITY_CARD_CLICK_CRITERIA_AND_BACK_OK');
`)(require);
