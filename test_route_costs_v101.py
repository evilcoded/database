import unittest,sys,json,copy,datetime
from pathlib import Path
sys.path.insert(0,'/workspace/porquinho-a24/project')
from universal_portfolio.route_documentary_cost_a24 import project
class Tests(unittest.TestCase):
 def setUp(self):
  self.now=datetime.datetime(2026,10,23,9,tzinfo=datetime.timezone.utc)
  self.doc=json.loads(Path('/workspace/porquinho-a24/project/config/official_execution_route_policies_a24.json').read_text())
  self.iid=self.doc['policies'][0]['scope']['instrument_ids'][0]
  self.s=dict(plan_id='p',budget_id='b',candidate_id='c',policy_version_digest='v',horizon_unit='OBSERVATIONS',horizon_value=30,cash_fraction_numerator=0,cash_fraction_denominator=1,legs=[dict(instrument_id=self.iid,quote_currency='EUR',fraction_numerator=1,fraction_denominator=1)],common_research_unit=dict(currency='EUR',reference_capital='100',expected_gross_change='5',horizon_unit='OBSERVATIONS',horizon_value=30))
  self.a={k:self.s[k] for k in ('plan_id','budget_id','candidate_id','policy_version_digest')};self.a.update(status='EXISTING_RESEARCH_EVIDENCE_RECONCILED_NOT_A_FINAL_SUGGESTION',account_id='account',currency='EUR',reference_capital='100',expected_gross_change='5')
  self.accounts={'account':dict(_institution_name='N26',_institution_country='DE',currency='EUR',pricing_plan='Standard',management_mode='MANUAL')}
  self.catalog=[dict(instrument_id=self.iid,asset_class='CRYPTO')]
 def run_project(self):return project(self.s,'EUR',self.a,'account',self.accounts,self.catalog,self.doc,now=self.now)
 def test_commission_no_exchange_dependency_and_budget_deficit(self):
  before=copy.deepcopy((self.s,self.a,self.accounts,self.catalog,self.doc));r=self.run_project();self.assertEqual(r['status'],'ROUTE_DOCUMENTARY_COMPONENTS_PROJECTED');v=r['variants'][0];self.assertEqual(v['documented_component_subtotal'],'1.5');self.assertEqual(v['reference_budget_shortfall_before_unmodelled_costs'],'1.5');self.assertIsNone(v['net_change']);self.assertEqual((self.s,self.a,self.accounts,self.catalog,self.doc),before)
 def test_ceiling_cent(self):
  self.s['common_research_unit']['reference_capital']='1';self.a['reference_capital']='1';self.assertEqual(self.run_project()['variants'][0]['documented_component_subtotal'],'0.02')
 def test_no_metal_discount_or_other_asset_assumption(self):
  self.accounts['account']['pricing_plan']='Metal';self.assertIsNone(self.run_project())
 def test_currency_mismatch(self):
  self.a['currency']='BRL';self.assertFalse(self.run_project()['variants'])
 def test_expired_source(self):
  self.now+=datetime.timedelta(days=8);r=self.run_project();self.assertEqual(r['legs'][0]['status'],'CURRENT_ROUTE_DOCUMENT_REQUIRED');self.assertFalse(r['variants'])
 def test_policy_conflict(self):
  self.doc['policies'].append(copy.deepcopy(self.doc['policies'][0]));self.assertEqual(self.run_project()['legs'][0]['status'],'AMBIGUOUS_ROUTE_POLICIES')
 def test_class_conflict(self):
  self.catalog.append(dict(instrument_id=self.iid,asset_class='EQUITY'));self.assertIsNone(self.run_project())
 def test_nubank_dynamic_quote_never_zero_or_b3(self):
  self.accounts['account'].update(_institution_name='Nubank',_institution_country='BR',currency='BRL');self.a['currency']='BRL';self.s['common_research_unit']['currency']='BRL';self.s['legs'][0]['quote_currency']='BRL'
  r=project(self.s,'BRL',self.a,'account',self.accounts,self.catalog,self.doc,now=self.now);self.assertEqual(r['legs'][0]['status'],'ROUTE_PRETRADE_QUOTE_REQUIRED');self.assertFalse(r['variants']);self.assertIsNone(r['legs'][0]['documented_component_subtotal'])
 def test_arbitrary_instrument_supported_by_policy_data(self):
  self.doc['policies'][0]['scope']['instrument_ids']=['other'];self.s['legs'][0]['instrument_id']='other';self.catalog=[dict(instrument_id='other',asset_class='CRYPTO')];self.assertTrue(self.run_project()['variants'])
 def test_malformed_fraction(self):
  self.s['legs'][0]['fraction_numerator']=2;self.assertFalse(self.run_project()['variants'])
if __name__=='__main__':unittest.main()
