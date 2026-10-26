const fs=require('fs'),path=require('path');
const base=fs.readFileSync(path.join(__dirname,'test_global_dashboard_ui_v118.js'),'utf8');
const check=String.raw`
return (async()=>{
 const source=fs.readFileSync(path.join(root,'static/experience_panels_v37.js'),'utf8'),start=source.indexOf('async function v129OpenCostReview('),end=source.indexOf("\ndocument.addEventListener('click',event=>",start);
 new vm.Script(source.slice(start,end)).runInContext(ctx);
 const handlers={},status={textContent:''},button={disabled:false},fields={venue:{value:'Bank account application'},source_kind:{value:'OFFICIAL_PRETRADE_QUOTE'},source_ref:{value:'Explicit bank preview'},observed_at:{value:'2026-01-15T11:00:00+01:00'},valid_until:{value:'2026-01-15T12:00:00+01:00'},confirmed:{checked:true}};
 const names=['brokerage','exchange_fees','spread','slippage','taxes','other_costs'];
 for(const name of names){fields['status_'+name]={value:'UNKNOWN'};fields['amount_'+name]={value:'',disabled:true};}
 const form={elements:fields,addEventListener:(type,fn)=>handlers[type]=fn,querySelector:q=>q==='#v129-cost-status'?status:button};
 ctx.document={getElementById:()=>form};let html='',calls=[],refreshed=0;
 ctx.openModal=(title,body)=>html=body;ctx.r21386ls19aMutationHeaders=async()=>({'X-Porquinho-Session':'synthetic-session'});ctx.a24FetchMonitor=()=>refreshed++;
 ctx.scope={account_id:'A',currency:'BRL',instrument_id:'I',reference_amount:'100',label:'Asset'};
 ctx.fetch=async(url,options)=>{calls.push({url,options});return {ok:true,json:async()=>options?{financial_mutation:false,execution_authorized:false,model_validation_proven:false}:{cases:[{...ctx.scope,case_id:'case',review_context_digest:'digest',account_label:'Bank account'}]}};};
 await run('v129OpenCostReview(scope)');assert(html.includes('Desconhecido'));assert(!html.includes('value="0"'));assert(html.includes('Não é compra'));
 fields.status_brokerage.value='KNOWN';handlers.change({target:{dataset:{v129Component:'brokerage'},value:'KNOWN'}});assert.equal(fields.amount_brokerage.disabled,false);fields.amount_brokerage.value='0';
 await handlers.submit({preventDefault(){}});
 assert.equal(calls.length,2);assert.equal(calls[1].url,'/api/research/cost-reviews');const payload=JSON.parse(calls[1].options.body);
 assert.equal(payload.components.brokerage.amount,'0');assert.equal(payload.components.taxes.status,'UNKNOWN');assert.equal(payload.components.taxes.amount,null);assert.equal(payload.observed_at,'2026-01-15T10:00:00.000Z');assert.equal(payload.reference_amount,undefined);assert.equal(payload.authority,undefined);assert.equal(refreshed,1);assert.equal(button.disabled,true);assert(status.textContent.includes('nenhuma compra'));
 fields.amount_brokerage.value='-1';await handlers.submit({preventDefault(){}});assert.equal(calls.length,2);assert.equal(button.disabled,false);
 console.log('REAL_REVIEW_FORM_EXPLICIT_ZERO_UNKNOWN_TIMEZONE_SESSION_NO_BROKER_REQUEST_OK');
})();
`;
new Function('require','process',base+check)(require,process).catch(e=>{console.error(e);process.exitCode=1;});
