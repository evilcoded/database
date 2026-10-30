const fs=require('fs');
const fixture=fs.readFileSync('/workspace/database/test_review_click_dom_v130.js','utf8');
new Function('require',fixture.slice(0,fixture.indexOf('const tick='))+`
const s=setup();s.run('v35Init()');
s.run("var trace145={input_status:'CURRENT_RULE_INPUTS_AVAILABLE',selected_action:'COMPRE',rule_criteria:[{criterion:'BUY',matched:true,checks:[{metric:'promising_pct',operator:'GE',value:'80',threshold:'75',passed:true},{metric:'risk',operator:'LE',value:'35',threshold:'50',passed:true}]}],sizing_status:'PENDING',blocking_reasons:['COMPLETE_ACCOUNT_VALUATION_REQUIRED']};var row145={instrument_id:'TEST',account_id:'A',currency:'BRL',action:'COMPRE',reference_amount:null,decision_path:trace145};var context145={account_id:'A',currency:'BRL',action_counts:{COMPRE:1},rows:[row145,{instrument_id:'OTHER',action:null,decision_path:{rule_criteria:[],blocking_reasons:['EXACT_NATIVE_DAILY_HISTORY_REQUIRED']}}],decision_pipeline:{total_count:2,current_reading_count:1,input_pending_count:1,buy_signal_count:1,funded_buy_count:0,buy_sizing_pending_count:1}};var data145={cockpit_panels:{schema:'porquinho.experience-panels-a24/1.0',execution_authorized:false,global_operational_plan:{status:'CURRENT_ORIGINAL_OPERATIONAL_PLANS_COMPOSED',contexts:[context145]}}};a24CockpitState.account='';v35Modal('Plan',v137PlanButton(data145,'BRL'));");
const body=s.w.document.getElementById('modalBody');body.querySelector('[data-v35-popup]').click();
assert(body.textContent.includes('Leituras atuais: 1 de 2'));assert(body.textContent.includes('Sinais de COMPRA: 1'));assert(body.textContent.includes('Com valor de referência: 0'));
body.querySelector('[data-v35-popup]').click();
const rows=[...body.querySelectorAll('[data-v35-popup]')];assert.equal(rows.length,2);
rows[1].click();assert(body.textContent.includes('Histórico diário na moeda do ativo pendente'));s.run('v39Back()');
body.querySelector('[data-v35-popup]').click();assert(body.textContent.includes('Avaliação completa da conta pendente'));
body.querySelector('[data-v35-popup]').click();assert(body.textContent.includes('80 ≥ 75'));assert(body.textContent.includes('35 ≤ 50'));
assert(!body.textContent.includes('undefined'));assert.equal(s.requests.filter(r=>r.options?.method==='POST').length,0);
s.run("v35Modal('Row',v137OperationalDetails(row145,data145))");assert(body.textContent.includes('COMPRA'));assert(body.textContent.includes('Avaliação completa da conta pendente'));assert.deepEqual(s.errors,[]);s.dom.window.close();
console.log('DECISION_CRITERIA_CLICK_BUY_SIGNAL_VS_AMOUNT_PENDING_SOURCE_COVERAGE_AND_NO_POST_OK');
`)(require);
