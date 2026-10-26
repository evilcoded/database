const fs=require('fs');
const source=fs.readFileSync('/workspace/database/test_review_click_dom_v130.js','utf8');
new Function('require',source.slice(0,source.indexOf('const tick='))+`
const s=setup();s.run('v35Init()');
s.run("a24ExplicitFilters=true;a24CockpitState.currency='';a24CockpitState.account='';a24CockpitState.query='';var allCurrencyTest={cockpit_panels:{schema:'porquinho.experience-panels-a24/1.0',execution_authorized:false,global_opportunity_readings:{schema:'porquinho.global-opportunity-readings-a24/1.0',status:'GLOBAL_OPPORTUNITY_RULE_READINGS_INSPECTED',execution_authorized:false,rows:[]}}};for(const q of ['BRL','EUR'])for(let i=0;i<8;i++)allCurrencyTest.cockpit_panels.global_opportunity_readings.rows.push({instrument_id:q+':'+i,asset:q+' ASSET '+i,account_id:'Account '+q,currency:q,provider:'Source '+q,provider_id:'id'+i,action:'ACOMPANHE',metric_at:new Date().toISOString(),metric_values:{promising_pct:'64',risk:q==='EUR'?'38':'44'}});v35Modal('Opportunities',v37TopOpportunities(allCurrencyTest));");
const body=()=>s.w.document.getElementById('modalBody');
assert.equal(body().querySelectorAll('.v37-top-opp').length,2,'All currencies must render separate sections, not an empty currency filter');
assert(body().textContent.includes('Oportunidades · BRL'));assert(body().textContent.includes('Oportunidades · EUR'));
assert.equal(body().querySelectorAll('.v118-tile').length,12);assert.equal(s.run('a24CockpitState.currency'),'','Rendering must not change the saved filter');
for(const q of ['BRL','EUR']){
 const button=body().querySelector('[data-v35-popup="v132-opportunity:'+q+':0"]');assert(button);button.click();assert(body().textContent.includes('Source '+q),'Each currency card must retain its own popup data');assert(!body().textContent.includes('Source '+(q==='EUR'?'BRL':'EUR')));s.run('v39Back()');
 const expand=body().querySelector('[data-v35-popup="v132-all-opportunities:'+q+'"]');assert(expand);expand.click();assert.equal(body().querySelectorAll('.v118-tile').length,8);assert(body().textContent.includes(q+' ASSET 7'));assert(!body().textContent.includes((q==='EUR'?'BRL':'EUR')+' ASSET'));s.run('v39Back()');
}
s.run("a24CockpitState.account='Account BRL';v35Modal('Account filter',v37TopOpportunities(allCurrencyTest));");assert.equal(body().querySelectorAll('.v37-top-opp').length,1);assert(!body().textContent.includes('EUR ASSET'));
s.run("a24CockpitState.account='';a24CockpitState.query='EUR ASSET';v35Modal('Search filter',v37TopOpportunities(allCurrencyTest));");assert.equal(body().querySelectorAll('.v37-top-opp').length,1);assert(!body().textContent.includes('BRL ASSET'));
s.run("a24CockpitState.query='NO SUCH ASSET';v35Modal('No match',v37TopOpportunities(allCurrencyTest));");assert(body().textContent.includes('Nenhuma alternativa vinculada'));
assert.equal(s.requests.filter(r=>r.options?.method==='POST').length,0);assert.deepEqual(s.errors,[]);s.dom.window.close();
console.log('ALL_CURRENCIES_SEPARATE_GROUPS_COUNTS_POPUPS_FILTERS_AND_BACK_OK');
`)(require);
