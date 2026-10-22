import copy,unittest
from universal_portfolio.action_component_validation_a24 import project,REQUIRED
from test_a24_economic_component_set_producer import packet
class Validation(unittest.TestCase):
 def setUp(self):
  a=packet()['sets'][0]['alternatives'][0];a['kind']=a['kind'];a['research_readings']=a.pop('components');a['case_id']='synthetic'
  self.a=a
  self.h={'schema':'porquinho.action-research-handoff-a24/1.0','status':'CURRENT_RESEARCH_ATTACHED_TO_DRAFT_ACTIONS','alternatives':[a],**{k:False for k in ('execution_authorized','models_modified','financial_mutation','recommendation_created','comparison_authorized')}}
 def test_real_validator_not_implicit_action_authority(self):
  r=project(self.h);self.assertEqual(r['component_pass_count'],5);self.assertEqual(r['blocking_reason_counts'],{});self.assertFalse(r['comparison_authorized'])
 def test_explicit_context_preserved_without_decision(self):
  for c in self.a['research_readings'].values():c.update(alternative_id=self.a['alternative_id'],action_kind=self.a['kind'])
  r=project(self.h);self.assertEqual(r['blocking_reason_counts'],{});self.assertFalse(r['recommendation_created']);self.assertFalse(r['comparison_authorized'])
 def test_unvalidated_research_never_promoted(self):
  for c in self.a['research_readings'].values():c['validation_status']='NOT_VALIDATED_FOR_COMPARATOR'
  before=copy.deepcopy(self.h);r=project(self.h);self.assertEqual(r['component_pass_count'],0);self.assertEqual(before,self.h)
 def test_cost_missing_not_zero(self):
  del self.a['research_readings']['transaction_cost'];r=project(self.h);self.assertIn('TRANSACTION_COST_COMPONENT_REQUIRED',r['blocking_reason_counts']);self.assertNotIn('transaction_cost',self.a['research_readings'])
 def test_wrong_horizon_rejected(self):
  self.a['research_readings']['forward_return']['horizon_value']=120;r=project(self.h);self.assertIn('COMPONENT_SCOPE_MISMATCH',r['blocking_reason_counts'])
 def test_unknown_input_not_success(self):self.assertEqual(project({})['status'],'ACTION_COMPONENT_INPUT_UNAVAILABLE')
 def test_mutation_authority_rejected(self):
  self.h['execution_authorized']=True;self.assertEqual(project(self.h)['status'],'ACTION_COMPONENT_INPUT_UNAVAILABLE')
if __name__=='__main__':unittest.main()
