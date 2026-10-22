import copy,datetime as dt,json,tempfile,unittest
from pathlib import Path
from universal_portfolio.official_bank_cost_reference_a24 import project,build,CATALOG,INPUT_SCHEMA
NOW=dt.datetime(2026,10,22,22,tzinfo=dt.timezone.utc)
class Reference(unittest.TestCase):
 def setUp(self):
  self.e={'schema':'porquinho.economic-action-evidence-a24/1.0','status':'ACTION_EVIDENCE_ATTACHED_NOT_COMPARATOR_READY','execution_authorized':False,'alternatives':[{'alternative_id':'synthetic-action','legs':[{'account_id':'a','instrument_id':'EXPLICIT:SYNTHETIC','currency':'TST','side':'BUY'}]}]}
  self.accounts={'a':{'_institution_name':'Synthetic Bank','_institution_country':'XX','currency':'TST','management_mode':'MANUAL'}}
  self.candidates=[{'instrument_id':'EXPLICIT:SYNTHETIC','asset_class':'EQUITY'}]
  self.policy={'policy_id':'synthetic','scope':{'institution_name':'Synthetic Bank','registry_country':'XX','currency':'TST','asset_classes':['EQUITY'],'sides':['BUY','SELL'],'channel':'BANK_APP','pricing_plan_scope':'PUBLISHED_WITHOUT_PLAN_RESTRICTION'},'source':{'kind':'OFFICIAL_BANK_PUBLIC_PAGE','url':'https://example.test/prices','document_sha256':'a'*64,'observed_at':'2026-10-21T00:00:00Z','review_until':'2026-10-29T00:00:00Z'},'user_channel_declaration':{'source':'USER_DECLARED_EXECUTION_CHANNEL','registry_country':'XX','management_mode':'MANUAL','channel':'BANK_APP'},'components':{'brokerage':{'rule':'FIXED_DOCUMENTED_AMOUNT','amount':'0','unit':'CURRENCY_AMOUNT'}}}
  self.doc={'schema':INPUT_SCHEMA,'policies':[self.policy]}
 def result(self):return project(self.e,self.accounts,self.candidates,self.doc,now=NOW)
 def row(self):return self.result()['legs'][0]
 def test_zero_reference_is_not_zero_total_cost(self):
  r=self.row();self.assertEqual(r['component_references']['brokerage']['amount'],'0');self.assertIsNone(r['total_cost']);self.assertIn('spread',r['unresolved_execution_components']);self.assertFalse(r['complete_cost_estimate_created']);self.assertFalse(r['comparison_authorized'])
 def test_nonzero_policy_without_engine_change(self):
  self.policy['components']['brokerage']['amount']='12.34';self.assertEqual(self.row()['component_references']['brokerage']['amount'],'12.34')
 def test_other_bank_or_currency_not_inherited(self):
  self.accounts['a']['_institution_name']='Another';self.assertEqual(self.row()['component_references'],{})
 def test_unknown_asset_class_not_guessed_from_id(self):
  self.candidates=[];self.assertEqual(self.row()['component_references'],{})
 def test_conflicting_catalog_class_refused(self):
  self.candidates.append({'instrument_id':'EXPLICIT:SYNTHETIC','asset_class':'CRYPTO'});self.assertEqual(self.row()['component_references'],{})
 def test_crypto_not_given_equity_exemption(self):
  self.candidates[0]['asset_class']='CRYPTO';self.assertEqual(self.row()['component_references'],{})
 def test_desk_channel_not_given_app_price(self):
  self.policy['user_channel_declaration']['channel']='DESK';self.assertEqual(self.row()['component_references'],{})
 def test_expired_source_refused(self):
  self.policy['source']['review_until']='2026-10-22T00:00:00Z';self.assertEqual(self.row()['component_references'],{})
 def test_ambiguous_policies_not_selected(self):
  p=copy.deepcopy(self.policy);p['policy_id']='second';self.doc['policies'].append(p);self.assertEqual(self.row()['status'],'AMBIGUOUS_BANK_COMPONENT_POLICIES')
 def test_input_models_not_modified(self):
  before=copy.deepcopy((self.e,self.accounts,self.candidates,self.doc));self.result();self.assertEqual(before,(self.e,self.accounts,self.candidates,self.doc))
 def test_missing_catalog_has_no_write(self):
  with tempfile.TemporaryDirectory() as root:
   self.assertEqual(build(root,self.e,self.candidates,now=NOW)['status'],'BANK_COMPONENT_POLICY_NOT_CONFIGURED');self.assertEqual(list(Path(root).rglob('*')),[])
if __name__=='__main__':unittest.main()
