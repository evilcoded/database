/* Entirely synthetic, native-currency presentation controls; no user data. */
function dashboardFixture147(){
 const now='2026-10-30T21:00:00+00:00',positions=[],cash=[],catalog=[],rows=[],current=[],history=[],intraday=[];
 for(const [q,aid,start] of [['EUR','CONTROL_E',1000],['BRL','CONTROL_B',5000]]){
  cash.push({account_id:aid,currency:q,amount:String(start-100),context_status:'EXACT_REGISTERED_CONTEXT'});
  positions.push({instrument_id:'GLOBAL:CRYPTO:CRYPTO:ETH',display_label:'ETH',account_id:aid,currency:q,quantity:'1',cost_basis:'120',reference_market_value:'100',reference_pnl:'-20',reference_pnl_pct:'-16.666',reference_quote_at:now,context_status:'EXACT_REGISTERED_CONTEXT'});
  current.push({currency:q,account_id:null,value:start,invested:100,cash:start-100,wealth_complete:true,position_count:1,valued_position_count:1,pnl:-20,pnl_complete:true,pnl_position_count:1,quote_at:now});
  history.push({currency:q,account_id:null,scope:'OBSERVED_GLOBAL_PORTFOLIO',points:[0,1,2].map((i)=>({date:'2026-10-'+(28+i)+'T12:00:00+00:00',value:start-30+i*15,cash:start-100,coverage_fingerprint:q}))});
  intraday.push({currency:q,account_id:null,points:[0,1,2].map(i=>({date:'2026-10-30T20:'+String(40+i*10).padStart(2,'0').replace('60','00')+':00+00:00',pnl:-24+i*2,position_count:1,pnl_position_count:1,pnl_population_fingerprint:q,coverage_fingerprint:q}))});
  intraday.at(-1).points[2].date=now;
  for(const kind of ['CRYPTO','EQUITY'])for(let i=0;i<5;i++){
   const symbol=(kind==='CRYPTO'?'C':'S')+(i+1),id=(kind==='CRYPTO'?'GLOBAL:CRYPTO:CRYPTO:':'CONTROL:MARKET:EQUITY:')+symbol;
   if(!catalog.some(c=>c.instrument_id===id))catalog.push({instrument_id:id,symbol,asset_class:kind,catalog_status:'GLOBAL_CATALOG_REGISTERED'});
   rows.push({account_id:aid,currency:q,instrument_id:id,asset:symbol,provider:kind==='CRYPTO'?'CoinGecko':'CONTROL',provider_id:symbol,position_held:false,action:'ACOMPANHE',metric_at:now,metric_generation:'COMMON_NATIVE_PRICE_INDEX_V1',metric_values:{promising_pct:String(85-i-(q==='EUR'?1:0)),risk:'35',entry:'71',asymmetry:'75',reversal_risk:'30'}});
  }
 }
 return {schema:'porquinho.monitor-consolidation-a24/1.0',observed_at:now,monitor:{snapshot:{at:now},state:'WAITING_FOR_CADENCE',heartbeat_recent:true},universal_portfolio:{schema:'porquinho.universal-cockpit-a24/1.0',status:'UNIVERSAL_FACTS_PROJECTED',cross_currency_aggregation:false,execution_authorized:false,positions,cash,catalog,accounts:[{account_id:'CONTROL_E',currency:'EUR',name:'Conta de controle EUR',institution_name:'Controle'},{account_id:'CONTROL_B',currency:'BRL',name:'Conta de controle BRL',institution_name:'Controle'}]},cockpit_intraday:{observed_at:now,series:[]},cockpit_panels:{schema:'porquinho.experience-panels-a24/1.0',execution_authorized:false,global_finance:{current,changes:[]},wealth_history:{series:history},observed_finance_intraday:{schema:'porquinho.observed-finance-intraday-a24/1.0',financial_mutation:false,observed_at:now,series:intraday},weekly_goal:{targets:[],brain_previews:[]},global_opportunity_readings:{schema:'porquinho.global-opportunity-readings-a24/1.0',status:'GLOBAL_OPPORTUNITY_RULE_READINGS_INSPECTED',execution_authorized:false,rows},global_rule_readings:{rows:[]},capital_protection:{rows:[]},global_operational_learning:{issue_count:12,horizon_status_counts:{'30:PENDING':12}}}};
}
if(typeof module!=='undefined')module.exports=dashboardFixture147;
