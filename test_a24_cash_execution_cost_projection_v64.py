import copy,unittest
from universal_portfolio.cash_execution_cost_projection_a24 import project
class Costs(unittest.TestCase):
 def fixture(self,q='BRL'):
  scope={'plan_id':'p','budget_id':'b','candidate_id':'c','policy_version_digest':'v'}
  s={**scope,'horizon_unit':'OBSERVATIONS','horizon_value':30,'legs':[{'instrument_id':'EXACT:1','fraction_numerator':1,'fraction_denominator':1}],'common_research_unit':{'currency':q,'reference_capital':'5000','expected_return_pct':'6.2294','expected_gross_change':'311.47'},'reviewed_cost_context':{'status':'CANDIDATE_COST_CONTEXTS_LINKED_RESEARCH_ONLY','execution_authorized':False,'legs':[{'instrument_id':'EXACT:1','currency':q,'side':'BUY','research_capital_fraction':'1','reviewed_quote_candidates':[]}]}}
  a={**scope,'currency':q,'status':'EXISTING_RESEARCH_EVIDENCE_RECONCILED_NOT_A_FINAL_SUGGESTION','reference_capital':'5000','expected_gross_change':'311.47'}
  return s,a
 def quote(self,eid='e',amount='20',status='REVIEWED_PRETRADE_COST_ESTIMATE_NOT_VALIDATED'):
  return {'evidence_id':eid,'execution_venue_id':'bank-app','cost_evidence':{'evidence_id':eid,'status':status,'total_cost':amount,'execution_authorized':False}}
 def insert(self,s,quote):s['reviewed_cost_context']['legs'][0]['reviewed_quote_candidates'].append(quote)
 def test_unknown_not_zero(self):
  s,a=self.fixture();r=project(s,'BRL',a);self.assertEqual(r['variants'],[]);self.assertIsNone(r['net_advantage_vs_preserving_cash'])
 def test_existing_calculator_projects_cost_without_decision(self):
  for q in ['BRL','EUR','JPY']:
   s,a=self.fixture(q);self.insert(s,self.quote());before=copy.deepcopy((s,a));r=project(s,q,a);v=r['variants'][0];self.assertEqual(v['reviewed_execution_cost'],'20');self.assertEqual(v['research_change_less_execution_costs'],'291.4700');self.assertEqual(v['common_unit_status'],'NOT_COMPARABLE');self.assertFalse(r['recommendation_created']);self.assertFalse(r['execution_venue_selected']);self.assertEqual((s,a),before)
 def test_explicit_zero_remains_zero(self):
  s,a=self.fixture();self.insert(s,self.quote(amount='0'));self.assertEqual(project(s,'BRL',a)['variants'][0]['reviewed_execution_cost'],'0')
 def test_partial_cost_not_used(self):
  s,a=self.fixture();self.insert(s,self.quote(status='PARTIAL_COST_EVIDENCE'));self.assertEqual(project(s,'BRL',a)['variants'],[])
 def test_alternative_routes_not_chosen(self):
  s,a=self.fixture();self.insert(s,self.quote('e1','10'));self.insert(s,self.quote('e2','30'));r=project(s,'BRL',a);self.assertEqual(len(r['variants']),2);self.assertFalse(r['execution_venue_selected'])
 def test_notional_currency_and_identity_conflicts_refused(self):
  for field,value in [('research_capital_fraction','1/2'),('currency','EUR'),('instrument_id','OTHER:1')]:
   s,a=self.fixture();self.insert(s,self.quote());s['reviewed_cost_context']['legs'][0][field]=value;self.assertEqual(project(s,'BRL',a)['variants'],[])
 def test_duplicate_evidence_refused(self):
  s,a=self.fixture();self.insert(s,self.quote());self.insert(s,self.quote());self.assertEqual(project(s,'BRL',a)['variants'],[])
 def test_assessment_version_conflict_refused(self):
  s,a=self.fixture();self.insert(s,self.quote());a['policy_version_digest']='old';self.assertEqual(project(s,'BRL',a)['variants'],[])
 def test_cost_can_exceed_gross_without_false_positive(self):
  s,a=self.fixture();self.insert(s,self.quote(amount='400'));self.assertLess(float(project(s,'BRL',a)['variants'][0]['research_change_less_execution_costs']),0)
 def test_invalid_sources_not_break_monitor(self):self.assertEqual(project({},'BRL',None)['variants'],[])
if __name__=='__main__':unittest.main()
