"""Batch eligibility uses real synthetic research fixtures, not fake production approvals."""
import unittest
from unittest.mock import patch
from universal_portfolio import research_economic_components_a24 as c,global_history_source_a24 as h
import test_a24_research_economic_components as fixture
class Batch(unittest.TestCase):
 def setUp(self):
  self.f=fixture.Components();self.f.setUp();self.addCleanup(self.f.doCleanups);self.f.seed();self.f.demand=self.f.f.f.f.demand(duplicate_account=True)
 def test_all_ready_accounts_same_cycle_and_repeat_preserves_bytes(self):
  r=self.f.runproducer();self.assertEqual(r['packets_created'],2);self.assertEqual(r['eligible_packet_count'],2)
  self.assertEqual(self.f.summary()['packet_count'],2)
  before={p:(p.read_bytes(),p.stat().st_mtime_ns) for p in (self.f.root/c.STORE/'packets').rglob('*.json')}
  again=self.f.runproducer();self.assertEqual(again['packets_created'],0);self.assertEqual(again['packets_already_current'],2)
  self.assertEqual(before,{p:(p.read_bytes(),p.stat().st_mtime_ns) for p in before})
 def test_eligibility_change_between_writes_stops_and_reports_partial_progress(self):
  calls=[]
  def revalidate():
   calls.append(1);return self.f.current() if len(calls)==1 else set()
  r=c.run(self.f.root,self.f.demand,now=fixture.NOW,revalidate=revalidate)
  self.assertEqual(len(calls),2);self.assertEqual(r['status'],'RESEARCH_COMPONENT_PRODUCTION_UNAVAILABLE');self.assertEqual(r['packets_created'],1)
  self.assertEqual(len(list((self.f.root/c.STORE/'packets').rglob('*.json'))),1)
 def test_no_network_or_unrelated_model_write(self):
  before={p:p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()}
  with patch.object(h.Transport,'get_json',side_effect=AssertionError('NO_NETWORK')):r=self.f.runproducer()
  self.assertEqual(r['packets_created'],2);self.assertEqual(r['network_requests'],0)
  for p,b in before.items():self.assertEqual(p.read_bytes(),b)
 def test_failed_second_write_retains_first_packet_and_truthful_count(self):
  real=h.store_once;calls=[]
  def store(path,body):
   calls.append(1)
   if len(calls)==2:raise OSError('synthetic disk failure')
   return real(path,body)
  with patch.object(h,'store_once',side_effect=store):r=self.f.runproducer()
  self.assertEqual(r['packets_created'],1);self.assertEqual(r['error_type'],'OSError');self.assertEqual(len(list((self.f.root/c.STORE/'packets').rglob('*.json'))),1)
if __name__=='__main__':unittest.main()
