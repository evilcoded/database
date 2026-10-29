import copy,datetime as dt,json,unittest
from decimal import Decimal
from unittest.mock import patch
import test_a24_research_quote_acquisition as fixture
from universal_portfolio import research_quote_acquisition_a24 as q
from universal_portfolio import brapi_research_acquisition_a24 as brapi
from universal_portfolio import explicit_market_bindings_a24 as bindings
from universal_portfolio.market_quote_context_a24 import inspect
from universal_portfolio.global_radar_a24 import date
NOW=fixture.NOW

class References(unittest.TestCase):
    def setUp(self):
        self.f=fixture.Acquisition();self.f.setUp();self.addCleanup(self.f.doCleanups);self.root=self.f.root
        self.prepare(9)
    def prepare(self,count):
        self.bindings=[self.f.rows(instrument_id='BR:B3:EQUITY:T'+str(i),provider='brapi',provider_id='T'+str(i)) for i in range(count)]
        (self.root/'data/universal_instrument_catalog.json').write_text(json.dumps({'instruments':[{'instrument_id':b['instrument_id']} for b in self.bindings]}));self.f.save(self.bindings)
        template=self.f.demand();request=template['research_requests'][0]
        template['research_requests']=[{**request,'instrument_id':b['instrument_id'],'candidate_asset_class':'EQUITY'} for b in self.bindings]
        self.demand=template;self.current={(c['account_id'],c['currency'],c['context_fingerprint']) for c in template['contexts']};self.calls=[]
    def fetch(self,*,now=NOW,price=100,mutate=None):
        def call(url,**kw):
            self.calls.append(url);ids=url.rsplit('/',1)[-1].split(';')
            rows=[{'symbol':pid,'currency':'BRL','regularMarketPrice':price,'regularMarketTime':int(now.timestamp())} for pid in ids]
            response={'results':rows};return mutate(response) if mutate else response
        return call
    def collect(self,*,now=NOW,fetch=None,revalidate=None,max_jobs=50):
        return q.collect(self.root,self.demand,now=now,transport=self.f.transport,brapi_transport=fetch or self.fetch(now=now),revalidate=revalidate or (lambda:self.current),max_jobs=max_jobs)
    def test_all_nine_current_references_are_refreshed_in_one_existing_batch_route(self):
        result=self.collect();self.assertEqual(result['observations_created'],9,result);self.assertEqual(result['current_references_refreshed'],9)
        self.assertEqual(len(self.calls),1);self.assertEqual(set(self.calls[0].rsplit('/',1)[-1].split(';')),{b['provider_id'] for b in self.bindings})
        self.assertEqual(len(q.valuation_records(self.root,now=NOW)),9);self.assertFalse(self.f.transport.calls)
    def test_intraday_updates_preserve_daily_training_bytes_but_replace_current_references(self):
        self.collect();path=q.storage_path(self.root,NOW.date());first=path.read_bytes()
        for minutes in (10,20,40,60):
            now=NOW+dt.timedelta(minutes=minutes);result=self.collect(now=now,fetch=self.fetch(now=now,price=100+minutes))
            self.assertEqual(result['observations_created'],0);self.assertEqual(result['current_references_refreshed'],9,result);self.assertEqual(path.read_bytes(),first)
            rows=q.valuation_records(self.root,now=now);self.assertEqual(len(rows),9);self.assertEqual({r['price'] for r in rows},{str(100+minutes)})
        self.assertEqual(len(q.read_records(self.root)),9)
    def test_within_ten_minutes_cache_avoids_provider_call(self):
        self.collect();before=len(self.calls);result=self.collect(now=NOW+dt.timedelta(minutes=9))
        self.assertEqual(len(self.calls),before);self.assertEqual(result['providers']['brapi']['cached_reference_count'],9)
    def test_partial_invalid_and_stale_rows_do_not_discard_other_exact_native_quotes(self):
        def mutate(body):
            body['results'][0]['regularMarketTime']=int((NOW-dt.timedelta(hours=2)).timestamp())
            body['results'][1]['currency']='EUR';body['results'][2]['regularMarketPrice']=True
            body['results'].append(copy.deepcopy(body['results'][3]));return body
        result=self.collect(fetch=self.fetch(mutate=mutate));self.assertEqual(result['current_references_refreshed'],5,result)
        self.assertEqual(len(q.valuation_records(self.root,now=NOW)),5);self.assertEqual(result['providers']['brapi']['blocked_reason_counts']['BRAPI_QUOTE_CURRENCY_MISMATCH'],1)
    def test_stale_observation_never_becomes_current_by_batch_capture_time(self):
        result=self.collect(fetch=self.fetch(now=NOW-dt.timedelta(hours=1)))
        self.assertEqual(result['current_references_refreshed'],0);self.assertEqual(result['providers']['brapi']['status'],'SOURCE_OBSERVATION_NOT_CURRENT');self.assertEqual(q.valuation_records(self.root,now=NOW),[])
    def test_pre_request_context_change_prevents_network(self):
        self.collect(revalidate=lambda:set());self.assertFalse(self.calls)
    def test_binding_change_during_response_prevents_any_publication(self):
        def mutate(body):self.f.save([{**b,'identity_source_ref':'CHANGED'} for b in self.bindings]);return body
        result=self.collect(fetch=self.fetch(mutate=mutate));self.assertEqual(result['current_references_refreshed'],0);self.assertEqual(q.read_records(self.root),[])
    def test_funding_change_after_response_prevents_any_publication(self):
        valid=[True]
        def mutate(body):valid[0]=False;return body
        result=self.collect(fetch=self.fetch(mutate=mutate),revalidate=lambda:self.current if valid[0] else set())
        self.assertEqual(result['current_references_refreshed'],0);self.assertEqual(q.read_records(self.root),[])
    def test_429_is_not_retried_and_counts_unattempted_batch_as_deferred(self):
        self.prepare(45)
        def fail(url,**kw):self.calls.append(url);raise RuntimeError('PROVIDER_HTTP_429')
        result=self.collect(fetch=fail);out=result['providers']['brapi'];self.assertEqual(len(self.calls),1);self.assertEqual(out['status'],'RATE_LIMITED');self.assertEqual(out['deferred_job_count'],25)
    def test_population_larger_than_budget_is_bounded_and_rotates_without_ranking(self):
        self.prepare(45);r=self.collect();out=r['providers']['brapi'];self.assertEqual(out['network_requests'],2);self.assertEqual(out['current_references_refreshed'],40);self.assertEqual(out['deferred_job_count'],5)
        now=NOW+dt.timedelta(minutes=1);r=self.collect(now=now,fetch=self.fetch(now=now));self.assertEqual(r['current_references_refreshed'],5);self.assertEqual(len(q.valuation_records(self.root,now=now)),45)
    def test_provider_secrets_do_not_appear_in_diagnostics(self):
        def fail(*a,**kw):raise RuntimeError('PRIVATE_PROVIDER_TOKEN')
        self.assertNotIn('PRIVATE_PROVIDER_TOKEN',json.dumps(self.collect(fetch=fail)))
        def disguised(*a,**kw):raise RuntimeError('PROVIDER_PRIVATE_TOKEN')
        self.assertNotIn('PROVIDER_PRIVATE_TOKEN',json.dumps(self.collect(fetch=disguised)))
    def test_coingecko_failure_does_not_gate_exact_brapi_source_refresh(self):
        failed={'status':'ACQUISITION_FAILED_CLOSED','observations_created':0,'network_requests':0}
        with patch.object(q,'_collect_coingecko',return_value=failed):result=self.collect()
        self.assertEqual(result['current_references_refreshed'],9);self.assertEqual(result['status'],'PARTIAL_PROVIDER_REFERENCES_REFRESHED');self.assertEqual(result['providers']['coingecko']['status'],'ACQUISITION_FAILED_CLOSED')
    def test_real_verified_ledger_holding_is_refreshed_without_crypto_routing_or_daily_training(self):
        from universal_portfolio.ledger import TransactionLedger
        ledger=TransactionLedger(self.root/'data/transaction_ledger.jsonl');iid=self.bindings[0]['instrument_id']
        ledger.append(dict(event_type='BUY',asset_id=iid,account_id='account-BRL',currency='BRL',quantity='2',unit_price='100',gross_amount='200',executed_at=(NOW-dt.timedelta(minutes=5)).isoformat()))
        registry={'accounts':[{'account_id':'account-BRL','institution_id':'bank','currency':'BRL'}],'institutions':[{'institution_id':'bank','country':'BR'}]}
        (self.root/'data/institution_accounts.json').write_text(json.dumps(registry))
        runtime=dict(authority='NONE',ledger_write=False,ledger_verified=ledger.verify(),cutover_effective_from=(NOW-dt.timedelta(days=1)).isoformat(),positions=[dict(account_reference='account-BRL',account_status='EXPLICIT_TRANSACTION_ACCOUNT',instrument_id=iid,currency='BRL',quantity='2',cost_basis='200')])
        self.demand['research_requests']=[];before=ledger.path.read_bytes()
        with patch('universal_portfolio.canonical_runtime_read_model.build',return_value=runtime):result=self.collect()
        self.assertEqual(result['current_references_refreshed'],1,result);self.assertFalse(self.f.transport.calls);self.assertEqual(result['observations_created'],0);self.assertEqual(q.read_records(self.root),[]);self.assertEqual(ledger.path.read_bytes(),before)
    def test_held_only_reference_does_not_create_daily_research_observations(self):
        prepared=q.plan(self.root,self.demand,now=NOW,include_observed=True);job=copy.deepcopy(prepared['jobs'][0]);job.update(funding_contexts=[],holding_contexts=['verified-holding'],daily_research_observation_eligible=False)
        with patch.object(q,'held_reference_jobs',return_value={'contexts':{'verified-holding'}}):
            result=brapi.collect(self.root,prepared,[job],now=NOW,transport=self.fetch(),revalidate=lambda:set())
        self.assertEqual(result['observations_created'],0);self.assertEqual(result['current_references_refreshed'],1);self.assertEqual(q.read_records(self.root),[])
    def test_changed_holding_proof_prevents_request(self):
        prepared=q.plan(self.root,self.demand,now=NOW,include_observed=True);job=copy.deepcopy(prepared['jobs'][0]);job.update(funding_contexts=[],holding_contexts=['old-proof'],daily_research_observation_eligible=False)
        with patch.object(q,'held_reference_jobs',return_value={'contexts':set()}):
            result=brapi.collect(self.root,prepared,[job],now=NOW,transport=self.fetch(),revalidate=lambda:set())
        self.assertEqual(result['current_references_refreshed'],0);self.assertFalse(self.calls)

class ProviderTimes(unittest.TestCase):
    def test_epoch_seconds_and_iso_are_identical_without_guessing_timezone(self):
        self.assertEqual(date(int(NOW.timestamp())),NOW);self.assertEqual(date(NOW.isoformat()),NOW)
        context=inspect({'regularMarketTime':int(NOW.timestamp())},fetched=NOW);self.assertTrue(context['research_currentness_passed']);self.assertEqual(context['provider_reported_session'],'UNKNOWN')
    def test_invalid_future_milliseconds_and_naive_times_are_not_accepted_as_current(self):
        for value in (True,False,None,float('inf'),float('nan'),int(NOW.timestamp()*1000),'2026-10-16T12:00:00'):
            self.assertIsNone(date(value),value)
        self.assertFalse(inspect({'regularMarketTime':int((NOW+dt.timedelta(minutes=2)).timestamp())},fetched=NOW)['research_currentness_passed'])

if __name__=='__main__':unittest.main()
