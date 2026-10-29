import ast,copy,datetime as dt,json,unittest
from pathlib import Path
from decimal import Decimal
from unittest.mock import patch
import test_a24_research_quote_acquisition as fixture
import test_operational_plan_v137 as operational
from universal_portfolio import operational_outcome_tracking_a24 as tracking
from universal_portfolio import global_operational_plan_a24 as plans
from universal_portfolio import research_economic_series_a24 as series

NOW=fixture.NOW

class Tracking(unittest.TestCase):
    def setUp(self):
        self.f=fixture.Acquisition();self.f.setUp();self.addCleanup(self.f.doCleanups);self.root=self.f.root
        self.f.save([self.f.rows()]);self.demand=self.f.demand();self.f.collect()
        row=operational.opportunity(i=fixture.IID);row.update(provider='CoinGecko',provider_id='source-id',identity_source_ref='explicit-test-source',metric_at=NOW.isoformat())
        row['account_id']='account-BRL'
        self.plan=plans.build({'execution_authorized':False,'financial_mutation':False,'positions':[],'cash':[operational.cash(a='account-BRL',value='100')]},
            {'status':'GLOBAL_OPPORTUNITY_RULE_READINGS_INSPECTED','execution_authorized':False,'rows':[row]},{'rows':[]},self.demand,operational.CFG,now=NOW)
        self.assertEqual(self.plan['status'],'CURRENT_ORIGINAL_OPERATIONAL_PLANS_COMPOSED',self.plan)
    def run_capture(self,now=NOW,plan=None):
        plan=plan or self.plan
        return tracking.run(self.root,plan,now=now,revalidate=lambda:plan)
    def test_actual_existing_quotes_and_sealed_store_create_one_daily_issue(self):
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()};result=self.run_capture()
        self.assertEqual(result['issues_created'],1,result);issue=tracking.issues(self.root,NOW)[0]
        self.assertEqual(issue['horizons_days'],[30,60,90,120]);self.assertEqual(issue['currency'],'BRL');self.assertEqual(issue['baseline']['price'],'100.25')
        self.assertFalse(issue['models_modified']);self.assertFalse(issue['legacy_learning_modified']);self.assertEqual(result['outcomes_created'],0)
        for p,data in before.items():self.assertEqual(p.read_bytes(),data)
    def test_repeated_intraday_capture_is_not_another_independent_daily_sample(self):
        self.run_capture();second=self.run_capture(NOW+dt.timedelta(minutes=1));self.assertEqual(second['issues_created'],0)
        self.assertEqual(len(tracking.issues(self.root,NOW+dt.timedelta(minutes=1))),1)
    def test_changed_plan_prevents_capture(self):
        result=tracking.run(self.root,self.plan,now=NOW,revalidate=lambda:{**self.plan,'changed':True});self.assertEqual(result['issues_created'],0);self.assertEqual(tracking.issues(self.root,NOW),[])
    def test_stale_baseline_is_not_backfilled_from_history(self):
        result=self.run_capture(NOW+dt.timedelta(hours=1));self.assertEqual(result['issues_created'],0)
    def test_missing_binding_and_price_are_not_replaced_by_ticker(self):
        self.plan['contexts'][0]['rows'][0]['provider_id']='other';self.assertEqual(self.run_capture()['issues_created'],0)
    def test_summary_is_read_only_and_calendar_horizons_are_not_observation_counts(self):
        self.run_capture();before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()};result=tracking.summary(self.root,now=NOW)
        self.assertEqual(result['horizon_status_counts']['30:PENDING'],1);self.assertEqual(result['issue_count'],1);self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def add_observation(self,days,price='110.275'):
        now=NOW+dt.timedelta(days=days)
        transport=fixture.Transport(now=now,quotes={'source-id':{'brl':Decimal(price),'last_updated_at':int(now.timestamp())}})
        current={(c['account_id'],c['currency'],c['context_fingerprint']) for c in self.demand['contexts']}
        self.f.collect(self.demand,now=now,transport=transport,revalidate=lambda:current)
        return now
    def test_two_observations_thirty_calendar_days_apart_mature_only_thirty_day_lane(self):
        self.run_capture();later=self.add_observation(30);issue=tracking.issues(self.root,later)[0]
        result=tracking.evaluate(issue,series.build(self.root,now=later),now=later)
        self.assertEqual(result['horizons'][0]['status'],'MATURED_REFERENCE_PRICE_OBSERVED');self.assertEqual(Decimal(result['horizons'][0]['gross_price_return_pct']),Decimal('10'))
        self.assertTrue(all(h['status']=='PENDING' for h in result['horizons'][1:]));self.assertFalse(result['model_validation_proven'])
    def test_thirty_sixty_ninety_and_one_twenty_mature_without_rewriting_old_issue(self):
        self.run_capture();path=next((self.root/tracking.STORE/'issues').glob('*.json'));before=path.read_bytes()
        for days in (30,60,90,120):
            later=self.add_observation(days);issue=tracking.issues(self.root,later)[0]
            result=tracking.evaluate(issue,series.build(self.root,now=later),now=later)
            self.assertEqual(sum(h['status']=='MATURED_REFERENCE_PRICE_OBSERVED' for h in result['horizons']),[30,60,90,120].index(days)+1)
        self.assertEqual(path.read_bytes(),before)
    def test_price_before_due_and_price_too_late_do_not_create_maturity(self):
        self.run_capture();self.add_observation(29);later=self.add_observation(34)
        result=tracking.evaluate(tracking.issues(self.root,later)[0],series.build(self.root,now=later),now=later)
        self.assertEqual(result['horizons'][0]['status'],'DUE_OBSERVATION_REQUIRED');self.assertIsNone(result['horizons'][0]['gross_price_return_pct'])
    def test_other_currency_series_never_labels_this_issue(self):
        self.run_capture();later=self.add_observation(30);market=series.build(self.root,now=later)
        for row in market['series']:row['quote_currency']='EUR'
        result=tracking.evaluate(tracking.issues(self.root,later)[0],market,now=later);self.assertIsNone(result['horizons'][0]['gross_price_return_pct'])
    def test_unsafe_market_contract_refused(self):
        self.run_capture();market=series.build(self.root,now=NOW);market['training_authorized']=True
        with self.assertRaises(ValueError):tracking.evaluate(tracking.issues(self.root,NOW)[0],market,now=NOW)
    def test_corrupt_issue_blocks_instead_of_rewriting_or_promoting(self):
        self.run_capture();path=next((self.root/tracking.STORE/'issues').glob('*.json'));path.write_text('{}')
        result=self.run_capture();self.assertEqual(result['status'],'OPERATIONAL_TRACKING_UNAVAILABLE');self.assertEqual(path.read_text(),'{}')
    def test_real_normal_cycle_hook_publishes_original_buy_and_captures_without_order(self):
        score=operational.metric(i='source-id',q='BRL');score.update(provider='CoinGecko',quote_observed_at=NOW.isoformat(),quote_currency_source='EXPLICIT_PROVIDER_REQUEST')
        (self.root/'config.json').write_text(json.dumps(operational.CFG));(self.root/'results').mkdir(exist_ok=True)
        (self.root/'results/latest.json').write_text(json.dumps({'timestamp':NOW.isoformat(),'scores':[score]}))
        cockpit={'execution_authorized':False,'financial_mutation':False,'positions':[],'cash':[operational.cash(a='account-BRL',value='100')]}
        plan=plans.from_root(self.root,self.demand,cockpit,now=NOW)
        row=plan['contexts'][0]['rows'][0];self.assertEqual(row['action'],'COMPRE');self.assertEqual(row['reference_amount'],'25.00')
        from universal_portfolio.operational_cycle_a24 import run
        ledger=self.root/'data/ledger_sentinel.json';ledger.write_text('UNCHANGED')
        with patch('universal_portfolio.universal_observation_bridge.observed_candidates',return_value=(self.root,[])),patch('universal_portfolio.funded_currency_research_a24.build',return_value=self.demand),patch('universal_portfolio.canonical_runtime_read_model.build',return_value={}),patch('universal_portfolio.universal_cockpit_a24.build',return_value=cockpit),patch('universal_portfolio.position_reference_reconciliation_a24.load',return_value=[]),patch('universal_portfolio.universal_observation_bridge.build_read_only_bridge',side_effect=AssertionError('Economic bridge must not gate original signals')):
            result=run(self.root,now=NOW)
        self.assertEqual(result['status'],'ORIGINAL_OPERATIONAL_CYCLE_EVALUATED',result);self.assertEqual(result['tracking']['issues_created'],1,result)
        self.assertEqual(ledger.read_text(),'UNCHANGED');self.assertEqual(len(tracking.issues(self.root,NOW)),1)

if __name__=='__main__':unittest.main()
