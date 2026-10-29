"""Reproduce the confirmed one-asset plan; exercise durable scheduling and cache."""
import datetime as dt,json,unittest
from unittest.mock import patch
import test_brapi_native_references_v141 as fixture
from universal_portfolio import brapi_research_acquisition_a24 as brapi
from universal_portfolio import research_quote_acquisition_a24 as q
from universal_portfolio import global_radar_a24 as radar

class SingleAssetPlan(unittest.TestCase):
    def setUp(self):
        self.f=fixture.References();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.f.prepare(9);self.root=self.f.root;self.now=fixture.NOW;self.calls=[]
    def provider(self,at,*,stale=False,fail=None):
        def fetch(url,**kw):
            self.calls.append(url)
            pid=url.rsplit('/',1)[-1]
            if ',' in pid or ';' in pid:raise RuntimeError('PROVIDER_HTTP_400')
            if fail:raise RuntimeError(fail)
            stamp=at-dt.timedelta(hours=2) if stale else at
            return {'results':[{'symbol':pid,'currency':'BRL','regularMarketPrice':10,
                                'regularMarketTime':int(stamp.timestamp())}]}
        return fetch
    def collect(self,minute=0,**kwargs):
        at=self.now+dt.timedelta(minutes=minute)
        return self.f.collect(now=at,fetch=self.provider(at,**kwargs))
    def test_one_asset_plan_covers_nine_without_burst_or_starvation(self):
        total=0
        for minute in range(5):
            result=self.collect(minute);native=result['providers']['brapi']
            self.assertLessEqual(native['network_requests'],2)
            self.assertEqual(native['assets_per_request'],1)
            total+=native['current_references_refreshed']
            self.assertEqual(native['deferred_job_count'],max(0,9-2*(minute+1)))
        self.assertEqual(total,9);self.assertEqual(len(self.calls),9)
        self.assertEqual(len(q.valuation_records(self.root,now=self.now+dt.timedelta(minutes=5))),9)
        self.assertEqual(self.collect(5)['network_requests'],0)
    def test_stale_results_rotate_across_calls_and_are_not_current_cache(self):
        for minute in range(5):self.collect(minute,stale=True)
        self.assertEqual(len(set(self.calls)),9)
        self.assertEqual(q.valuation_records(self.root,now=self.now+dt.timedelta(minutes=5)),[])
        result=self.collect(5,stale=True)['providers']['brapi']
        self.assertEqual(result['network_requests'],0);self.assertEqual(result['cooldown_reference_count'],9)
        self.assertEqual(result['deferred_job_count'],9)
    def test_failures_are_deferred_without_selecting_same_two_on_every_cycle(self):
        for minute in range(5):self.collect(minute,fail='PROVIDER_HTTP_404')
        self.assertEqual(len(set(self.calls)),9)
        self.assertEqual(q.read_records(self.root),[])
    def test_persisted_attempts_survive_new_collector_invocation_and_expire(self):
        self.f.prepare(2);self.collect(stale=True)
        before=len(self.calls);self.collect(9,stale=True)
        self.assertEqual(len(self.calls),before)
        self.collect(10,stale=True);self.assertEqual(len(self.calls),before+2)
    def test_429_stops_and_defers_all_remaining_across_cycles(self):
        result=self.collect(fail='PROVIDER_HTTP_429')['providers']['brapi']
        self.assertEqual(len(self.calls),1);self.assertEqual(result['deferred_job_count'],8)
        result=self.collect(1)['providers']['brapi']
        self.assertEqual(result['status'],'PROVIDER_REQUEST_COOLDOWN');self.assertEqual(len(self.calls),1)
        result=self.collect(10)['providers']['brapi'];self.assertEqual(result['network_requests'],2)
    def test_auth_error_does_not_spend_next_request_or_leak_credentials(self):
        result=self.collect(fail='PROVIDER_HTTP_401')['providers']['brapi']
        self.assertEqual(result['network_requests'],1)
        self.assertEqual(self.collect(1)['network_requests'],0)
        raw=q.local(self.root,brapi.SCHEDULE_FILE).read_text()
        self.assertNotIn('Authorization',raw)
    def test_schedule_symlink_and_corruption_fail_before_network(self):
        self.collect(stale=True);path=q.local(self.root,brapi.SCHEDULE_FILE)
        path.write_text('{"schema":"OTHER"}');before=len(self.calls)
        result=self.collect(20)['providers']['brapi']
        self.assertEqual(result['reason'],'BRAPI_REQUEST_SCHEDULE_INVALID');self.assertEqual(len(self.calls),before)
        path.unlink();path.symlink_to(self.root/'elsewhere')
        self.collect(20);self.assertEqual(len(self.calls),before)
    def test_non_default_max_jobs_can_only_reduce_calls(self):
        result=self.f.collect(fetch=self.provider(self.now),max_jobs=1)
        self.assertEqual(result['network_requests'],1)
        self.assertEqual(result['providers']['brapi']['deferred_job_count'],8)
    def test_radar_reuses_exact_shared_cache_without_provider_request_or_writes(self):
        self.collect()
        rows=[{'instrument_id':b['instrument_id'],'symbol':b['provider_id'],'asset_class':'EQUITY',
               'market':'B3','jurisdiction':'BR','currency':'BRL'} for b in self.f.bindings]
        (self.root/'data/universal_instrument_catalog.json').write_text(json.dumps({'instruments':rows}))
        before={str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with patch('market_data.global_quote_transport_a24.get_json') as get:
            out=radar.snapshot(self.root,now=self.now)
        get.assert_not_called()
        self.assertEqual(sum(r['price'] is not None for r in out['assets']),2)
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def test_radar_injected_provider_receives_only_individual_identifiers(self):
        def fetch(provider,currency,ids):
            self.assertEqual(len(ids),1)
            return [{'provider_id':ids[0],'currency':currency,'price':10,'observed_at':self.now.isoformat()}]
        out=radar.snapshot(self.root,now=self.now,fetcher=fetch)
        self.assertEqual(sum(r['price'] is not None for r in out['assets']),9)

if __name__=='__main__':unittest.main()
