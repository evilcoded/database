const fs=require('fs'),path=require('path');
const base=fs.readFileSync(path.join(__dirname,'test_global_dashboard_ui_v118.js'),'utf8');
new Function('require','process',base+`
assert.equal(run("v129CostDecimal('0')"),'0');assert.equal(run("v129CostDecimal('00')"),'00');assert.equal(run("v129CostDecimal('0,10')"),'0.10');assert.equal(run("v129CostDecimal('12345678901234567890.00000000000000000001')"),'12345678901234567890.00000000000000000001');
for(const value of ['','-1','NaN','Infinity','1e3','1.000,00']){ctx.bad=value;assert.throws(()=>run('v129CostDecimal(bad)'));}
const original=run('v37Wealth(d)');ctx.r={side:'BUY',instrument_id:'TEST:ASSET',reference_amount:'100'};ctx.c={account_id:'Conta A',currency:'BRL'};
assert(run("v129CostReviewButton(r,c,'Ativo')").includes('Revisar custos'));
ctx.r.reference_amount=null;assert.equal(run("v129CostReviewButton(r,c,'Ativo')"),'');
ctx.c.research_enabled=true;ctx.c.capital_status='ACTIVE_BUDGETS_EXCEED_CURRENT_CASH';ctx.c.research_context_status='MARKET_RESEARCH_ONLY_CAPITAL_RECONCILIATION_PENDING';ctx.c.research_capital_reconciliation={reference_capital:'40',declared_budget_amount:'50'};
const text=run('v111CashResearchStatus(c)');assert(text.includes('40,00'));assert(text.includes('50,00'));assert(text.includes('nenhum saldo ou plano foi reescrito'));assert.equal(run('v37Wealth(d)'),original);
console.log('EXPLICIT_ZERO_DECIMAL_PRECISION_REVIEW_BUTTON_CASH_REFERENCE_NO_WEALTH_REGRESSION_OK');
`)(require,process);
