import copy,datetime as dt,hashlib,json,unittest
from tests import test_brapi_history_source_v75 as fixture
from universal_portfolio import global_history_source_a24 as h
from universal_portfolio import recovered_history_composition_a24 as c
from brain.evolution.global_research_lab_a24 import sources,experiment
class Tests(unittest.TestCase):
 def setUp(self):
  self.f=fixture.Tests();self.f.setUp();self.addCleanup(self.f.doCleanups);self.root=self.f.root;self.now=self.f.now
  points=[{'date':int((self.now-dt.timedelta(days=i)).timestamp()),'close':100+i} for i in range(200,19,-1)]
  self.old={'source':'brapi.dev','usedInterval':'1d','points':points}
  self.f.data['results'][0]['historicalDataPrice']=[{'date':int((self.now-dt.timedelta(days=i)).timestamp()),'close':100+i} for i in range(62,0,-1)]
  self.base=h.bundle(self.f.binding,self.f.data,now=self.now,binding_digest='fixture')
 def test_composition_extends_without_certifying_currency(self):
  body=c.compose(self.base,self.old,'fixture',at=self.now);c.validate(body)
  self.assertEqual(len(body['observations']),200);self.assertEqual(body['overlap_day_count'],43)
  self.assertFalse(body['historical_row_attestation']);self.assertFalse(body['execution_authorized']);self.assertFalse(body['canonical_publication_authorized'])
  self.assertNotEqual(body['series_id'],self.base['series_id']);self.assertIsNone(body['observations'][0]['volume_24h'])
 def test_divergence_refused(self):
  self.old['points'][-1]['close']+=1
  with self.assertRaisesRegex(ValueError,'OVERLAPPING_CLOSES_DIVERGE'):c.compose(self.base,self.old,'fixture',at=self.now)
 def test_explicit_currency_conflict_refused(self):
  self.old['currency']='USD'
  with self.assertRaisesRegex(ValueError,'EXPLICIT_RECOVERED_CONTEXT_CONFLICT'):c.compose(self.base,self.old,'fixture',at=self.now)
 def test_insufficient_overlap_refused(self):
  self.old['points']=self.old['points'][:150]
  with self.assertRaisesRegex(ValueError,'MORE_OVERLAP_EVIDENCE_REQUIRED'):c.compose(self.base,self.old,'fixture',at=self.now)
 def test_originals_unchanged_and_tampering_rejected(self):
  old=copy.deepcopy(self.old);base=copy.deepcopy(self.base)
  body=c.compose(self.base,self.old,'fixture',at=self.now)
  self.assertEqual(self.old,old);self.assertEqual(self.base,base)
  body['observations'][0]['price']='999'
  with self.assertRaises(ValueError):c.validate(body)
 def test_storage_and_existing_lab_source_selection(self):
  raw=json.dumps({'schema':'porquinho.equity-historical/1.0','series':{'NEW3':self.old}}).encode();sha=hashlib.sha256(raw).hexdigest()
  p=self.root/'data/recovered_market_sources_a24'/sha/'ohlcv.json';p.parent.mkdir(parents=True);p.write_bytes(raw)
  path=self.root/h.STORE/'bundles'/self.base['series_id']/(self.now.date().isoformat()+'.json');h.store_once(path,self.base)
  # Align the fixture's source binding digest to the actual current registry.
  from universal_portfolio.explicit_market_bindings_a24 import load,digest
  self.base['binding_digest']=digest(load(self.root));path.unlink();h.store_once(path,self.base)
  before=path.read_bytes();out=c.collect(self.root,self.f.f.demand,now=self.now,revalidate=self.f.f.current)
  self.assertEqual(out['compositions_created'],1)
  _,eligible,latest=sources(self.root,self.f.f.demand,self.now)
  self.assertEqual(len(latest),1);key=next(iter(latest));self.assertNotEqual(key,self.base['series_id']);self.assertIn(key,eligible)
  body=latest[key][1];self.assertEqual(len(body['observations']),200);self.assertEqual(path.read_bytes(),before);self.assertEqual(p.read_bytes(),raw)
  out=c.collect(self.root,self.f.f.demand,now=self.now,revalidate=self.f.f.current);self.assertEqual(out['compositions_created'],0)
  self.assertEqual(experiment(body,now=self.now)['provider'],'brapi')
