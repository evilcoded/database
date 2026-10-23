import ast,copy,sys,unittest
from pathlib import Path
sys.path.insert(0,'/workspace/porquinho-a24/project')
from universal_portfolio.canonical_opportunity_manual_trade import build_trade_draft,ManualTradeDraftError
source=Path('/workspace/porquinho-a24/project/webapp/universal_position_router_api_v38275.py').read_text();tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='capability');namespace={};exec(compile(ast.Module(body=[node],type_ignores=[]),'capability','exec'),namespace);capability=namespace['capability']
class Tests(unittest.TestCase):
 def test_crypto_reuses_existing_flow(self):
  for currency in ('EUR','BRL','USD'):
   r=capability(dict(instrument_id='global-id',asset_class='CRYPTO',market='GLOBAL',currency=currency));self.assertEqual(r['route'],'EXISTING_MANUAL_EXTERNAL_TRADE');self.assertNotEqual(r['position_registration'],'SUPPORTED')
 def test_explicit_market_identity_required(self):
  for market in ('',None):self.assertEqual(capability(dict(instrument_id='id',asset_class='CRYPTO',market=market))['position_registration'],'UNSUPPORTED')
 def test_class_conflict_refused(self):self.assertEqual(capability(dict(instrument_id='id',asset_class='CRYPTO',market='GLOBAL',catalog_status='CATALOG_IDENTITY_CONFLICT'))['position_registration'],'UNSUPPORTED')
 def test_other_domains_unchanged(self):
  self.assertEqual(capability(dict(asset_class='EQUITY',market='B3'))['route'],'BR_EQUITY_SPECIALIZED');self.assertEqual(capability(dict(asset_class='FIXED_INCOME'))['route'],'FIXED_INCOME_SPECIALIZED')
 def test_same_draft_boundary_for_all_currencies(self):
  for currency in ('BRL','EUR','USD'):
   catalog={'instruments':[dict(instrument_id='global-id',asset_class='CRYPTO',market='GLOBAL',jurisdiction='GLOBAL',currency=currency,status='KNOWN',source='TEST_CATALOG')]};accounts={'accounts':[dict(account_id='account',currency=currency)]};trade=dict(account_id='account',instrument_id='global-id',transaction_type='BUY',quantity='2',unit_price='50',gross_amount='100',transaction_currency=currency,executed_at='2026-10-23T09:00:00+00:00',funding_source='REGISTERED_ACCOUNT_CASH',provenance={'source':'MANUAL_EXTERNAL_TRADE'})
   before=copy.deepcopy((catalog,accounts,trade));draft=build_trade_draft(catalog=catalog,accounts=accounts,trade=trade);self.assertEqual(draft.transaction_currency,currency);self.assertFalse(draft.ledger_write);self.assertFalse(draft.position_direct_write);self.assertEqual((catalog,accounts,trade),before)
if __name__=='__main__':unittest.main()
