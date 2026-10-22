import copy,datetime as dt,unittest
from tests import test_a24_global_history_source as fixture
from universal_portfolio import global_history_source_a24 as h
from universal_portfolio.brapi_history_source_a24 import points,SAMPLING
class Tests(unittest.TestCase):
 def setUp(self):
  self.f=fixture.History();self.f.setUp();self.addCleanup(self.f.doCleanups)
  self.root=self.f.root;self.now=fixture.NOW
  self.binding=self.f.f.rows(provider='brapi',provider_id='NEW3');self.f.f.save([self.binding])
  self.data={'results':[{'symbol':'NEW3','currency':'BRL','historicalDataPrice':[{'date':int((self.now-dt.timedelta(days=i)).timestamp()),'close':100+i,'volume':300} for i in range(130,0,-1)]}]}
 def test_native_close_semantics_and_immutable_bundle(self):
  b=h.bundle(self.binding,self.data,now=self.now,binding_digest='x');h.validate_bundle(b)
  self.assertEqual(b['sampling'],SAMPLING);self.assertIn('NATIVE_CURRENCY_CLOSE',b['pricing_method']);self.assertEqual(len(b['observations']),130)
  self.assertIsNone(b['observations'][0]['volume_24h']);self.assertFalse(b['historical_row_attestation'])
 def test_collector_dispatches_brapi_request(self):
  calls=[];outer=self
  class Transport:
   def get_json(self,path,params,timeout):calls.append((path,params));return outer.data
  result=h.collect(self.root,self.f.demand,now=self.now,transport=Transport(),revalidate=self.f.current)
  self.assertEqual(result['bundles_created'],1);self.assertEqual(calls,[('/api/quote/NEW3',{'range':'1y','interval':'1d'})])
  result=h.collect(self.root,self.f.demand,now=self.now,transport=Transport(),revalidate=self.f.current)
  self.assertEqual(result['network_requests'],0);self.assertEqual(len(calls),1)
 def test_wrong_currency_or_symbol(self):
  for key,value in [('currency','EUR'),('symbol','OTHER')]:
   d=copy.deepcopy(self.data);d['results'][0][key]=value
   with self.assertRaises(h.HistoryError):points(self.binding,d,self.now)
 def test_duplicate_days_refused(self):
  self.data['results'][0]['historicalDataPrice']*=2
  with self.assertRaises(h.HistoryError):points(self.binding,self.data,self.now)
 def test_current_day_excluded(self):
  self.data['results'][0]['historicalDataPrice'].append({'date':int(self.now.timestamp()),'close':150})
  self.assertEqual(len(points(self.binding,self.data,self.now)),130)
 def test_nonpositive_or_nonfinite_prices(self):
  for value in [True,0,-1,float('nan')]:
   d=copy.deepcopy(self.data);d['results'][0]['historicalDataPrice'][0]['close']=value
   with self.assertRaises(h.HistoryError):points(self.binding,d,self.now)
 def test_lab_accepts_validated_history_without_changing_method(self):
  from brain.evolution.global_research_lab_a24 import experiment,METHOD
  b=h.bundle(self.binding,self.data,now=self.now,binding_digest='x')
  out=experiment(b,now=self.now)
  self.assertEqual(out['method'],METHOD);self.assertEqual(out['provider'],'brapi')
  self.assertFalse(out['canonical_publication_authorized'])
