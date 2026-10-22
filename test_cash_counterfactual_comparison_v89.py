import copy,datetime as dt,unittest
from universal_portfolio.cash_counterfactual_comparison_a24 import compare,MODEL_SCHEMA
from universal_portfolio.cash_execution_cost_projection_a24 import project
from test_a24_cash_execution_cost_projection_v64 import Costs
NOW=dt.datetime(2026,10,22,tzinfo=dt.timezone.utc)
class Comparison(unittest.TestCase):
 def setUp(self):
  fixture=Costs();self.s,self.a=fixture.fixture();fixture.insert(self.s,fixture.quote());self.a['account_id']='synthetic-account';self.s['funding_context_fingerprint']='funding-context'
  self.model={'schema':MODEL_SCHEMA,'status':'EXPLICIT_CASH_RETURN_ESTIMATE','account_id':'synthetic-account','currency':'BRL','plan_id':'p','budget_id':'b','horizon_unit':'OBSERVATIONS','horizon_value':30,'reference_capital':'5000','context_fingerprint':'funding-context','source_ref':'SYNTHETIC_SOURCE','model_ref':'SYNTHETIC_MODEL','model_version':'test','computed_at':'2026-10-21T00:00:00+00:00','review_until':'2026-10-23T00:00:00+00:00','expected_net_change':'10','cash_cost_coverage':'NET_OF_MODELLED_CASH_COSTS_AND_TAXES','investment_carrying_cost_status':'KNOWN','investment_carrying_cost':'5','execution_authorized':False}
 def run_comparison(self,model=None):return project(self.s,'BRL',self.a,cash_models=[self.model] if model is None else model,now=NOW)
 def value(self):return self.run_comparison()['variants'][0]['cash_counterfactual_comparison']
 def test_hand_calculated_advantage(self):
  r=self.value();self.assertEqual(r['net_advantage_vs_preserving_cash'],'276.47');self.assertEqual(r['execution_cost_break_even'],'296.47');self.assertEqual(r['arithmetic_result'],'INVESTMENT_ESTIMATE_ABOVE_CASH');self.assertFalse(r['recommendation_created']);self.assertFalse(r['comparison_authorized'])
 def test_no_cash_model_not_zero(self):
  r=self.run_comparison([])['variants'][0]['cash_counterfactual_comparison'];self.assertIsNone(r['net_advantage_vs_preserving_cash']);self.assertFalse(r['cash_yield_assumed_zero'])
 def test_explicit_zero_cash_return_allowed(self):
  self.model['expected_net_change']='0';self.assertEqual(self.value()['net_advantage_vs_preserving_cash'],'286.47')
 def test_each_scope_conflict_refused(self):
  for key in ('account_id','currency','plan_id','budget_id','horizon_unit','horizon_value'):
   with self.subTest(key=key):
    old=self.model[key];self.model[key]='other';self.assertIsNone(self.value()['net_advantage_vs_preserving_cash']);self.model[key]=old
 def test_funding_version_conflict_refused(self):
  self.model['context_fingerprint']='old';self.assertEqual(self.value()['reason'],'CASH_MODEL_FUNDING_CONTEXT_MISMATCH')
 def test_carrying_cost_unknown_not_zero(self):
  self.model['investment_carrying_cost_status']='UNKNOWN';self.assertEqual(self.value()['reason'],'INVESTMENT_CARRYING_COST_MODEL_REQUIRED')
 def test_cash_model_expired_or_future_refused(self):
  self.model['review_until']='2026-10-21T00:00:00Z';self.assertEqual(self.value()['reason'],'CURRENT_CASH_MODEL_REQUIRED')
 def test_ambiguous_models_not_selected(self):
  r=self.run_comparison([self.model,copy.deepcopy(self.model)])['variants'][0]['cash_counterfactual_comparison'];self.assertEqual(r['reason'],'AMBIGUOUS_CASH_RETURN_MODELS')
 def test_capital_mismatch_refused(self):
  self.model['reference_capital']='100';self.assertEqual(self.value()['reason'],'COMMON_CASH_CAPITAL_REQUIRED')
 def test_high_cash_return_can_reverse_advantage(self):
  self.model['expected_net_change']='1000';r=self.value();self.assertLess(float(r['net_advantage_vs_preserving_cash']),0);self.assertEqual(r['arithmetic_result'],'INVESTMENT_ESTIMATE_BELOW_CASH');self.assertIsNone(r['decision'])
 def test_inputs_preserved(self):
  before=copy.deepcopy((self.s,self.a,self.model));self.value();self.assertEqual(before,(self.s,self.a,self.model))
 def test_missing_source_provenance_refused(self):
  del self.model['source_ref'];self.assertEqual(self.value()['reason'],'CASH_MODEL_PROVENANCE_REQUIRED')
 def test_malformed_time_is_local_failure_not_monitor_failure(self):
  self.model['computed_at']='invalid';self.assertEqual(self.value()['status'],'CASH_COMPARISON_INPUT_REQUIRED');self.assertIn('variants',self.run_comparison())
if __name__=='__main__':unittest.main()
