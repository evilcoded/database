import copy,unittest
from universal_portfolio.cash_plan_visibility_a24 import project
from universal_portfolio.funded_currency_research_a24 import fingerprint
class CashPlanVisibility(unittest.TestCase):
 def fixture(self,q='JPY'):
  c={'account_id':'a','currency':q,'canonical_cash_observed':'5000','investment_budget_amount':'5000','capital_status':'ACTIVE_INVESTMENT_BUDGET','research_enabled':True,'active_plan_ids':['p'],'active_plan_contexts':[{'plan_id':'p','planning_budget_id':'b','allowed_asset_classes':['EQUITY'],'period':'30D'}],'planning_budget_intents':[{'budget_id':'b','amount':'5000'}]};c['context_fingerprint']=fingerprint(c)
  r={'account_id':'a','quote_currency':q,'candidate_asset_class':'EQUITY','status':'READY_FOR_SOURCE_REVIEW','context_fingerprint':c['context_fingerprint']}
  f={'schema':'porquinho.funded-currency-research-a24/1.0','status':'OBSERVATION_DEMAND_PROJECTED','authority':'NONE','financial_mutation':False,'automatic_execution_authorized':False,'contexts':[c],'research_requests':[r]}
  a={'schema':'porquinho.economic-action-plan-a24/1.0','status':'ACTION_CONTEXTS_PROJECTED_NOT_COMPARATOR_READY','recommendation_created':False,'execution_authorized':False,'cases':[{'resource_kind':'CASH','account_id':'a','currency':q,'alternatives':[{'kind':'DEPLOY_CASH','blocking_reasons':['VALIDATED_SIZING_REQUIRED']}]}]};return f,a
 def test_generic_currencies_and_no_mutation(self):
  for q in ['BRL','EUR','JPY','CAD']:
   f,a=self.fixture(q);original=copy.deepcopy((f,a));r=project(f,a);c=r['contexts'][0];self.assertEqual(c['plans'][0]['budget_amount'],'5000');self.assertEqual(c['blocking_reason_counts'],{'VALIDATED_SIZING_REQUIRED':1});self.assertFalse(r['recommendation_created']);self.assertEqual((f,a),original)
 def test_other_currency_and_account_not_joined(self):
  f,a=self.fixture();a['cases'][0]['account_id']='other';self.assertFalse(project(f,a)['contexts'][0]['action_diagnostic_available']);a['cases'][0]['account_id']='a';a['cases'][0]['currency']='BRL';self.assertFalse(project(f,a)['contexts'][0]['action_diagnostic_available'])
 def test_fingerprint_conflict_not_presented(self):
  f,a=self.fixture();f['contexts'][0]['investment_budget_amount']='99999';self.assertEqual(project(f,a)['status'],'CASH_PLAN_VISIBILITY_UNAVAILABLE')
 def test_duplicate_cases_not_confirmed_zero(self):
  f,a=self.fixture();a['cases']*=2;r=project(f,a)['contexts'][0];self.assertIsNone(r['blocking_reason_counts']);self.assertFalse(r['action_diagnostic_available'])
 def test_missing_sources(self):self.assertEqual(project({}, {})['status'],'CASH_PLAN_VISIBILITY_UNAVAILABLE')
 def test_requests_must_match_plan_class_and_fingerprint(self):
  f,a=self.fixture();f['research_requests'][0]['candidate_asset_class']='CRYPTO';r=project(f,a)['contexts'][0];self.assertEqual(r['plans'][0]['research_request_status_counts'],{});f['research_requests'][0]['context_fingerprint']='invalid';self.assertEqual(project(f,a)['contexts'][0]['research_request_status_counts'],{})
if __name__=='__main__':unittest.main()
