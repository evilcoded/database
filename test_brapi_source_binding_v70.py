import datetime as dt,json,tempfile,unittest
from pathlib import Path
from universal_portfolio.brapi_source_binding_a24 import check,discover,apply
from universal_portfolio.explicit_market_bindings_a24 import load
NOW=dt.datetime.now(dt.timezone.utc)-dt.timedelta(seconds=10)
class Tests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name)
  self.row={'instrument_id':'BR:B3:EQUITY:NEW3','symbol':'NEW3','market':'B3','jurisdiction':'BR','asset_class':'EQUITY','currency':'BRL','catalog_status':'GLOBAL_CATALOG_REGISTERED'}
  self.listing={'stocks':[{'stock':'NEW3','type':'stock','name':'New'}]}
  self.quote={'results':[{'symbol':'NEW3','currency':'BRL','regularMarketPrice':10,'regularMarketTime':(NOW-dt.timedelta(hours=1)).isoformat()}]}
  self.write('data/universal_instrument_catalog.json',{'instruments':[self.row]})
 def write(self,p,v):
  path=self.root/p;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(v))
 def fetch(self,url,*args,**kw):return self.listing if '/list' in url else self.quote
 def test_checked_and_preserves_existing_financial_files(self):
  self.write('data/positions.json',{'unchanged':True});before=(self.root/'data/positions.json').read_bytes()
  r=discover(self.root,now=NOW,fetcher=self.fetch,pause=lambda _:None);out=apply(self.root,r,now=NOW)
  self.assertEqual(out['added'],1);self.assertFalse(r['independent_attestation'])
  self.assertEqual(load(self.root)['bindings'][0]['provider_id'],'NEW3');self.assertEqual((self.root/'data/positions.json').read_bytes(),before)
  self.assertEqual(apply(self.root,discover(self.root,now=NOW,fetcher=self.fetch,pause=lambda _:None),now=NOW)['added'],0)
 def test_class_not_inferred_from_ticker(self):
  self.listing['stocks'][0]['type']='bdr';self.assertEqual(check(self.row,self.listing,self.quote,now=NOW)[0],'SOURCE_CLASS_MISMATCH')
 def test_currency_mismatch(self):
  self.quote['results'][0]['currency']='EUR';self.assertIsNone(check(self.row,self.listing,self.quote,now=NOW)[1])
 def test_missing_catalog_currency(self):
  self.assertEqual(check({**self.row,'currency':None},self.listing,self.quote,now=NOW)[0],'CATALOG_CURRENCY_REQUIRED')
 def test_symbol_ambiguity(self):
  self.listing['stocks']*=2;self.assertIsNone(check(self.row,self.listing,self.quote,now=NOW)[1])
 def test_stale_future_and_invalid_prices(self):
  for value in ['2027-01-01T00:00:00Z','2026-01-01T00:00:00Z',None]:
   self.quote['results'][0]['regularMarketTime']=value;self.assertIsNone(check(self.row,self.listing,self.quote,now=NOW)[1])
 def test_no_retroactive_route(self):
  r=discover(self.root,now=NOW,fetcher=self.fetch,pause=lambda _:None);apply(self.root,r,now=NOW)
  self.assertEqual(load(self.root)['bindings'][0]['effective_from'],NOW.date().isoformat())
 def test_catalog_change_cancels(self):
  r=discover(self.root,now=NOW,fetcher=self.fetch,pause=lambda _:None);self.write('data/universal_instrument_catalog.json',{'instruments':[]})
  with self.assertRaises(ValueError):apply(self.root,r,now=NOW)
  self.assertEqual(load(self.root)['bindings'],[])
 def test_errors_redacted(self):
  def fail(*a,**kw):raise RuntimeError('SECRET')
  r=discover(self.root,now=NOW,fetcher=fail,pause=lambda _:None);self.assertNotIn('SECRET',str(r));self.assertEqual(apply(self.root,r,now=NOW)['added'],0)
