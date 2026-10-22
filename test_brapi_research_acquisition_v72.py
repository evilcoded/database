import datetime as dt,unittest
from tests import test_a24_research_quote_acquisition as fixture
from universal_portfolio import research_quote_acquisition_a24 as q

class Tests(unittest.TestCase):
 setUp=fixture.Acquisition.setUp
 rows=fixture.Acquisition.rows
 save=fixture.Acquisition.save
 demand=fixture.Acquisition.demand
 def response(self,**kw):return {'results':[{'symbol':'NEW3','currency':'BRL','regularMarketPrice':12,'regularMarketTime':fixture.NOW.isoformat(),**kw}]}
 def run_collect(self,fetch=None,revalidate=None):
  self.save([self.rows(provider='brapi',provider_id='NEW3')]);d=self.demand()
  current={(c['account_id'],c['currency'],c['context_fingerprint']) for c in d['contexts']}
  return q.collect(self.root,d,now=fixture.NOW,transport=self.transport,brapi_transport=fetch or (lambda *a,**kw:self.response()),revalidate=revalidate or (lambda:current))
 def test_records_in_existing_journal_without_cg_network(self):
  r=self.run_collect();self.assertEqual(r['observations_created'],1);self.assertEqual(r['network_requests'],1);self.assertFalse(self.transport.calls)
  rows=q.read_records(self.root);self.assertEqual(rows[0]['provider'],'brapi');self.assertEqual(rows[0]['quote_currency'],'BRL');self.assertIsNone(rows[0]['volume_24h']);self.assertFalse(rows[0]['execution_authorized'])
 def test_stale_price_rejected(self):
  r=self.run_collect(fetch=lambda *a,**kw:self.response(regularMarketTime=(fixture.NOW-dt.timedelta(hours=1)).isoformat()))
  self.assertEqual(r['observations_created'],0);self.assertEqual(r['providers']['brapi']['status'],'SOURCE_OBSERVATION_NOT_CURRENT')
 def test_wrong_currency(self):
  self.assertEqual(self.run_collect(fetch=lambda *a,**kw:self.response(currency='EUR'))['observations_created'],0)
 def test_duplicate_id_response_rejected(self):
  self.assertEqual(self.run_collect(fetch=lambda *a,**kw:{'results':self.response()['results']*2})['observations_created'],0)
 def test_429_only_one_request_no_retry(self):
  calls=[]
  def fetch(*a,**kw):calls.append(a);raise RuntimeError('PROVIDER_HTTP_429')
  r=self.run_collect(fetch=fetch);self.assertEqual(len(calls),1);self.assertEqual(r['providers']['brapi']['status'],'RATE_LIMITED')
 def test_changed_funding_prevents_request(self):
  calls=[]
  r=self.run_collect(fetch=lambda *a,**kw:calls.append(a),revalidate=lambda:set())
  self.assertFalse(calls);self.assertEqual(r['observations_created'],0)
 def test_daily_dedup_no_second_request(self):
  self.run_collect();calls=[]
  r=self.run_collect(fetch=lambda *a,**kw:calls.append(a));self.assertEqual(r['network_requests'],0);self.assertFalse(calls)
 def test_secret_not_in_report(self):
  def fetch(*a,**kw):raise RuntimeError('PRIVATE_TOKEN')
  self.assertNotIn('PRIVATE_TOKEN',str(self.run_collect(fetch=fetch)))
