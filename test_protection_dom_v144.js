const fs=require('fs');
const fixture=fs.readFileSync('/workspace/database/test_review_click_dom_v130.js','utf8');
new Function('require',fixture.slice(0,fixture.indexOf('const tick='))+`
const s=setup();s.run('v35Init()');
s.run("a24ExplicitFilters=true;a24CockpitState.currency='EUR';a24CockpitState.account='A';a24CockpitState.query='';var nowProtection=new Date().toISOString();var p144={instrument_id:'ETH',display_label:'ETH',account_id:'A',currency:'EUR',reference_market_value:'81',reference_pnl:'-19',reference_pnl_pct:'-19',cost_basis:'100',reference_quote_at:nowProtection,context_status:'EXACT_REGISTERED_CONTEXT'};var r144={...p144,quote_at:nowProtection,alert:true,pnl_amount:'-19',pnl_pct:'-19',recovery_to_recorded_cost_pct:'23.45679',selected_action:'ACOMPANHE',current_rule_evaluation_available:true,sell_risk_condition:{matched:false},sell_thesis_condition:{matched:false,daily_confirmation:false}};var d144={universal_portfolio:{schema:'porquinho.universal-cockpit-a24/1.0',status:'UNIVERSAL_FACTS_PROJECTED',cross_currency_aggregation:false,execution_authorized:false,positions:[p144],cash:[],catalog:[],accounts:[]},cockpit_panels:{schema:'porquinho.experience-panels-a24/1.0',execution_authorized:false,capital_protection:{rows:[r144]},global_rule_readings:{rows:[{...p144,action:'ACOMPANHE',metric_at:nowProtection}],thresholds:{sell_structural_risk:75,sell_max_promising:50}}}};v35Modal('Decisions',v35Pending(d144));");
const body=s.w.document.getElementById('modalBody'),card=body.querySelector('[data-v35-popup="v118-position:0"]');
assert(card);assert(card.textContent.includes('Revisar proteção'));assert(card.textContent.includes('ACOMPANHE'));assert(!card.textContent.includes('VENDA'));
card.click();assert(body.textContent.includes('Revisar proteção do capital'));assert(body.textContent.includes('23,46'));assert(body.textContent.includes('não é uma recomendação de MANTENHA'));assert(body.textContent.includes('dois dias completos'));
s.run("r144.account_id='OTHER'");assert.equal(s.run('v144ProtectionBadge(p144,d144)'), '');
s.run("r144.account_id='A';r144.currency='BRL'");assert.equal(s.run('v144ProtectionBadge(p144,d144)'), '');
s.run("r144.currency='EUR';r144.quote_at=new Date(Date.now()-3600000).toISOString()");assert.equal(s.run('v144ProtectionBadge(p144,d144)'), '');
assert.equal(s.requests.filter(r=>r.options?.method==='POST').length,0);assert.deepEqual(s.errors,[]);s.dom.window.close();
console.log('LOSS_REVIEW_BADGE_CLICK_RECOVERY_RULE_REASON_SCOPE_AND_EXPIRY_WITHOUT_SELL_OR_POST_OK');
`)(require);
