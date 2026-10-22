import json,unittest
from tests import test_brapi_history_source_v75 as fixture
from universal_portfolio import global_history_source_a24 as h
from universal_portfolio.brapi_history_source_a24 import settings,request
class Tests(unittest.TestCase):
 def setUp(self):
  self.f=fixture.Tests();self.f.setUp();self.addCleanup(self.f.doCleanups);self.root=self.f.root
 def config(self,period):
  p=self.root/'config/market_history_requests_a24.json';p.parent.mkdir(exist_ok=True);p.write_text(json.dumps({'schema':'porquinho.history-request-settings/1.0','providers':{'brapi':{'range':period,'interval':'1d'}}}))
 def test_configured_range_sent_and_sealed(self):
  self.config('3mo');calls=[];outer=self
  class T:
   def get_json(self,path,params,timeout):calls.append(params);return outer.f.data
  result=h.collect(self.root,self.f.f.demand,now=self.f.now,transport=T(),revalidate=self.f.f.current)
  self.assertEqual(result['bundles_created'],1);self.assertEqual(calls,[{'range':'3mo','interval':'1d'}])
  p=next((self.root/h.STORE/'bundles').glob('*/*.json'));body=h.validate_bundle(h.read_sealed(p),p)
  self.assertIsNone(body['requested_days']);self.assertEqual(body['requested_range'],'3mo')
 def test_different_windows_do_not_share_id(self):
  b=self.f.binding
  self.assertNotEqual(h.series_id(b,{'range':'3mo','interval':'1d'}),h.series_id(b))
  self.assertEqual(h.series_id(b,{'range':'1y','interval':'1d'}),h.series_id(b))
 def test_no_plan_name_rules(self):
  self.config('6mo');self.assertEqual(settings(self.root)['range'],'6mo')
  self.assertEqual(request(self.f.binding,settings(self.root))[1]['range'],'6mo')
 def test_invalid_settings_refused(self):
  self.config('invalid')
  with self.assertRaises(ValueError):settings(self.root)
 def test_lab_source_selection_matches_configured_window(self):
  self.config('3mo');outer=self
  class T:
   def get_json(self,*a,**kw):return outer.f.data
  h.collect(self.root,self.f.f.demand,now=self.f.now,transport=T(),revalidate=self.f.f.current)
  from brain.evolution.global_research_lab_a24 import sources
  _,eligible,latest=sources(self.root,self.f.f.demand,self.f.now)
  self.assertEqual(len(latest),1);self.assertEqual(set(latest),set(eligible))
