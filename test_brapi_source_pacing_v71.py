import unittest
from tests.test_brapi_source_binding_v70 import Tests,NOW
from universal_portfolio.brapi_source_binding_a24 import discover
class PacingTests(Tests):
 def test_429_stops_all_following_requests(self):
  self.write('data/universal_instrument_catalog.json',{'instruments':[self.row,{**self.row,'instrument_id':'BR:B3:EQUITY:OTHER','symbol':'OTHER'}]})
  calls=[]
  def fail(*args,**kw):calls.append(args);raise RuntimeError('PROVIDER_HTTP_429')
  r=discover(self.root,now=NOW,fetcher=fail,pause=lambda _:None)
  self.assertEqual(len(calls),1);self.assertTrue(r['rate_limit_stop']);self.assertEqual(r['network_requests'],1)
  self.assertEqual([x['status'] for x in r['rows']],['PROVIDER_HTTP_429','DEFERRED_AFTER_RATE_LIMIT'])
 def test_spacing_between_requests(self):
  pauses=[];r=discover(self.root,now=NOW,fetcher=self.fetch,pause=pauses.append)
  self.assertEqual(pauses,[3]);self.assertEqual(r['network_requests'],2)
 def test_missing_symbol_skips_quote_request(self):
  calls=[]
  def empty(*args,**kw):calls.append(args);return {'stocks':[]}
  r=discover(self.root,now=NOW,fetcher=empty,pause=lambda _:None)
  self.assertEqual(len(calls),1);self.assertEqual(r['rows'][0]['status'],'SOURCE_SYMBOL_NOT_FOUND_OR_AMBIGUOUS')
