import datetime as dt,json,tempfile,unittest
from pathlib import Path
from universal_portfolio import manual_execution_availability_a24 as m
NOW=dt.datetime(2026,10,22,12,tzinfo=dt.timezone.utc)
class Availability(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name);(self.root/m.STORE).mkdir(parents=True)
 def add(self,status='UNAVAILABLE',stamp='2026-10-22T10:00:00+00:00',account='account-A'):
  r={'schema':m.SCHEMA,'account_id':account,'instrument_id':'EXACT:ASSET','currency':'BRL','channel':'BANK_APP','status':status,'observed_at':stamp,'source_kind':'USER_REPORT'};r['record_id']=m.record_id(r);(self.root/m.STORE/(r['record_id']+'.json')).write_text(json.dumps(r));return r
 def status(self,account='account-A',currency='BRL',iid='EXACT:ASSET'):
  return m.scenario_status(m.inspect(self.root,now=NOW),account,currency,{'legs':[{'instrument_id':iid}]})['status']
 def test_unknown_not_unavailable(self):self.assertEqual(self.status(),'AVAILABILITY_NOT_CONFIRMED')
 def test_exact_declaration_applies_only_to_declared_route(self):
  self.add();self.assertEqual(self.status(),'USER_REPORTED_UNAVAILABLE');self.assertEqual(self.status(account='account-B'),'AVAILABILITY_NOT_CONFIRMED');self.assertEqual(self.status(currency='EUR'),'AVAILABILITY_NOT_CONFIRMED');self.assertEqual(self.status(iid='OTHER:ASSET'),'AVAILABILITY_NOT_CONFIRMED')
 def test_new_available_record_overrides_old_without_deleting_history(self):
  self.add();self.add('AVAILABLE','2026-10-22T11:00:00+00:00');self.assertEqual(self.status(),'USER_REPORTED_AVAILABLE');self.assertEqual(len(list((self.root/m.STORE).glob('*.json'))),2)
 def test_new_unknown_forces_review(self):
  self.add();self.add('UNKNOWN','2026-10-22T11:00:00+00:00');self.assertEqual(self.status(),'AVAILABILITY_NOT_CONFIRMED')
 def test_conflicting_same_timestamp_not_selected(self):
  self.add();self.add('AVAILABLE');self.assertEqual(self.status(),'AVAILABILITY_NOT_CONFIRMED')
 def test_record_tampering_not_trusted(self):
  r=self.add();p=self.root/m.STORE/(r['record_id']+'.json');r['status']='AVAILABLE';p.write_text(json.dumps(r));self.assertEqual(m.inspect(self.root,now=NOW)['status'],'ROUTE_DECLARATIONS_UNAVAILABLE')
 def test_no_mutation_on_read(self):
  self.add();before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()};self.status();self.assertEqual(before,{p:p.read_bytes() for p in before})
if __name__=='__main__':unittest.main()
