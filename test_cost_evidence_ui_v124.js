const fs=require('fs'),path=require('path');
const base=fs.readFileSync(path.join(__dirname,'test_global_dashboard_ui_v118.js'),'utf8');
new Function('require','process',base+`
const before=run('v37Wealth(d)');ctx.d.reported_pretrade_preview_inventory={schema:'porquinho.reported-preview-inventory-a24/1.0',execution_authorized:false,financial_mutation:false,rows:[{account_id:'Conta A',currency:'BRL',instrument_id:'TEST:ASSET',reference_amount:'1000',explicit_commission:'0',total_debit:'1000',current_account_scope_matches:true,recorded_at:new Date().toISOString()},{account_id:'Conta EU',currency:'EUR',instrument_id:'EU_ONLY',reference_amount:'12',explicit_commission:'2',total_debit:'14'}]};
ctx.d.universal_portfolio.accounts=[{account_id:'Conta A',currency:'BRL',pricing_plan:'PLAN <unsafe>'}];
ctx.d.cash_plan_visibility={contexts:[{account_id:'Conta A',currency:'BRL',learned_scenario_transport:{scenarios:[{documentary_cost_projection:{status:'ROUTE_SPECIFIC_COMPONENTS_PENDING',legs:[{instrument_id:'TEST:ASSET',status:'EXACT_ROUTE_POLICY_REQUIRED',route_blocking_reasons:['INSTRUMENT_NOT_COVERED_BY_TARIFF_DOCUMENT'],total_cost:null}]}}]}}]};
let evidence=run('v95CostReferences(d)');assert(evidence.includes('Prévias relatadas'));assert(evidence.includes('Comissão informada'));assert(evidence.includes('0,00'));assert(evidence.includes('Tarifa aplicável ainda não documentada'));assert(evidence.includes('PLAN &lt;unsafe&gt;'));assert(!evidence.includes('EU_ONLY'));assert.equal(run('v37Wealth(d)'),before);
run("a24CockpitState.account='OTHER'");assert(!run('v124CostEvidence(d)').includes('Comissão informada'));
console.log('PREVIEW_WITHOUT_SCENARIO_ROUTE_CONTEXT_SCOPE_ESCAPING_LAYOUT_PRESERVED_OK');
`)(require,process);
