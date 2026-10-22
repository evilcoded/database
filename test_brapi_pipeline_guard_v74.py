import datetime as dt,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,Mock
from universal_portfolio import global_history_source_a24 as h
from universal_portfolio import research_quote_acquisition_a24 as q
from universal_portfolio import research_economic_series_a24 as series
class Tests(unittest.TestCase):
 def test_brapi_never_sent_to_coingecko_history(self):
  transport=Mock()
  with tempfile.TemporaryDirectory() as folder:
   fake={'jobs':[{'binding':{'provider':'brapi'}}],'blocked_reason_counts':{},'binding_digest':'x'}
   with patch.object(q,'plan',return_value=fake):
    result=h.collect(Path(folder),{},transport=transport)
   self.assertEqual(result['network_requests'],0);transport.get_json.assert_not_called()
   self.assertEqual(result['blocked_reason_counts'],{'HISTORICAL_PROVIDER_ADAPTER_NOT_IMPLEMENTED':1})
 def test_brapi_cannot_be_sealed_as_coingecko_bundle(self):
  with self.assertRaises(h.HistoryError):h.bundle({'provider':'brapi'},{},now=dt.datetime.now(dt.timezone.utc),binding_digest='x')
 def test_daily_brapi_observation_reaches_series(self):
  from tests.test_brapi_research_acquisition_v72 import Tests as Fixture
  f=Fixture();f.setUp()
  try:
   f.run_collect()
   rows=q.read_records(f.root)
   out=series.project(rows,now=dt.datetime.now(dt.timezone.utc))
   self.assertEqual(out['series'][0]['provider'],'brapi');self.assertEqual(out['series'][0]['quote_currency'],'BRL')
   self.assertEqual(out['series'][0]['observation_count'],1);self.assertEqual(out['series'][0]['realized_outcomes'],[])
  finally:f.doCleanups()
