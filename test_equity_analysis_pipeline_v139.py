import copy,datetime as dt,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from universal_portfolio import equity_analysis_pipeline_a24 as pipeline
from universal_portfolio import global_history_source_a24 as history
from universal_portfolio import explicit_market_bindings_a24 as bindings
from equities.technical import compute as technical
from equities.risk_regime import compute as risk
from equities.opportunity import compute as opportunity
NOW=dt.datetime(2026,10,29,15,tzinfo=dt.timezone.utc)
IID='BR:B3:EQUITY:TEST3'

class Pipeline(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.b={'instrument_id':IID,'provider':'brapi','provider_id':'TEST3','quote_currency':'BRL','identity_source_ref':'explicit-test-route','confirmed_by':'user','confirmed_at':'2026-01-01T00:00:00+00:00','effective_from':'2026-01-01'}
        self.identity={'instrument_id':IID,'symbol':'TEST3','asset_class':'EQUITY','market':'B3','jurisdiction':'BR','currency':'BRL'}
        self.write('data/universal_instrument_catalog.json',{'instruments':[self.identity]})
        self.write(bindings.REGISTRY,{'schema':bindings.SCHEMA,'bindings':[self.b]})
        self.rows=[]
        for i in range(100):
            price=100+i*.1;stamp=int((NOW-dt.timedelta(days=101-i)).replace(hour=20).timestamp())
            self.rows.append({'date':stamp,'open':price,'high':price+2,'low':price-2,'close':price+1,'adjustedClose':price+1,'volume':1000+i})
        self.response={'results':[{'symbol':'TEST3','currency':'BRL','historicalDataPrice':self.rows}]}
        self.bundle=self.store(self.response)
    def write(self,rel,body):
        p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(body));return p
    def store(self,response,*,binding=None,now=NOW):
        b=binding or self.b;body=history.bundle(b,response,now=now,binding_digest=bindings.digest(bindings.load(self.root)))
        history.store_once(history.path_for(self.root,{'binding':b},now),body);return body
    def build(self,**kw):return pipeline.build(self.root,now=kw.get('now',NOW))
    def test_actual_existing_math_is_reused_without_converting_scores_to_global_action(self):
        result=self.build();self.assertEqual(result['analysis_count'],1,result);row=result['assets'][0]
        points=pipeline.ohlcv(self.bundle,NOW)
        t=technical('TEST3',points);r=risk('TEST3',points,[]);o=opportunity('TEST3',None,t,r)
        for x in (t,r,o):x['generated_at']=int(NOW.timestamp())
        self.assertEqual(row['technical'],t);self.assertEqual(row['risk_regime'],r);self.assertEqual(row['opportunity'],o)
        self.assertFalse(row['standardized_action_metrics_available']);self.assertIsNone(row['action']);self.assertEqual(result['standardized_action_metric_count'],0)
        self.assertFalse(result['shared_rule_thresholds_modified']);self.assertEqual(result['network_requests'],0)
    def test_collect_publishes_sealed_evidence_without_modifying_any_old_input_or_ledger(self):
        self.write('data/ledger.json',{'cash':500});self.write('models/sentinel.json',{'weights':[1,2]})
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        out=pipeline.collect(self.root,now=NOW);self.assertEqual(out['analysis_count'],1,out)
        for p,v in before.items():self.assertEqual(p.read_bytes(),v)
        result=pipeline.inspect(self.root,now=NOW);self.assertEqual(result['analysis_count'],1,result)
        out2=pipeline.collect(self.root,now=NOW);self.assertFalse(out2['history_write_performed'])
    def test_corrupt_optional_fundamentals_and_quotes_do_not_stop_technical_analysis(self):
        self.write('data/equities/fundamentals_latest.json',[])
        with patch.object(pipeline,'valuation_records',side_effect=ValueError('invalid quote store')):result=self.build()
        self.assertEqual(result['analysis_count'],1);self.assertEqual(result['reason_counts']['CURRENT_QUOTES_NOT_USABLE'],1)
        self.assertEqual(result['reason_counts']['FUNDAMENTALS_ARTIFACT_NOT_USABLE'],1)
    def test_calculation_failure_preserves_old_captures_without_promoting_failed_analysis(self):
        good=pipeline.collect(self.root,now=NOW);old=next((self.root/pipeline.STORE/'captures').rglob('*.json'));before=old.read_bytes()
        with patch('equities.technical.compute',return_value={'features':{'bad':float('nan')}}):result=pipeline.collect(self.root,now=NOW)
        self.assertEqual(result['analysis_count'],0);self.assertEqual(pipeline.inspect(self.root,now=NOW)['assets'][0]['reason'],'FINITE_DERIVED_ANALYSIS_REQUIRED')
        self.assertEqual(good['standardized_action_metric_count'],0);self.assertEqual(old.read_bytes(),before)
    def test_no_benchmark_is_silently_selected_or_fabricated(self):
        row=self.build()['assets'][0]
        self.assertEqual(row['relative_reference_status'],'EXPLICIT_QUALIFIED_BENCHMARK_REQUIRED')
        self.assertTrue(all(v['value'] is None for v in row['risk_regime']['relative'].values()))
        self.assertIn('relative_value',row['opportunity']['missing_components'])
    def test_undated_fundamentals_cannot_become_current_predictive_inputs(self):
        self.write('data/equities/fundamentals_latest.json',{'schema':'porquinho.equity-fundamental-snapshot/1.0','assets':[{'identity':self.identity,'metrics':{'returnOnEquity':{'value':999}}}]})
        row=self.build()['assets'][0];self.assertTrue(row['fundamental_evidence_available']);self.assertEqual(row['fundamental_currentness'],'UNDATED_LEGACY_EVIDENCE_NOT_USED');self.assertIn('fundamental',row['opportunity']['missing_components'])
    def test_currency_and_identity_are_not_guessed_from_ticker(self):
        self.identity['currency']='EUR';self.write('data/universal_instrument_catalog.json',{'instruments':[self.identity]})
        self.assertEqual(self.build()['assets'],[])
    def test_unbound_legacy_ohlcv_does_not_supply_native_currency_history(self):
        for p in (self.root/history.STORE/'bundles').rglob('*.json'):p.unlink()
        self.write('data/equities/historical/daily/ohlcv.json',{'series':{'TEST3':{'points':self.rows}}})
        result=self.build();self.assertEqual(result['analysis_count'],0);self.assertFalse(result['legacy_ticker_only_history_rebound'])
    def test_wrong_source_binding_does_not_supply_a_history(self):
        for p in (self.root/history.STORE/'bundles').rglob('*.json'):p.unlink()
        wrong={**self.b,'identity_source_ref':'OTHER'};self.store(self.response,binding=wrong)
        self.assertEqual(self.build()['analysis_count'],0)
    def test_raw_close_tampering_in_sealed_history_is_not_accepted(self):
        p=next((self.root/history.STORE/'bundles').rglob('*.json'));body=history.read_sealed(p);body['source_response']['results'][0]['historicalDataPrice'][0]['close']=999
        p.write_text(json.dumps({'body':body,'sha256':bindings.digest(body)}))
        self.assertEqual(self.build()['analysis_count'],0)
    def test_missing_ohlcv_does_not_get_filled_from_closes_or_zero(self):
        for p in (self.root/history.STORE/'bundles').rglob('*.json'):p.unlink()
        response=copy.deepcopy(self.response)
        for row in response['results'][0]['historicalDataPrice']:row.pop('open')
        self.store(response);result=self.build();self.assertEqual(result['analysis_count'],0);self.assertEqual(result['assets'][0]['reason'],'COMPLETE_UNAMBIGUOUS_OHLCV_REQUIRED')
    def test_incomplete_current_day_not_used_in_technical_history(self):
        body=copy.deepcopy(self.bundle);body['source_response']['results'][0]['historicalDataPrice'].append({'date':int(NOW.timestamp()),'close':500})
        self.assertEqual(len(pipeline.ohlcv(body,NOW)),100)
    def test_source_quote_absence_is_not_hidden_by_current_computation_time(self):
        row=self.build()['assets'][0];self.assertEqual(row['source_currentness'],'CURRENT_EXACT_QUOTE_REQUIRED');self.assertFalse(row['history_is_current_quote'])
    def test_input_binding_change_between_analysis_and_publishing_is_refused(self):
        real=pipeline.build
        def race(*a,**kw):
            result=real(*a,**kw);self.write(bindings.REGISTRY,{'schema':bindings.SCHEMA,'bindings':[]});return result
        with patch.object(pipeline,'build',side_effect=race):out=pipeline.collect(self.root,now=NOW)
        self.assertEqual(out['status'],'EQUITY_ANALYSIS_UNAVAILABLE');self.assertFalse((self.root/pipeline.STORE/'latest.json').exists())
    def test_old_or_changed_analysis_is_unavailable_not_current(self):
        pipeline.collect(self.root,now=NOW)
        self.assertEqual(pipeline.inspect(self.root,now=NOW+dt.timedelta(hours=1))['status'],'EQUITY_ANALYSIS_UNAVAILABLE')
        self.write(bindings.REGISTRY,{'schema':bindings.SCHEMA,'bindings':[]})
        self.assertEqual(pipeline.inspect(self.root,now=NOW)['reason'],'EQUITY_ANALYSIS_CONTEXT_CHANGED')
    def test_inspection_and_computation_have_no_provider_io(self):
        with patch('market_data.gateway.get_json',side_effect=AssertionError('No external request')),patch.dict('sys.modules',{'equities.benchmark':None}):
            pipeline.collect(self.root,now=NOW);self.assertEqual(pipeline.inspect(self.root,now=NOW)['analysis_count'],1)
    def test_bridge_consumes_exact_evidence_but_does_not_promote_it_to_decision(self):
        pipeline.collect(self.root,now=NOW)
        from universal_portfolio.universal_observation_bridge import _equity_specialized
        captured=pipeline.inspect(self.root,now=NOW)
        with patch('universal_portfolio.equity_analysis_pipeline_a24.inspect',return_value=captured):
            result=_equity_specialized(self.root,[self.identity])
        row=result[IID];self.assertFalse(row['evidence']['standardized_action_metrics_available']);self.assertTrue(row['provenance']['legacy_action_not_promoted']);self.assertEqual(row['evidence']['score_scale'],'SIGNED_EVIDENCE_MINUS_ONE_TO_ONE_NOT_PROBABILITY')

if __name__=='__main__':unittest.main()
