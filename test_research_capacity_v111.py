"""Market research eligibility must not grant spending capacity or alter plan intent."""
import copy,datetime as dt,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from universal_portfolio import funded_currency_research_a24 as f
from universal_portfolio import cash_plan_visibility_a24 as visibility
from universal_portfolio import research_quote_acquisition_a24 as q
from universal_portfolio import explicit_market_bindings_a24 as b
NOW=dt.datetime(2026,10,23,12,tzinfo=dt.timezone.utc)
IID='GLOBAL:CRYPTO:CRYPTO:EXAMPLE'
class Tests(unittest.TestCase):
 def inputs(self,cur='BRL',cash='800',budget='1000'):
  return dict(cash=[dict(account_id='a',currency=cur,amount=cash)],registry={'accounts':[dict(account_id='a',currency=cur,institution_id='bank')],'institutions':[dict(institution_id='bank',country='XX')]},budgets=[dict(budget_id='b',account_id='a',currency=cur,amount=budget,status='ACTIVE',authority='NONE',ledger_semantics='NONE',creates_cash=False,mutates_ledger=False)],plans=[dict(plan_id='p',planning_budget_id='b',source_account_id='a',currency=cur,status='ACTIVE',authority='NONE',automatic_execution_authorized=False,execution_mode='MANUAL',allowed_asset_classes=['CRYPTO'])],candidates=[dict(instrument_id=IID,asset_class='CRYPTO')])
 def test_budget_excess_restores_research_but_not_spending_capacity(self):
  data=self.inputs();before=copy.deepcopy(data);out=f.project(**data);c=out['contexts'][0]
  self.assertTrue(c['research_enabled']);self.assertEqual(c['capital_status'],'ACTIVE_BUDGETS_EXCEED_CURRENT_CASH');self.assertIsNone(c['investment_budget_amount']);self.assertEqual(c['planning_budget_intents'][0]['amount'],'1000');self.assertEqual(c['canonical_cash_observed'],'800');self.assertEqual(len(out['research_requests']),1);self.assertEqual(data,before)
  self.assertFalse(out['financial_mutation']);self.assertFalse(out['automatic_execution_authorized']);self.assertFalse(c['execution_authorized'])
 def test_new_context_fingerprint_covers_research_state(self):
  c=f.project(**self.inputs())['contexts'][0];self.assertEqual(c['context_fingerprint'],f.fingerprint({k:v for k,v in c.items() if k!='context_fingerprint'}))
 def test_currency_agnostic(self):
  for cur in ('BRL','EUR','JPY'):
   out=f.project(**self.inputs(cur));self.assertEqual({r['quote_currency'] for r in out['research_requests']},{cur});self.assertTrue(out['contexts'][0]['research_enabled'])
 def test_valid_budget_existing_context_does_not_gain_new_metadata(self):
  out=f.project(**self.inputs(budget='500'));c=out['contexts'][0];self.assertEqual(c['investment_budget_amount'],'500');self.assertEqual(c['capital_status'],'ACTIVE_INVESTMENT_BUDGET');self.assertNotIn('research_context_status',c)
 def test_zero_cash_still_has_no_new_investment_research_context(self):self.assertEqual(f.project(**self.inputs(cash='0'))['contexts'],[])
 def test_account_currency_conflict_not_bypassed(self):
  data=self.inputs();data['registry']['accounts'][0]['currency']='EUR';out=f.project(**data);self.assertFalse(out['contexts'][0]['research_enabled']);self.assertEqual(out['research_requests'],[])
 def test_invalid_budget_authority_not_bypassed(self):
  data=self.inputs();data['budgets'][0]['authority']='EXECUTE';out=f.project(**data);self.assertEqual(out['research_requests'],[])
 def test_invalid_authority_plus_excess_budget_not_bypassed(self):
  data=self.inputs();data['budgets'].append({**data['budgets'][0],'budget_id':'bad','authority':'EXECUTE'});out=f.project(**data);self.assertFalse(out['contexts'][0]['research_enabled']);self.assertEqual(out['research_requests'],[])
 def test_automatic_plan_not_promoted_to_research(self):
  data=self.inputs();data['plans'][0]['automatic_execution_authorized']=True;out=f.project(**data);self.assertEqual(out['research_requests'],[])
 def test_duplicate_plan_not_bypassed(self):
  data=self.inputs();data['plans'].append({**data['plans'][0],'plan_id':'other'});out=f.project(**data);self.assertFalse(out['contexts'][0]['research_enabled'])
 def test_class_restriction_unchanged(self):
  data=self.inputs();data['candidates'].append(dict(instrument_id='OTHER',asset_class='BOND'));out=f.project(**data);self.assertEqual(len(out['research_requests']),1);self.assertEqual(out['research_requests'][0]['instrument_id'],IID)
 def test_visibility_keeps_intent_and_research_separate(self):
  funding=f.project(**self.inputs());view=visibility.project(funding,{})['contexts'][0];self.assertEqual(view['plans'][0]['budget_amount'],'1000');self.assertIsNone(view['investment_budget_amount']);self.assertTrue(view['research_enabled']);self.assertEqual(view['research_context_status'],'MARKET_RESEARCH_ONLY_CAPITAL_RECONCILIATION_PENDING')
 def test_action_builder_still_refuses_unreconciled_spending_capacity(self):
  from universal_portfolio.economic_action_plan_a24 import project as actions
  data=self.inputs();funding=f.project(**data)
  out=actions(positions=[],cash=data['cash'],registry=data['registry'],funding=funding,candidates=data['candidates'],plans=data['plans'])
  case=next(c for c in out['cases'] if c['resource_kind']=='CASH');self.assertIsNone(case['capital_ceiling'])
  deploy=[a for a in case['alternatives'] if a['kind']=='DEPLOY_CASH'];self.assertTrue(deploy)
  self.assertTrue(all('ACTIVE_INVESTMENT_BUDGET_REQUIRED' in a['blocking_reasons'] for a in deploy));self.assertFalse(out['recommendation_created']);self.assertFalse(out['execution_authorized'])
 def test_research_acquisition_uses_existing_adapter_and_daily_journal(self):
  data=self.inputs();demand=f.project(**data);ctx=demand['contexts'][0];current={('a','BRL',ctx['context_fingerprint'])}
  class Transport:
   def get_json(self,path,params,timeout):
    return ['brl'] if path.endswith('supported_vs_currencies') else {'source-id':{'brl':100,'last_updated_at':int(NOW.timestamp())}}
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'data/instruments').mkdir(parents=True);(root/'data/universal_instrument_catalog.json').write_text(json.dumps({'instruments':[{'instrument_id':IID}]}))
   binding=dict(instrument_id=IID,provider='CoinGecko',provider_id='source-id',quote_currency='BRL',identity_source_ref='test',confirmed_by='reviewer',confirmed_at='2020-01-01T00:00:00+00:00',effective_from='2020-01-01')
   (root/b.REGISTRY).write_text(b.canonical({'schema':b.SCHEMA,'bindings':[binding]}))
   out=q._collect_coingecko(root,demand,now=NOW,transport=Transport(),revalidate=lambda:current)
   self.assertEqual(out['observations_created'],1,out);self.assertEqual(q.read_records(root)[0]['quote_currency'],'BRL');self.assertFalse(out['execution_performed'])
if __name__=='__main__':unittest.main()
