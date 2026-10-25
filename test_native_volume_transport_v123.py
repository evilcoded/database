import copy,datetime as dt,unittest
from unittest.mock import patch
import pandas as pd
import test_a24_global_research_lab as fixture
from universal_portfolio import global_history_source_a24 as h
from universal_portfolio import native_history_volume_a24 as native
from universal_portfolio.recovered_history_composition_a24 import compose
from brain.evolution import global_existing_lab_a24 as lab

class Transport(unittest.TestCase):
 def setUp(self):
  self.f=fixture.Lab();self.f.setUp();self.addCleanup(self.f.doCleanups);self.now=fixture.NOW
 def brapi(self,n=130):
  binding=self.f.f.f.rows(provider='brapi',provider_id='TEST3')
  rows=[{'date':int((self.now-dt.timedelta(days=i)).timestamp()),'close':100+(n-i)*.2+(i%7)*.07,'volume':1000+(i%9)*50} for i in range(n,0,-1)]
  response={'results':[{'symbol':'TEST3','currency':binding['quote_currency'],'historicalDataPrice':rows}]}
  return h.bundle(binding,response,now=self.now,binding_digest='synthetic')
 def test_mixed_provider_rows_are_not_dropped_for_missing_monetary_volume(self):
  crypto=self.f.body();equity=self.brapi();before=copy.deepcopy(equity)
  oldrows=[]
  for b in (crypto,equity):
   for r in b['observations']:oldrows.append({**b['binding'],'asset':b['binding']['instrument_id'],'date':r['observation_date'],'price':r['price'],'volume':r.get('volume_24h'),'market_cap':r.get('market_cap')})
  original,_=lab.legacy._features(pd.DataFrame(oldrows));self.assertFalse((original['provider'].str.lower()=='brapi').any())
  x,features=lab.input_frame([crypto,equity]);eq=x[x['provider'].str.lower()=='brapi']
  self.assertGreater(len(eq),50);self.assertEqual(len(features),14);self.assertEqual(equity,before)
  self.assertTrue(eq['_a24_market_cap'].isna().all());self.assertTrue((eq['input_volume_semantics']==native.KIND).all())
  self.assertTrue((eq['liquidity']==35).all());self.assertTrue(eq['rel_volume'].notna().all())
  report=lab.input_coverage([crypto,equity],x);r=next(r for r in report if r['provider'].lower()=='brapi');self.assertEqual(r['feature_row_count'],len(eq));self.assertEqual(r['native_volume_feature_rows'],len(eq));self.assertFalse(r['model_validation_proven'])
 def test_missing_volume_does_not_become_zero_or_one(self):
  b=self.brapi();response=copy.deepcopy(b['source_response'])
  for row in response['results'][0]['historicalDataPrice']:row.pop('volume')
  b=h.bundle(b['binding'],response,now=self.now,binding_digest='synthetic');self.assertEqual(native.project(b),{})
  x,_=lab.input_frame([self.f.body(),b]);self.assertFalse((x['provider'].str.lower()=='brapi').any())
 def test_monetary_coingecko_features_unchanged(self):
  body=self.f.body();x,features=lab.input_frame([body]);rows=[]
  for r in body['observations']:rows.append({**body['binding'],'asset':body['binding']['instrument_id'],'date':r['observation_date'],'price':r['price'],'volume':r.get('volume_24h'),'market_cap':r.get('market_cap')})
  original,old_features=lab.legacy._features(pd.DataFrame(rows));self.assertEqual(features,old_features)
  pd.testing.assert_frame_equal(x[features],original[features]);self.assertEqual(native.project(body),{})
 def test_recovered_prefix_requires_matching_native_volume_overlap(self):
  full=self.brapi(180);base_response=copy.deepcopy(full['source_response']);base_response['results'][0]['historicalDataPrice']=base_response['results'][0]['historicalDataPrice'][-80:]
  base=h.bundle(full['binding'],base_response,now=self.now,binding_digest='synthetic')
  recovered={'source':'brapi.dev','usedInterval':'1d','points':full['source_response']['results'][0]['historicalDataPrice']}
  merged=compose(base,recovered,'a'*64,at=self.now);self.assertEqual(len(native.project(merged)),180)
  changed=copy.deepcopy(recovered);changed['points'][-1]['volume']+=1
  merged=compose(base,changed,'b'*64,at=self.now);self.assertEqual(len(native.project(merged)),80)
 def test_bad_volume_refused_and_input_not_mutated(self):
  b=self.brapi();response=copy.deepcopy(b['source_response'])
  for val in (None,True,-1,'NaN','Infinity'):
   response['results'][0]['historicalDataPrice'][0]['volume']=val
   changed=h.bundle(b['binding'],response,now=self.now,binding_digest='synthetic');self.assertEqual(len(native.project(changed)),129)
 def test_existing_monetary_volume_not_overridden(self):
  b=self.f.body();x,_=lab.input_frame([b]);self.assertTrue((x['input_volume_semantics']=='SOURCE_MONETARY_VOLUME_OR_UNAVAILABLE').all())
if __name__=='__main__':unittest.main()
