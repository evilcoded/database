const fs=require('fs'),path=require('path');
const base=fs.readFileSync(path.join(__dirname,'test_global_dashboard_ui_v118.js'),'utf8');
new Function('require','process',base+`
ctx.d.cockpit_panels.wealth_history.series=[{currency:'BRL',account_id:null,scope:'OBSERVED_GLOBAL_PORTFOLIO',points:[{date:'2026-10-23T12:00:00Z',value:'5000',coverage_fingerprint:'SAME'},{date:'2026-10-24T12:00:00Z',value:'4975',coverage_fingerprint:'SAME'}]},{currency:'EUR',account_id:null,scope:'OBSERVED_GLOBAL_PORTFOLIO',points:[{date:'2026-10-23T12:00:00Z',value:'99999'}]}];
let sparkHtml=run('v37Wealth(d)');assert(sparkHtml.includes('v120-wealth-spark'));assert(sparkHtml.includes('<path'));assert(!sparkHtml.includes('99999'));assert(sparkHtml.indexOf('v120-wealth-spark')<sparkHtml.indexOf('v37-submetrics'));
ctx.d.cockpit_panels.wealth_history.series[0].points[1].coverage_fingerprint='CHANGED';sparkHtml=run('v37Wealth(d)');assert(sparkHtml.includes('<circle'));assert(!sparkHtml.includes('<path'));
run("a24CockpitState.account='Conta B'");sparkHtml=run('v120WealthSpark(d)');assert(!sparkHtml.includes('<svg'));assert(sparkHtml.includes('sem leituras'));
run("a24CockpitState.account='';a24CockpitState.query='Ativo'");assert(!run('v120WealthSpark(d)').includes('<svg'));
console.log('WEALTH_SPARK_RESTORED_SCOPED_NO_COVERAGE_INTERPOLATION_OK');
`)(require,process);
