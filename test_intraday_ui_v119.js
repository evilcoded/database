const fs=require('fs'),path=require('path');
const base=fs.readFileSync(path.join(__dirname,'test_global_dashboard_ui_v118.js'),'utf8');
new Function('require','process',base+`
const time=Date.now(),one=new Date(time-600000).toISOString(),two=new Date(time).toISOString();
ctx.d.cockpit_panels.global_finance.current[0].pnl_population_fingerprint='POPULATION';
ctx.d.cockpit_panels.global_finance.intraday=[{currency:'BRL',account_id:null,points:[{date:one,pnl:'-10',pnl_population_fingerprint:'POPULATION',pnl_position_count:1,position_count:2},{date:two,pnl:'-15',pnl_population_fingerprint:'POPULATION',pnl_position_count:1,position_count:2}]}];
ctx.d.cockpit_panels.global_finance.changes=[{currency:'BRL',account_id:null,observed_at:two,value:'-5',interval_seconds:600,pnl_population_fingerprint:'POPULATION'}];
assert.equal(run('v119Intraday(d,"BRL").count'),2);assert(run('v40Pnl(d)').includes('<svg'));assert(run('v40Pnl(d)').includes('5,00'));assert.equal(run('v119Intraday(d,"EUR").count'),0);
ctx.d.cockpit_panels.global_finance.current[0].pnl_population_fingerprint='NEW_POPULATION';assert.equal(run('v119Intraday(d,"BRL").delta'),null);
run("a24CockpitState.query='Ativo'");assert.equal(run('v119Intraday(d,"BRL").count'),0);
console.log('INTRADAY_CURVE_DELTA_SCOPE_AND_POPULATION_OK');
`)(require,process);
