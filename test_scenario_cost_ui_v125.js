const fs=require('fs'),path=require('path');
const base=fs.readFileSync(path.join(__dirname,'test_global_dashboard_ui_v118.js'),'utf8');
new Function('require','process',base+`
const original=run('v37Wealth(d)');ctx.d.cash_plan_visibility={contexts:[{account_id:'Conta A',currency:'BRL',learned_scenario_transport:{scenarios:[{reviewed_pretrade_cost_projection:{execution_authorized:false,status:'REVIEWED_PURCHASE_COSTS_ATTACHED_NOT_COMPARATOR_VALIDATED',cost_arithmetic_available:true,purchase_execution_cost_estimate:'0.60',reference_budget_covers_allocation_costs_and_preserved_cash:false,legs:[{instrument_id:'TEST:ASSET',reference_amount:'100',status:'REVIEWED_PRETRADE_COST_ESTIMATE_NOT_VALIDATED'}]}}]}},{account_id:'EU',currency:'EUR',learned_scenario_transport:{scenarios:[{reviewed_pretrade_cost_projection:{execution_authorized:false,cost_arithmetic_available:true,purchase_execution_cost_estimate:'999',legs:[{instrument_id:'EU_ONLY'}]}}]}}]};
let details=run('v125ReviewedCosts(d)');assert(details.includes('0,60'));assert(details.includes('ultrapassam'));assert(!details.includes('EU_ONLY'));assert(details.includes('não some'));assert.equal(run('v37Wealth(d)'),original);
const p=ctx.d.cash_plan_visibility.contexts[0].learned_scenario_transport.scenarios[0].reviewed_pretrade_cost_projection;p.cost_arithmetic_available=false;p.purchase_execution_cost_estimate=null;p.legs[0].status='PARTIAL_COST_EVIDENCE';p.legs[0].estimate={missing_components:['taxes']};details=run('v125ReviewedCosts(d)');assert(details.includes('tributos'));assert(!details.includes('Custo de compra revisado:'));
run("a24CockpitState.account='OTHER'");assert.equal(run('v125ReviewedCosts(d)'),'');
console.log('SCENARIO_REVIEWED_COST_KNOWN_UNKNOWN_SCOPE_BUDGET_WARNING_LAYOUT_OK');
`)(require,process);
