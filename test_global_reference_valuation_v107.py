import copy,datetime as dt,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'/workspace/porquinho-a24/project')
from universal_portfolio.position_reference_reconciliation_a24 import from_runtime
from universal_portfolio.monitor_consolidation_a24 import position_records
from universal_portfolio.universal_cockpit_a24 import project
from universal_portfolio.live_financial_projection import build as live_build
NOW=dt.datetime(2026,10,23,10,tzinfo=dt.timezone.utc)
class Tests(unittest.TestCase):
 def setUp(self):
  self.positions=[dict(account_reference='a',account_status='EXPLICIT_TRANSACTION_ACCOUNT',portfolio_id=None,instrument_id='financial-id',currency='BRL',quantity='2',cost_basis='100')]
  self.runtime=dict(schema='porquinho.canonical-runtime-read-model/1.0',authority='NONE',ledger_write=False,ledger_verified={'head_hash':'a'*64},positions=self.positions,cash=[{'account_id':'a','currency':'BRL','amount':'1000'}])
  self.registered={'a':{'account_id':'a','institution_id':'bank','currency':'BRL'}}
  self.registry={'institutions':[{'institution_id':'bank','name':'Example','country':'BR'}],'accounts':list(self.registered.values())}
  self.alias=[dict(position_instrument_id='financial-id',research_instrument_id='research-id',evidence_ref='reviewed-identity')]
  self.bindings=[dict(instrument_id='research-id',quote_currency='BRL',provider='CoinGecko',provider_id='provider-id',identity_source_ref='reviewed-source',confirmed_at='2020-01-01T00:00:00+00:00',effective_from='2020-01-01')]
  self.observations=[dict(instrument_id='research-id',quote_currency='BRL',provider='CoinGecko',provider_id='provider-id',price='60',fetched_at='2026-10-23T09:55:00+00:00')]
 def chain(self):return from_runtime(runtime=self.runtime,research_links=self.alias,quote_bindings=self.bindings,accounts=self.registered,now=NOW)
 def facts(self):return project(position_records(self.positions),self.runtime['cash'],self.registry,{'instruments':[]},self.observations,observed_at=NOW.isoformat(),reference_links=self.chain(),bindings=self.bindings)
 def test_new_ledger_position_values_without_binding_write(self):
  before=copy.deepcopy((self.runtime,self.alias,self.bindings));r=self.facts()['positions'][0];self.assertEqual(r['reference_market_value'],'120');self.assertEqual(r['reference_pnl'],'20');self.assertEqual(r['reference_quote_age_seconds'],300);self.assertFalse(r['reference_is_execution_quote']);self.assertEqual((self.runtime,self.alias,self.bindings),before)
 def test_no_alias_no_bridge(self):self.alias=[];self.assertIsNone(self.facts()['positions'][0]['reference_market_value'])
 def test_wrong_registered_currency_no_bridge(self):self.registered['a']['currency']='EUR';self.assertEqual(self.chain(),[])
 def test_no_verified_head_no_bridge(self):
  self.runtime['ledger_verified']={}
  with self.assertRaises(ValueError):self.chain()
 def test_unverified_position_account_not_bridged(self):self.positions[0]['account_status']='GUESSED';self.assertEqual(self.chain(),[])
 def test_duplicate_provider_bindings_refused(self):self.bindings*=2;self.assertEqual(self.chain(),[])
 def test_duplicate_position_scope_refused(self):self.positions*=2;self.assertEqual(self.chain(),[])
 def test_quote_currency_and_provider_isolation(self):
  for key,value in [('quote_currency','EUR'),('provider_id','another')]:
   self.setUp();self.observations[0][key]=value;self.assertIsNone(self.facts()['positions'][0]['reference_market_value'])
 def test_future_and_naive_quote_refused(self):
  for stamp in ('2026-10-23T11:00:00+00:00','2026-10-23T09:00:00'):
   self.observations[0]['fetched_at']=stamp;self.assertIsNone(self.facts()['positions'][0]['reference_market_value'])
 def test_live_accounts_use_same_global_valuation_and_ignore_ticker_snapshot(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'data').mkdir();p=root/'data/institution_accounts.json';p.write_text(json.dumps(self.registry));before=p.read_bytes();chain=self.chain()
   with patch('universal_portfolio.live_financial_projection.build_runtime',return_value=self.runtime),patch('universal_portfolio.global_radar_a24.catalog',return_value=([],[])),patch('universal_portfolio.explicit_market_bindings_a24.load',return_value={'bindings':self.bindings}),patch('universal_portfolio.research_quote_acquisition_a24.read_records',return_value=self.observations),patch('universal_portfolio.position_reference_reconciliation_a24.load',return_value=chain):
    out=live_build(root,{'scores':[{'asset':'financial-id','price_eur':999999}]})
   self.assertEqual(out['positions'][0]['market_value'],120);self.assertEqual(out['positions'][0]['reference_pnl'],'20');self.assertEqual(out['currency_totals']['BRL']['wealth'],1120);self.assertFalse(out['cross_currency_aggregation']);self.assertEqual(p.read_bytes(),before);self.assertEqual(len(list(root.rglob('*'))),2)
if __name__=='__main__':unittest.main()
