import copy,unittest
from universal_portfolio.analysis_coverage_a24 import project
class Tests(unittest.TestCase):
 def setUp(self):
  self.cash={'schema':'porquinho.cash-plan-visibility-a24/1.0','status':'EXISTING_CASH_PLAN_CONTEXTS_TRANSPORTED','execution_authorized':False,'contexts':[{'account_id':'A','currency':'BRL','analyses':[{'instrument_id':'ID','request_status':'READY_FOR_SOURCE_REVIEW'}]}]}
  self.lab={'schema':'porquinho.global-research-lab-a24/1.0','status':'GLOBAL_RESEARCH_LAB_INSPECTED','execution_authorized':False,'contexts':[{'instrument_id':'ID','quote_currency':'BRL','provider':'brapi','provider_id':'N','observation_count':1268,'status':'RESEARCH_FORECAST_COMPUTED_NOT_VALIDATED','latest_source_date':'2026-10-21','source_kind':'LOCAL_RECOVERED_AND_PROVIDER_HISTORY_COMPOSITION'}]}
 def test_research_is_not_promoted_to_recommendation(self):
  row=project(self.cash,self.lab)['rows'][0];self.assertEqual(row['observation_count'],1268);self.assertIsNone(row['final_recommendation']);self.assertEqual(row['publication_status'],'NO_FINAL_RECOMMENDATION_TRANSPORTED')
 def test_currencies_do_not_cross(self):
  self.lab['contexts'][0]['quote_currency']='EUR';self.assertIsNone(project(self.cash,self.lab)['rows'][0]['observation_count'])
 def test_multiple_sources_are_not_arbitrarily_selected(self):
  self.lab['contexts']*=2;self.assertEqual(project(self.cash,self.lab)['rows'][0]['research_status'],'AMBIGUOUS_RESEARCH_SOURCE')
 def test_account_scope_retained(self):
  self.cash['contexts'].append({'account_id':'B','currency':'EUR','analyses':[{'instrument_id':'ID','request_status':'READY_FOR_SOURCE_REVIEW'}]})
  rows=project(self.cash,self.lab)['rows'];self.assertEqual(rows[0]['account_id'],'A');self.assertIsNone(rows[1]['observation_count'])
 def test_unavailable_lab_not_zero_history(self):
  row=project(self.cash,{})['rows'][0];self.assertIsNone(row['observation_count']);self.assertEqual(row['research_status'],'RESEARCH_STATUS_UNAVAILABLE')
 def test_no_mutation(self):
  before=copy.deepcopy((self.cash,self.lab));project(self.cash,self.lab);self.assertEqual(before,(self.cash,self.lab))
