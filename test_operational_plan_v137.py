import ast,base64,copy,datetime as dt,json,random,unittest
from pathlib import Path
import numpy as np
import test_global_dashboard_v118 as old
from universal_portfolio import operational_decision_core_a24 as core
from universal_portfolio import global_action_readings_a24 as readings
from universal_portfolio import global_operational_plan_a24 as plans

NOW=old.NOW
CFG={'action_rules':old.CFG,'max_positions':5,'position_sizing':{'max_position_pct':25}}

def metric(i='ASSET',q='BRL',score=80,risk=35,**kw):
    return {**old.metrics(q,risk,score),'provider_id':i,'asset':i,'opportunity':80,**kw}

def cash(a='A',q='BRL',value='1000'):
    return {'account_id':a,'currency':q,'amount':value,'context_status':'EXACT_REGISTERED_CONTEXT'}

def opportunity(i='ASSET',a='A',q='BRL',score=80,risk=35,held=False,**kw):
    p={'instrument_id':i,'account_id':a,'currency':q,'context_status':'EXACT_REGISTERED_CONTEXT','reference_provider':'TEST_PROVIDER','reference_provider_id':i,'reference_pnl_pct':'0','reference_quote_at':NOW.isoformat()}
    m=metric(i,q,score,risk,**kw)
    r=readings.project({'positions':[p]},{'scores':[m]},old.CFG,now=NOW,invested=held)['rows'][0]
    return {**r,'position_held':held,'provider':'TEST_PROVIDER','provider_id':i,'identity_source_ref':'synthetic-binding','position_instrument_id':i if held else None}

class OriginalParity(unittest.TestCase):
    def test_2000_original_brain_target_and_cash_allocation_cases(self):
        source=Path(__file__).with_name('original_decision_fixture_v137.py').read_text();ns={'np':np,'CFG':CFG};exec(compile(source,'original_decision','exec'),ns)
        rng=random.Random(137)
        for _ in range(2000):
            rows=[{'asset':'S'+str(j),'promising_pct':rng.uniform(0,100),'opportunity':rng.uniform(0,100),'entry':rng.uniform(0,100),'risk':rng.uniform(0,100),'asymmetry':rng.uniform(0,100),'reversal_risk':rng.uniform(0,100),'current_value_eur':rng.choice([0,100]),'pnl_pct':rng.uniform(-40,40),'action':rng.choice(['COMPRE','VENDA','MANTENHA','ACOMPANHE','REALIZE'])} for j in range(rng.randint(0,12))]
            money=rng.uniform(0,10000);wealth=money+1000;before=copy.deepcopy(rows)
            a=ns['_v38133_brain_experimental'](rows,money,wealth);b=core.brain_signals(rows,money,wealth);self.assertEqual(a,b)
            self.assertEqual(ns['target_weights'](rows,wealth),core.target_weights(rows,wealth,max_positions=5,max_position_pct=25))
            opportunity_data=ns['_v38140_opportunity_intelligence'](rows,a,money)
            chosen=[r for r in opportunity_data['opportunities'] if r['decision_lane']==opportunity_data['allocation_lane']]
            # Exercise exactly the chosen input order used by the legacy function.
            names={r['asset'] for r in chosen};ordered=[r for r in rows if r['asset'] in names]
            expected={r['asset']:r['suggested_allocation_eur'] for r in chosen}
            self.assertEqual(expected,core.cash_shares(ordered,money));self.assertEqual(rows,before)
    def test_no_original_functions_other_than_shared_delegations_changed(self):
        installer=Path(__file__).with_name('PORQUINHO_INDICADORES_NATIVOS_V131.command').read_text()
        encoded=ast.literal_eval(next(line[6:] for line in installer.splitlines() if line.startswith('FILES=')))['porquinho.py']
        oldtree=ast.parse(base64.b64decode(encoded).decode());newtree=ast.parse(Path('/workspace/porquinho-a24/project/porquinho.py').read_text())
        changed={'_v38133_brain_experimental','target_weights','_v38140_opportunity_intelligence'}
        strip=lambda t:ast.dump(ast.Module(body=[n for n in t.body if not isinstance(n,ast.FunctionDef) or n.name not in changed],type_ignores=[]),include_attributes=False)
        self.assertEqual(strip(oldtree),strip(newtree))

class Plans(unittest.TestCase):
    def setUp(self):
        self.cockpit={'execution_authorized':False,'financial_mutation':False,'positions':[],'cash':[cash()]}
        self.rows=[opportunity()];self.funding={'contexts':[]};self.cfg=copy.deepcopy(CFG)
    def build(self):
        result=plans.build(self.cockpit,{'status':'GLOBAL_OPPORTUNITY_RULE_READINGS_INSPECTED','execution_authorized':False,'rows':self.rows},{'rows':[]},self.funding,self.cfg,now=NOW)
        self.assertEqual(result['status'],'CURRENT_ORIGINAL_OPERATIONAL_PLANS_COMPOSED',result);return result
    def row(self):return self.build()['contexts'][0]['rows'][0]
    def test_buy_reaches_original_capped_reference_amount_both_eur_brl(self):
        for q in ('BRL','EUR'):
            self.cockpit['cash']=[cash(q=q)];self.rows=[opportunity(q=q)]
            r=self.row();self.assertEqual(r['action'],'COMPRE');self.assertEqual(r['reference_amount'],'250.00');self.assertEqual(r['target_weight_pct'],25)
            self.assertFalse(self.build()['execution_authorized']);self.assertFalse(self.build()['economic_validation_granted'])
    def test_cash_and_original_position_caps_are_jointly_respected(self):
        self.rows=[opportunity('S'+str(i)) for i in range(7)];p=self.build()['contexts'][0]
        amounts=[r['reference_amount'] for r in p['rows'] if r['reference_amount'] is not None]
        self.assertEqual(len(amounts),5);self.assertLessEqual(sum(map(float,amounts)),1000);self.assertTrue(all(float(v)<=250 for v in amounts))
    def test_maximum_positions_not_multiplied_by_bank_count_within_same_currency(self):
        self.cfg['max_positions']=1
        self.cockpit['cash']=[cash('A'),cash('B')]
        self.rows=[opportunity('BEST',a='A',score=90),opportunity('SECOND',a='B',score=80)]
        values=[r for c in self.build()['contexts'] for r in c['rows'] if r['reference_amount'] is not None]
        self.assertEqual([r['instrument_id'] for r in values],['BEST'])
    def test_active_budget_limits_joint_purchase_references_without_rewriting_plan(self):
        self.rows=[opportunity('FIRST'),opportunity('SECOND')]
        self.funding={'contexts':[{'account_id':'A','currency':'BRL','investment_budget_amount':'11','canonical_cash_observed':'1000','research_enabled':True}]}
        before=copy.deepcopy(self.funding);p=self.build()['contexts'][0]
        self.assertEqual(sum(float(r['reference_amount']) for r in p['rows']),11);self.assertEqual(self.funding,before)
    def test_no_buy_is_not_a_hidden_signal_and_experimental_buy_is_not_promoted(self):
        self.rows=[opportunity(score=69)];p=self.build()['contexts'][0];r=p['rows'][0]
        self.assertEqual(r['action'],'ACOMPANHE');self.assertEqual(r['brain_action'],'COMPRE');self.assertTrue(r['brain_experimental']);self.assertIsNone(r['reference_amount']);self.assertEqual(p['buy_gate_failures'],{'promising_pct':1})
    def test_partial_valuation_keeps_buy_signal_without_inventing_wealth_or_amount(self):
        self.cockpit['positions']=[{'account_id':'A','currency':'BRL','instrument_id':'UNKNOWN'}]
        r=self.row();self.assertEqual(r['action'],'COMPRE');self.assertIsNone(r['reference_amount'])
    def test_no_sizing_configuration_does_not_hide_buy_or_create_default_limit(self):
        self.cfg.pop('position_sizing');r=self.row();self.assertEqual(r['action'],'COMPRE');self.assertIsNone(r['reference_amount'])
    def position(self,score=60,risk=80,pnl='-18',**kw):
        p={'instrument_id':'HELD','account_id':'A','currency':'BRL','context_status':'EXACT_REGISTERED_CONTEXT','quantity':'2','reference_market_value':'200','reference_quote_at':NOW.isoformat(),'reference_pnl_pct':pnl}
        self.cockpit['positions']=[p];r=opportunity('HELD',score=score,risk=risk,held=True,**kw)
        m=metric('HELD',score=score,risk=risk,**kw);p.update(reference_provider='TEST_PROVIDER',reference_provider_id='HELD')
        original=readings.project({'positions':[p]},{'scores':[m]},old.CFG,now=NOW)['rows'][0];r.update(original);self.rows=[r]
        return self.row()
    def test_sell_uses_existing_full_exit_and_exact_held_units(self):
        r=self.position();self.assertEqual(r['action'],'VENDA');self.assertEqual(r['reference_quantity'],'2');self.assertEqual(r['reference_amount'],'200')
    def test_realize_preserves_original_convergence_and_partial_fraction(self):
        r=self.position(score=60,risk=61,pnl='10');self.assertEqual(r['action'],'REALIZE');self.assertEqual(r['reference_quantity'],'0.50');self.assertEqual(r['reference_amount'],'50.00')
    def test_realize_one_trigger_is_review_without_sale_amount(self):
        r=self.position(score=60,risk=35,pnl='10');self.assertEqual(r['action'],'REALIZE');self.assertEqual(r['operational_assessment']['execution_state'],'REVIEW');self.assertIsNone(r['reference_amount'])
    def test_held_loss_does_not_create_stop_or_experimental_entry(self):
        r=self.position(score=67,risk=35);self.assertEqual(r['action'],'MANTENHA');self.assertNotEqual(r['brain_action'],'COMPRE')
    def test_stale_metrics_never_receive_amount_or_brain_signal(self):
        self.rows[0]['metric_at']=(NOW-dt.timedelta(hours=1)).isoformat();r=self.row();self.assertIsNone(r['reference_amount']);self.assertIsNone(r['brain_action'])
    def test_reallocation_links_only_actual_exit_and_entry_same_account_currency(self):
        self.position();self.rows.append(opportunity());p=self.build()['contexts'][0]
        self.assertEqual(len(p['reallocation_candidates']),1);self.assertFalse(p['reallocation_candidates'][0]['selected'])
        batch=p['operational_reallocation_plan'];self.assertEqual(batch['action'],'REALLOCATE');self.assertEqual(len(batch['source_movements']),1);self.assertEqual(len(batch['destination_movements']),1);self.assertFalse(batch['sale_proceeds_used_as_available_cash']);self.assertFalse(batch['net_advantage_validated'])
        self.rows[-1]['currency']='EUR';self.assertTrue(all(not c['reallocation_candidates'] for c in self.build()['contexts']))
    def test_unresolved_identity_never_enters_allocation(self):
        self.rows[0].update(action=None,position_held=None);r=self.row();self.assertIsNone(r['reference_amount']);self.assertIsNone(r['brain_action'])
    def test_original_market_universe_not_hidden_or_assigned_to_account(self):
        snapshot={'scores':[{**metric(i='UNBOUND',q='EUR',score=69),'provider':'CoinGecko','provider_id':'unique-id','quote_currency_source':'EXPLICIT_PROVIDER_REQUEST','action':'ACOMPANHE'}],
            'brain_experimental':{'signals':[{'provider_id':'unique-id','quote_currency':'EUR','brain_action':'COMPRE','experimental':True}]}}
        result=plans.build(self.cockpit,{'status':'GLOBAL_OPPORTUNITY_RULE_READINGS_INSPECTED','execution_authorized':False,'rows':self.rows},{'rows':[]},self.funding,self.cfg,now=NOW,snapshot=snapshot)
        signal=result['market_signals'][0];self.assertEqual(signal['brain_action'],'COMPRE');self.assertIsNone(signal['account_id']);self.assertIsNone(signal['allocation_amount'])
        snapshot['brain_experimental']['signals'][0]['quote_currency']='BRL'
        result=plans.build(self.cockpit,{'status':'GLOBAL_OPPORTUNITY_RULE_READINGS_INSPECTED','execution_authorized':False,'rows':self.rows},{'rows':[]},self.funding,self.cfg,now=NOW,snapshot=snapshot)
        self.assertIsNone(result['market_signals'][0]['brain_action'])

if __name__=='__main__':unittest.main()
