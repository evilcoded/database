import datetime as dt,tempfile,unittest
from pathlib import Path
from test_global_dashboard_v118 import cockpit,NOW
from universal_portfolio.global_dashboard_observations_a24 import capture,read

class Intraday(unittest.TestCase):
 def test_all_observations_not_only_four_and_account_currency_separation(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);c=cockpit()
   for i in range(10):
    at=NOW+dt.timedelta(minutes=i*10)
    c['positions'][0].update(reference_quote_at=at.isoformat(),reference_market_value=str(485+i),reference_pnl=str(-15+i))
    c['positions'][2]['reference_quote_at']=at.isoformat()
    capture(root,c,now=at,revalidate=lambda:c)
   r=read(root,at);br=next(s for s in r['intraday'] if s['currency']=='BRL' and s['account_id'] is None)
   self.assertEqual(len(br['points']),10);self.assertEqual(br['points'][-1]['pnl'],'-6')
   eu=next(s for s in r['intraday'] if s['currency']=='EUR' and s['account_id'] is None);self.assertEqual(eu['points'][-1]['pnl'],'-18')
   change=next(s for s in r['changes'] if s['currency']=='BRL' and s['account_id'] is None);self.assertEqual(change['value'],'1');self.assertEqual(change['interval_seconds'],600)
 def test_midnight_and_longer_observed_interval_are_supported(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);c=cockpit();before=NOW.replace(hour=23,minute=50);after=before+dt.timedelta(minutes=50)
   for p in (c['positions'][0],c['positions'][2]):p['reference_quote_at']=before.isoformat()
   capture(root,c,now=before,revalidate=lambda:c)
   c['positions'][0].update(reference_quote_at=after.isoformat(),reference_market_value='480',reference_pnl='-20')
   c['positions'][2]['reference_quote_at']=after.isoformat();capture(root,c,now=after,revalidate=lambda:c)
   r=read(root,after);br=next(s for s in r['changes'] if s['currency']=='BRL' and s['account_id'] is None)
   self.assertEqual(br['value'],'-5');self.assertEqual(br['interval_seconds'],3000)
 def test_changed_population_breaks_comparison_but_keeps_points(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);c=cockpit();capture(root,c,now=NOW,revalidate=lambda:c)
   c['positions'][0]['quantity']='2';at=NOW+dt.timedelta(minutes=10);capture(root,c,now=at,revalidate=lambda:c)
   r=read(root,at);self.assertFalse([s for s in r['changes'] if s['currency']=='BRL' and s['account_id'] is None]);self.assertEqual(len(r['intraday'][0]['points']),2)
 def test_single_observation_and_no_history_remain_honest(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.assertEqual(read(root,NOW)['diagnostic']['batch_count_48h'],0)
   c=cockpit();capture(root,c,now=NOW,revalidate=lambda:c);r=read(root,NOW)
   self.assertEqual(r['changes'],[]);self.assertEqual(r['diagnostic']['batch_count_48h'],1)
if __name__=='__main__':unittest.main()
