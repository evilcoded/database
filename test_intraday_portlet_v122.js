const fs=require('fs'),path=require('path');
const base=fs.readFileSync(path.join(__dirname,'test_global_dashboard_ui_v118.js'),'utf8');
new Function('require','process',base+`
vm.runInContext("var v40State={minutes:1440},v122IntradayState={mode:'portfolio'},v122LegacyIntraday=()=>'<section class=\\\"legacy-quotes\\\">Existing quote chart</section>'",ctx);
load('intraday_dashboard_v40.js');
const now=Date.now();ctx.d.cockpit_panels.observed_finance_intraday={schema:'porquinho.observed-finance-intraday-a24/1.0',financial_mutation:false,observed_at:new Date(now).toISOString(),series:[{currency:'BRL',account_id:null,points:Array.from({length:6},(_,i)=>({date:new Date(now-(5-i)*600000).toISOString(),pnl:String(-20-i),pnl_position_count:1,position_count:2,pnl_population_fingerprint:'POP',coverage_fingerprint:'COVER'}))},{currency:'EUR',account_id:null,points:[{date:new Date(now).toISOString(),pnl:'99999',pnl_population_fingerprint:'OTHER',coverage_fingerprint:'OTHER'}]}]};
const before=run('v37Wealth(d)');let chart=run('v122Intraday(d)');assert(chart.includes('<svg'));assert(chart.includes('6 leituras'));assert(!chart.includes('EUR'));assert.equal(run('v122ObservedSeries(d).currency'),'BRL');assert.equal(run('v37Wealth(d)'),before);
run("v40State.minutes=30");chart=run('v122Intraday(d)');assert(chart.includes('4 leituras'));
run("a24CockpitState.account='NoHistory'");assert(!run('v122Intraday(d)').includes('<svg'));run("a24CockpitState.account='';v122IntradayState.mode='quotes'");assert(run('v122Intraday(d)').includes('Existing quote chart'));
console.log('EXISTING_INTRADAY_PORTLET_OBSERVED_PNL_QUOTES_SCOPE_AND_LAYOUT_UNCHANGED_OK');
`)(require,process);
