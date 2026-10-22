import copy,unittest
from universal_portfolio.action_research_handoff_a24 import project,summary,SCOPE
class Handoff(unittest.TestCase):
 def setUp(self):
  a={'alternative_id':'test','instrument_id':'synthetic','account_id':'account','currency':'TST','horizon_unit':'OBSERVATIONS','horizon_value':60,'planning_context_fingerprint':'budget-context','kind':'DEPLOY_CASH'}
  self.action=a
  self.plan={'schema':'porquinho.economic-action-plan-a24/1.0','status':'ACTION_CONTEXTS_PROJECTED_NOT_COMPARATOR_READY','execution_authorized':False,'cases':[{'case_id':'case','alternatives':[a]}]}
  self.reading={**{k:a[k] for k in SCOPE},'authority':'NONE','validation_status':'NOT_VALIDATED_FOR_COMPARATOR','value':.03}
  self.row={'instrument_id':'synthetic','account_id':'account','quote_currency':'TST','context_fingerprint':'budget-context','component_readings':{'forward_return':self.reading}}
  self.research={'schema':'porquinho.research-economic-components-a24/1.0','status':'RESEARCH_COMPONENTS_INSPECTED','model_validation_proven':False,'execution_authorized':False,'contexts':[self.row]}
 def run_handoff(self):return project(self.plan,self.research)
 def test_exact_link_preserves_inputs_and_validation(self):
  before=copy.deepcopy((self.plan,self.research));out=self.run_handoff();r=out['alternatives'][0];self.assertEqual(r['research_readings']['forward_return'],self.reading);self.assertFalse(r['comparator_ready']);self.assertEqual((self.plan,self.research),before)
  r['research_readings']['forward_return']['value']=99;self.assertEqual(self.reading['value'],.03)
 def test_each_horizon_scope_is_exact(self):
  for k in SCOPE:
   with self.subTest(k=k):
    old=self.reading[k];self.reading[k]='different';self.assertEqual(self.run_handoff()['alternatives'][0]['status'],'RESEARCH_COMPONENT_SCOPE_MISMATCH');self.reading[k]=old
 def test_account_currency_budget_cannot_cross(self):
  for k in ('account_id','quote_currency','context_fingerprint'):
   with self.subTest(k=k):
    old=self.row[k];self.row[k]='other';self.assertIsNone(self.run_handoff()['alternatives'][0]['research_readings']);self.row[k]=old
 def test_ambiguous_provider_not_selected(self):
  self.research['contexts'].append(copy.deepcopy(self.row));self.assertEqual(self.run_handoff()['alternatives'][0]['status'],'AMBIGUOUS_RESEARCH_SOURCE_CONTEXT')
 def test_cash_not_given_stock_forecast(self):
  self.action['instrument_id']=None;self.assertEqual(self.run_handoff()['alternatives'][0]['status'],'CASH_COUNTERFACTUAL_MODEL_REQUIRED')
 def test_unavailable_source_not_empty_opportunity_set(self):
  self.research['status']='RESEARCH_COMPONENT_INSPECTION_UNAVAILABLE';self.assertEqual(self.run_handoff()['status'],'ACTION_RESEARCH_HANDOFF_UNAVAILABLE')
 def test_summary_excludes_raw_models(self):
  s=summary(self.run_handoff());self.assertNotIn('alternatives',s);self.assertEqual(s['alternative_count'],1);self.assertFalse(s['recommendation_created'])
if __name__=='__main__':unittest.main()
