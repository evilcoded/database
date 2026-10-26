/* Real DOM, complete local scripts, nested modal serialization, pending HTTP. */
const assert=require('assert'),fs=require('fs'),path=require('path'),vm=require('vm'),{JSDOM,VirtualConsole}=require('jsdom');
const root=process.env.PORQUINHO_PROJECT||process.cwd(),html=fs.readFileSync(path.join(root,'templates/index.html'),'utf8');
function setup(){
 const vc=new VirtualConsole(),dom=new JSDOM(html,{url:'http://127.0.0.1:8765',runScripts:'outside-only',virtualConsole:vc}),w=dom.window;
 const run=s=>new vm.Script(s).runInContext(dom.getInternalVMContext()),timers=new Map(),pending=[],requests=[],errors=[];let timerId=0;
 const add=w.document.addEventListener.bind(w.document);w.document.addEventListener=(type,listener,options)=>{if(type!=='DOMContentLoaded')add(type,listener,options)};
 Object.defineProperty(w.document,'readyState',{get:()=> 'loading'});
 w.setInterval=()=>1;w.setTimeout=(fn,ms)=>{timers.set(++timerId,{fn,ms});return timerId};w.clearTimeout=id=>timers.delete(id);w.requestAnimationFrame=()=>1;w.scrollTo=()=>{};w.HTMLElement.prototype.scrollTo=function(){};
 w.Chart=class{destroy(){}update(){}};w.Chart.defaults={};w.addEventListener('error',e=>errors.push(e.message));
 w.fetch=(url,options)=>{
  requests.push({url,options});
  if(url==='/api/research/cost-reviews/cases')return new Promise((resolve,reject)=>{pending.push({resolve,reject});options?.signal?.addEventListener('abort',()=>reject(new w.DOMException('Timeout','AbortError')));});
  if(url==='/api/security/local-human/bootstrap')return Promise.resolve({ok:true,json:async()=>({session_id:'synthetic-session',mutation_token:'synthetic-token'})});
  if(url==='/api/research/cost-reviews')return Promise.resolve({ok:true,json:async()=>({financial_mutation:false,execution_authorized:false,model_validation_proven:false})});
  return new Promise(()=>{});
 };
 for(const match of html.matchAll(/<script[^>]+src="(\/static\/[^"?]+)/g)){
  const file=process.env.PORQUINHO_REVIEW_SCRIPT&&match[1]==='/static/experience_panels_v37.js'?process.env.PORQUINHO_REVIEW_SCRIPT:path.join(root,match[1]);
  run(fs.readFileSync(file,'utf8'));
 }
 run(`a24CockpitState.currency='EUR';a24CockpitState.account='A';var testData={universal_portfolio:{catalog:[]},cash_plan_visibility:{contexts:[{account_id:'A',currency:'EUR',learned_scenario_transport:{scenarios:[{reviewed_pretrade_cost_projection:{execution_authorized:false,legs:[{side:'BUY',instrument_id:'BTC',reference_amount:'1'}]}}]}}]}};v35Modal('Costs',v125ReviewedCosts(testData));var popup=v35PopupStore.get(document.querySelector('[data-v35-popup]').dataset.v35Popup);v35Modal(popup.title,popup.html);`);
 return {dom,w,run,timers,pending,requests,errors,click:()=>w.document.querySelector('[data-v129-review]').click(),respond:()=>pending.at(-1).resolve({ok:true,json:async()=>({cases:[{account_id:'A',currency:'EUR',instrument_id:'BTC',reference_amount:'1',case_id:'case',review_context_digest:'digest',account_label:'Bank account'}]})})};
}
const tick=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
 let s=setup();s.click();assert(s.w.document.getElementById('v130-review-loading'),'Click must display feedback before the server responds');assert.equal(s.pending.length,1);assert.equal(s.requests.filter(r=>r.url==='/api/research/cost-reviews').length,0);
 s.respond();await tick();const form=s.w.document.getElementById('v129-cost-form');assert(form);assert(!s.w.document.getElementById('v130-review-loading'));
 for(const [name,value] of Object.entries({venue:'Bank app',source_ref:'Documented quote',observed_at:'2026-01-15T11:00:00+01:00',valid_until:'2026-01-15T12:00:00+01:00'}))form.elements[name].value=value;
 form.elements.status_brokerage.value='KNOWN';form.elements.status_brokerage.dispatchEvent(new s.w.Event('change',{bubbles:true}));form.elements.amount_brokerage.value='0';form.elements.confirmed.checked=true;
 form.dispatchEvent(new s.w.Event('submit',{bubbles:true,cancelable:true}));await tick();await tick();const posts=s.requests.filter(r=>r.url==='/api/research/cost-reviews');assert.equal(posts.length,1);const saved=JSON.parse(posts[0].options.body);assert.equal(saved.components.brokerage.amount,'0');assert.equal(saved.components.taxes.amount,null);assert(posts[0].options.headers['X-Porquinho-Mutation-Token']);assert(s.w.document.getElementById('v129-cost-status').textContent.includes('registrada'));assert.deepEqual(s.errors,[]);s.run('v39Back()');assert(s.w.document.querySelector('[data-v129-review]'));s.dom.window.close();
 s=setup();s.click();s.run('v39Back()');s.respond();await tick();assert(!s.w.document.getElementById('v129-cost-form'),'Late response must not reopen a form after Back');assert(s.w.document.querySelector('[data-v129-review]'));s.dom.window.close();
 s=setup();s.click();const deadline=[...s.timers.values()].find(t=>t.ms===45000);assert(deadline);deadline.fn();await tick();assert(s.w.document.querySelector('[role=alert]').textContent.includes('demorou'));assert.equal(s.requests.filter(r=>r.url==='/api/research/cost-reviews').length,0);s.dom.window.close();
 console.log('FULL_SCRIPT_DOM_CLICK_LOADING_REVIEW_SUBMIT_BACK_TIMEOUT_NO_SILENT_WAIT_OK');
})().catch(e=>{console.error(e);process.exitCode=1;});
