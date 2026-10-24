import datetime as dt,json,tempfile,unittest
from pathlib import Path
from test_global_dashboard_v118 import NOW,cockpit
from universal_portfolio.global_dashboard_observations_a24 import capture,STORE,digest
from universal_portfolio.observed_finance_intraday_a24 import build

class ObservedIntraday(unittest.TestCase):
 def test_more_than_four_actual_points_zero_delta_is_valid_and_get_never_writes(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);c=cockpit()
   for i in range(6):
    at=NOW+dt.timedelta(minutes=i*10)
    for p in (c['positions'][0],c['positions'][2]):p['reference_quote_at']=at.isoformat()
    capture(root,c,now=at,revalidate=lambda:c)
   before={str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()};result=build(root,now=at)
   series=next(s for s in result['series'] if s['currency']=='BRL' and s['account_id'] is None)
   self.assertEqual(len(series['points']),6);self.assertEqual(series['points'][0]['pnl'],'-15')
   self.assertEqual(before,{str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()});self.assertEqual(result['batch_count'],6)
   self.assertEqual(next(s for s in result['series'] if s['currency']=='EUR' and s['account_id'] is None)['points'][0]['pnl'],'-18')
 def test_midnight_included_and_future_excluded(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);c=cockpit();before=NOW.replace(hour=23,minute=55);after=before+dt.timedelta(minutes=10)
   for at in (before,after,after+dt.timedelta(hours=1)):
    for p in (c['positions'][0],c['positions'][2]):p['reference_quote_at']=at.isoformat()
    capture(root,c,now=at,revalidate=lambda:c)
   r=build(root,now=after);self.assertEqual(r['batch_count'],2);self.assertEqual(len(r['series'][0]['points']),2)
 def test_corruption_refused_not_empty_success(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);p=root/STORE/'2026-10-24.jsonl';p.parent.mkdir(parents=True);p.write_text('{partial')
   r=build(root,now=NOW);self.assertFalse(r['series']);self.assertEqual(len(r['issues']),1)
 def test_conflicting_duplicate_timestamp_not_arbitrarily_selected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);c=cockpit();capture(root,c,now=NOW,revalidate=lambda:c)
   c['positions'][0].update(reference_market_value='480',reference_pnl='-20');capture(root,c,now=NOW,revalidate=lambda:c)
   r=build(root,now=NOW);self.assertEqual(r['conflicting_point_count'],2);self.assertFalse([s for s in r['series'] if s['currency']=='BRL'])
if __name__=='__main__':unittest.main()
