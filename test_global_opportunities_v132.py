import copy,datetime as dt,json,unittest
from unittest.mock import patch
import test_a24_research_quote_acquisition as fixture
import test_global_dashboard_v118 as dashboard
from universal_portfolio import global_opportunity_readings_a24 as opportunities
from universal_portfolio import global_action_readings_a24 as readings
from universal_portfolio import manual_execution_availability_a24 as routes

NOW=fixture.NOW

class Opportunities(unittest.TestCase):
    def setUp(self):
        self.f=fixture.Acquisition();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.root=self.f.root;self.f.save([self.f.rows(),self.f.rows(quote_currency='EUR')])
        self.demand=self.f.demand(('BRL','EUR'),duplicate_account=True)
        self.cockpit={'positions':[],'execution_authorized':False,'financial_mutation':False};self.snapshot={'scores':[self.metric('BRL'),self.metric('EUR')]}
    def metric(self,q='BRL',score=80,risk=35):
        return {**dashboard.metrics(q,risk,score),'provider':'CoinGecko','provider_id':'source-id','quote_observed_at':NOW.isoformat()}
    def position(self,**change):
        return {**{'instrument_id':fixture.IID,'account_id':'account-BRL','currency':'BRL','reference_provider':'CoinGecko','reference_provider_id':'source-id',
            'context_status':'EXACT_REGISTERED_CONTEXT','reference_pnl_pct':'-18','reference_quote_at':NOW.isoformat()},**change}
    def build(self):return opportunities.build(self.root,self.demand,self.cockpit,self.snapshot,dashboard.CFG,now=NOW)
    def row(self,account='account-BRL'):
        result=self.build();self.assertEqual(result['status'],'GLOBAL_OPPORTUNITY_RULE_READINGS_INSPECTED',result)
        return next(r for r in result['rows'] if r['account_id']==account)
    def test_native_metrics_reach_all_exact_accounts_without_writes_or_http(self):
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()};inputs=copy.deepcopy((self.demand,self.snapshot,self.cockpit))
        result=self.build();self.assertEqual(len(result['rows']),3);self.assertEqual(result['action_counts'],{'COMPRE':3})
        self.assertEqual({r['currency'] for r in result['rows']},{'BRL','EUR'})
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()});self.assertEqual(inputs,(self.demand,self.snapshot,self.cockpit))
        for key in ('network_requests','history_write_performed','financial_mutation','execution_authorized','recommendation_created','ranking_created','order_amount_created'):self.assertFalse(result[key])
    def test_real_monitor_panel_composition_exposes_native_opportunities_read_only(self):
        from universal_portfolio.experience_panels_a24 import build
        (self.root/'config.json').write_text(json.dumps({'action_rules':dashboard.CFG}))
        (self.root/'results').mkdir();(self.root/'results/latest.json').write_text(json.dumps(self.snapshot))
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result=build(self.root,now=NOW,cockpit={**self.cockpit,'cash':[]},funding=self.demand)
        self.assertEqual(result['global_opportunity_readings']['action_counts'],{'COMPRE':3},result.get('issues'))
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def test_held_position_uses_hold_not_new_entry_rules(self):
        self.cockpit['positions']=[self.position()];self.assertEqual(self.row()['action'],'MANTENHA')
        self.assertEqual(self.row('second')['action'],'COMPRE')
        self.assertTrue(self.row()['rule_evaluation']['position_held'])
    def test_eur_not_used_as_brl_and_partial_metrics_not_completed(self):
        self.snapshot['scores']=[self.metric('EUR')];self.assertIsNone(self.row()['action'])
        self.assertEqual(self.row('account-EUR')['action'],'COMPRE')
        self.snapshot['scores']=[{**self.metric(),'entry':None}];self.assertIsNone(self.row()['action'])
    def test_stale_future_wrong_unit_and_wrong_provider_are_blocked(self):
        for key,value in [('quote_observed_at',(NOW-dt.timedelta(minutes=31)).isoformat()),('quote_observed_at',(NOW+dt.timedelta(seconds=1)).isoformat()),('metric_unit','RETURN_FRACTION'),('provider','other'),('provider_id','other')]:
            self.snapshot['scores']=[{**self.metric(),key:value}];self.assertIsNone(self.row()['action'],(key,value))
    def test_duplicate_conflicting_metrics_and_positions_refused(self):
        self.snapshot['scores']=[self.metric(),self.metric(score=30)];self.assertEqual(self.row()['status'],'AMBIGUOUS_STANDARDIZED_METRICS')
        self.cockpit['positions']=[self.position(),self.position()];self.assertEqual(self.row()['status'],'AMBIGUOUS_REGISTERED_POSITION_CONTEXT')
    def test_invalid_context_fingerprint_cannot_gain_opportunity(self):
        self.demand['contexts'][0]['context_fingerprint']='changed';self.assertFalse([r for r in self.build()['rows'] if r['account_id']=='account-BRL'])
    def test_unverified_financial_source_refused(self):
        self.cockpit.pop('financial_mutation');self.assertEqual(self.build()['rows'],[])
        self.assertEqual(self.build()['reason'],'VERIFIED_NONMUTATING_COCKPIT_REQUIRED')
    def test_unbound_instrument_not_matched_by_symbol(self):
        self.f.save([]);self.assertEqual(self.build()['rows'],[])
        self.assertTrue(self.build()['binding_blockers'])
    def test_source_disagreement_with_held_position_refused(self):
        self.cockpit['positions']=[self.position(reference_provider_id='other')];self.assertEqual(self.row()['status'],'POSITION_AND_RESEARCH_SOURCE_MISMATCH')
    def test_availability_unknown_or_negative_does_not_change_market_score_or_authorize_order(self):
        r=self.row();self.assertEqual(r['route_availability']['status'],'AVAILABILITY_NOT_CONFIRMED');self.assertEqual(r['action'],'COMPRE')
        record={'schema':routes.SCHEMA,'source_kind':'USER_REPORT','status':'UNAVAILABLE','observed_at':NOW.isoformat(),'account_id':'account-BRL','currency':'BRL','instrument_id':fixture.IID,'channel':'BANK_APP'}
        record['record_id']=routes.record_id(record);p=self.root/routes.STORE;p.mkdir();(p/(record['record_id']+'.json')).write_text(json.dumps(record))
        r=self.row();self.assertEqual(r['route_availability']['status'],'USER_REPORTED_UNAVAILABLE');self.assertEqual(r['action'],'COMPRE');self.assertIn('USER_REPORTED_UNAVAILABLE',r['publication_blockers']);self.assertFalse(r['reading_is_broker_eligibility'])
    def test_binding_mutation_during_read_withdraws_all_rows(self):
        original=opportunities.availability.inspect
        def mutate(root,now):
            self.f.save([]);return original(root,now=now)
        with patch.object(opportunities.availability,'inspect',mutate):self.assertEqual(self.build()['rows'],[])

class Explanations(unittest.TestCase):
    def result(self,score=64,risk=38,pnl='-18',confirmed=False,**changes):
        p=dashboard.cockpit()['positions'][2];p['reference_pnl_pct']=pnl;p.update(changes)
        m=dashboard.metrics('EUR',risk,score);m.update(daily_sell_confirmation=confirmed,daily_sell_confirmation_currency='EUR')
        return readings.project({'positions':[p]},{'scores':[m]},dashboard.CFG,now=dashboard.NOW)['rows'][0]
    def test_loss_from_buy_does_not_create_stop_or_weak_thesis(self):
        r=self.result();self.assertEqual(r['action'],'ACOMPANHE');e=r['rule_evaluation'];self.assertFalse(e['fixed_loss_stop_configured']);self.assertEqual(e['pnl_basis'],'REGISTERED_ACQUISITION_COST_NOT_LAST_SNAPSHOT')
        self.assertTrue(all(c['matched'] is False for c in e['criteria']))
    def test_sell_risk_and_daily_confirmation_explanations_match_original_rules(self):
        r=self.result(risk=75);self.assertEqual(r['action'],'VENDA');self.assertTrue(r['rule_evaluation']['criteria'][0]['matched'])
        self.assertEqual(self.result(score=49)['action'],'ACOMPANHE')
        r=self.result(score=49,confirmed=True);self.assertEqual(r['action'],'VENDA');self.assertTrue(r['rule_evaluation']['criteria'][1]['matched'])
    def test_realize_requires_gain_and_deterioration_not_loss(self):
        r=self.result(pnl='8');self.assertEqual(r['action'],'REALIZE');self.assertTrue(r['rule_evaluation']['criteria'][2]['matched'])
    def test_stale_pnl_cannot_trigger_realization_but_current_structural_risk_still_sells(self):
        stale=(dashboard.NOW-dt.timedelta(hours=1)).isoformat()
        r=self.result(pnl='20',reference_quote_at=stale);self.assertIsNone(r['action']);self.assertEqual(r['status'],'POSITION_PNL_REQUIRED_FOR_COMPLETE_RULE_EVALUATION')
        self.assertEqual(self.result(risk=75,pnl='20',reference_quote_at=stale)['action'],'VENDA')
    def test_purchase_boundary_prevents_older_pnl_use(self):
        r=self.result(pnl='20',reference_not_before=(dashboard.NOW+dt.timedelta(seconds=1)).isoformat());self.assertIsNone(r['action'])

if __name__=='__main__':unittest.main()
