import copy,sys,unittest
sys.path.insert(0,'/workspace/porquinho-a24/project')
from universal_portfolio.action_cost_visibility_a24 import project
class Tests(unittest.TestCase):
 def inputs(self):
  leg=dict(alternative_id='a',account_id='acct',currency='BRL',instrument_id='iid',side='BUY')
  return dict(schema='porquinho.official-bank-cost-reference-a24/1.0',execution_authorized=False,legs=[leg|{'component_references':{'brokerage':{'amount':'0'}}}]),dict(schema='porquinho.exchange-fee-reference-a24/1.0',execution_authorized=False,legs=[leg|{'hypotheses':[{'unrounded_reference_amount':'1.5'}]}])
 def test_exact_join_and_preservation(self):
  b,e=self.inputs();before=copy.deepcopy((b,e));r=project(b,e)
  self.assertEqual(len(r['rows']),1);self.assertIsNone(r['rows'][0]['total_cost']);self.assertEqual((b,e),before)
 def test_currency_account_side_separation(self):
  for key,val in [('currency','EUR'),('account_id','other'),('side','SELL'),('alternative_id','b')]:
   b,e=self.inputs();e['legs'][0][key]=val;self.assertEqual(len(project(b,e)['rows']),2)
 def test_ambiguity_refuses_selection(self):
  b,e=self.inputs();b['legs']*=2;r=project(b,e)['rows'][0];self.assertEqual(r['status'],'AMBIGUOUS_LEG_REFERENCES');self.assertEqual(r['bank_components'],{});self.assertEqual(r['exchange_hypotheses'],[])
 def test_unavailable_not_empty_success(self):self.assertEqual(project({}, {})['status'],'COST_REFERENCES_UNAVAILABLE')
if __name__=='__main__':unittest.main()
