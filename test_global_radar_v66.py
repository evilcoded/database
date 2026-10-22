import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from universal_portfolio.global_radar_a24 import snapshot
from universal_portfolio.asset_resolver import AssetResolver

NOW=dt.datetime(2026,10,22,12,tzinfo=dt.timezone.utc)
class GlobalRadarTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  self.row={'instrument_id':'X:M:E:NEW','symbol':'NEW','asset_class':'EQUITY','market':'M','jurisdiction':'X','currency':'USD'}
  self.write('data/universal_instrument_catalog.json',{'instruments':[self.row]})
  self.write('static/data/asset_registry_v365.json',{'radar_seed':[{'symbol':'OLD','family':'CRYPTO'}]})
 def write(self,path,obj):
  p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj))
 def binding(self,q='BRL',pid='new-id'):
  return {'instrument_id':self.row['instrument_id'],'provider':'CoinGecko','provider_id':pid,'quote_currency':q,'identity_source_ref':'explicit-reference','confirmed_by':'reviewer','confirmed_at':'2026-10-21T00:00:00+00:00','effective_from':'2026-10-21'}
 def bind(self,rows):self.write('data/instruments/market_provider_bindings_a24.json',{'schema':'porquinho.explicit-market-bindings-a24/1.0','bindings':rows})
 def value(self,q='BRL',price=42):return {'provider_id':'new-id','currency':q,'price':price,'observed_at':'2026-10-22T11:55:00+00:00'}
 def test_new_catalog_asset_without_seed(self):
  result=snapshot(self.root,now=NOW,fetcher=lambda *a:[])
  self.assertEqual([r['symbol'] for r in result['assets']],['NEW']);self.assertEqual(result['assets'][0]['status'],'EXPLICIT_PROVIDER_QUOTE_BINDING_REQUIRED')
 def test_seed_not_used_by_resolver(self):
  self.assertEqual(AssetResolver(self.root).resolve_local('NEW').selected['instrument_id'],self.row['instrument_id'])
  self.assertIsNone(AssetResolver(self.root).resolve_local('OLD').selected)
 def test_explicit_brl_no_fx_or_catalog_currency_default(self):
  self.bind([self.binding()]);calls=[]
  def fetch(*a):calls.append(a);return [self.value()]
  out=snapshot(self.root,now=NOW,fetcher=fetch)
  self.assertEqual(calls,[('coingecko','BRL',['new-id'])]);self.assertEqual(out['assets'][0]['price'],42);self.assertEqual(out['assets'][0]['currency'],'BRL')
 def test_wrong_currency_refused(self):
  self.bind([self.binding()]);r=snapshot(self.root,now=NOW,fetcher=lambda *a:[self.value('EUR')])['assets'][0]
  self.assertIsNone(r['price']);self.assertEqual(r['status'],'PROVIDER_QUOTE_CURRENCY_MISMATCH')
 def test_duplicate_response_refused(self):
  self.bind([self.binding()]);r=snapshot(self.root,now=NOW,fetcher=lambda *a:[self.value(),self.value()])['assets'][0]
  self.assertEqual(r['status'],'AMBIGUOUS_PROVIDER_RESPONSE')
 def test_nan_and_future_refused(self):
  self.bind([self.binding()])
  for val in [self.value(price=float('nan')),{**self.value(),'observed_at':'2027-01-01T00:00:00+00:00'}]:
   self.assertIsNone(snapshot(self.root,now=NOW,fetcher=lambda *a:[val])['assets'][0]['price'])
 def test_conflicting_overlay_never_queried(self):
  self.bind([self.binding()]);self.write('data/instruments/manual_instruments.json',{'instruments':[{**self.row,'symbol':'OTHER'}]})
  def fail(*a):raise AssertionError('should not fetch')
  self.assertEqual(snapshot(self.root,now=NOW,fetcher=fail)['assets'][0]['status'],'CATALOG_IDENTITY_CONFLICT')
 def test_two_currencies_separate_and_no_project_writes(self):
  self.bind([self.binding(),self.binding('EUR')]);before={str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
  out=snapshot(self.root,now=NOW,fetcher=lambda p,q,ids:[self.value(q)])
  self.assertEqual({r['currency'] for r in out['assets']},{'BRL','EUR'})
  self.assertEqual(before,{str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
 def test_provider_failure_keeps_catalog(self):
  self.bind([self.binding()])
  def fail(*a):raise RuntimeError('network')
  out=snapshot(self.root,now=NOW,fetcher=fail);self.assertEqual(len(out['assets']),1);self.assertIsNone(out['assets'][0]['price']);self.assertTrue(out['issues'])
 def test_equal_symbol_different_global_identity_ambiguous(self):
  self.write('data/universal_instrument_catalog.json',{'instruments':[self.row,{**self.row,'instrument_id':'Y:M:E:NEW'}]})
  self.assertEqual(AssetResolver(self.root).resolve_local('NEW').status,'AMBIGUOUS')
if __name__=='__main__':unittest.main()

class TransportTests(unittest.TestCase):
 def test_coingecko_explicit_id_and_brl(self):
  from unittest.mock import patch
  from market_data.global_quote_transport_a24 import fetch
  with patch('market_data.global_quote_transport_a24.get_json',return_value=[{'id':'new-id','current_price':5,'last_updated':'2026-10-22T00:00:00Z'}]) as get:
   result=fetch('coingecko','BRL',['new-id'])
   self.assertEqual(get.call_args.args[1]['vs_currency'],'brl');self.assertEqual(get.call_args.args[1]['ids'],'new-id');self.assertEqual(result[0]['currency'],'BRL')
 def test_brapi_never_defaults_currency(self):
  from unittest.mock import patch
  from market_data.global_quote_transport_a24 import fetch
  with patch('market_data.global_quote_transport_a24.get_json',return_value={'results':[{'symbol':'NEW3','regularMarketPrice':5}]}):
   self.assertIsNone(fetch('brapi','BRL',['NEW3'])[0]['currency'])
 def test_unsupported_provider_no_network(self):
  from unittest.mock import patch
  from market_data.global_quote_transport_a24 import fetch
  with patch('market_data.global_quote_transport_a24.get_json') as get:
   with self.assertRaises(ValueError):fetch('unknown','BRL',['new-id'])
   get.assert_not_called()
 def test_service_uses_global_catalog(self):
  from unittest.mock import patch
  from market_data.service import MarketDataService
  with tempfile.TemporaryDirectory() as directory:
   with patch('universal_portfolio.global_radar_a24.snapshot',return_value={'assets':[]}) as snapshot_mock:
    self.assertEqual(MarketDataService(directory).radar_snapshot(),{'assets':[]});snapshot_mock.assert_called_once_with(Path(directory))
