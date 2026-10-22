import datetime as dt,unittest
from universal_portfolio.market_quote_context_a24 import inspect
NOW=dt.datetime(2026,10,22,12,tzinfo=dt.timezone.utc)
class Tests(unittest.TestCase):
 def test_old_unknown_is_not_assumed_closed(self):
  r=inspect({'regularMarketTime':'2026-10-22T04:42:09Z'},fetched=NOW)
  self.assertEqual(r['status'],'STALE_REFERENCE_SESSION_UNKNOWN');self.assertFalse(r['research_currentness_passed']);self.assertEqual(r['provider_reported_session'],'UNKNOWN')
 def test_open_stale(self):
  r=inspect({'regularMarketTime':'2026-10-22T04:42:09Z','marketState':'REGULAR'},fetched=NOW)
  self.assertEqual(r['status'],'STALE_DURING_PROVIDER_REPORTED_OPEN_SESSION')
 def test_closed_never_makes_old_price_current(self):
  r=inspect({'regularMarketTime':'2026-10-22T04:42:09Z','marketState':'CLOSED'},fetched=NOW)
  self.assertEqual(r['status'],'LAST_REFERENCE_OUTSIDE_PROVIDER_REPORTED_SESSION');self.assertFalse(r['research_currentness_passed'])
 def test_recent(self):
  r=inspect({'regularMarketTime':'2026-10-22T11:59:00Z'},fetched=NOW)
  self.assertTrue(r['research_currentness_passed']);self.assertEqual(r['age_seconds'],60)
 def test_invalid_and_future(self):
  for stamp in (None,'2026-10-22T13:00:00Z','2026-10-22T11:59:00'):
   self.assertFalse(inspect({'regularMarketTime':stamp},fetched=NOW)['research_currentness_passed'])
