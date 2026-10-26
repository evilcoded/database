import ast,copy,datetime as dt,json,random,unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
import numpy as np
import test_a24_research_quote_acquisition as fixture
import test_global_dashboard_v118 as dashboard
from universal_portfolio import global_operational_metrics_a24 as metrics
from universal_portfolio import operational_score_a24 as shared
from universal_portfolio import global_action_readings_a24 as reader
from universal_portfolio.explicit_market_bindings_a24 import digest,canonical
NOW=fixture.NOW

class Provider:
    def __init__(self,now=NOW):self.now=now;self.calls=[];self.native_change=Decimal('-7');self.missing=None;self.fail_native=False
    def row(self,pid,q):
        return {'id':pid,'symbol':'test' if pid!='bitcoin' else 'btc','last_updated':self.now.isoformat(),
            'price_change_percentage_7d_in_currency':Decimal('1') if pid=='bitcoin' else self.native_change if q!='usd' else Decimal('9'),
            'price_change_percentage_30d_in_currency':Decimal('2'),'market_cap':Decimal('7000000000') if q!='usd' else Decimal('1000000000'),
            'total_volume':Decimal('700000000') if q!='usd' else Decimal('100000000'),'ath_change_percentage':Decimal('-20')}
    def get_json(self,path,params,timeout):
        self.calls.append((path,copy.deepcopy(params),timeout))
        if path=='/global':return {'data':{'market_cap_percentage':{'btc':Decimal('55')},'updated_at':int(self.now.timestamp())}}
        q=params['vs_currency']
        if self.fail_native and q!='usd':raise fixture.q.AcquisitionError('PROVIDER_HTTP_429')
        rows=[self.row(pid,q) for pid in params['ids'].split(',')]
        if self.missing and q!='usd':
            for r in rows:
                if r['id']=='source-id':r[self.missing]=None
        return rows

class MathParity(unittest.TestCase):
    def test_original_and_shared_math_are_identical_in_2000_baseline_and_model_cases(self):
        # Get the immutable prior producer from the published V128 installer payload,
        # avoiding an import that would read a user's configuration or models.
        # Only the original pure function is loaded, without project state.
        source=Path(__file__).with_name('original_score_fixture_v131.py').read_text()
        tree=ast.parse(source);scope={'np':np,'safe':shared.safe,'clamp':shared.clamp};exec(compile(tree,'original_score','exec'),scope)
        old=scope['score_asset'];rng=random.Random(131)
        for i in range(2000):
            row={'symbol':'TEST','price_change_percentage_7d_in_currency':rng.uniform(-80,200),'price_change_percentage_30d_in_currency':rng.uniform(-95,400),'market_cap':rng.uniform(1,100000000000),'total_volume':rng.uniform(0,1000000000),'ath_change_percentage':rng.uniform(-99,0)}
            regime=rng.uniform(0,100);btc={'ch7':rng.uniform(-40,40),'ch30':rng.uniform(-60,60)}
            model=None if i%2 else {'trained':True,'calibration_usable':True,'kpi_weights':[rng.random() for _ in range(5)]}
            before=copy.deepcopy((row,model));self.assertEqual(old(row,regime,btc,model),shared.score_asset(row,regime,btc,model));self.assertEqual(before,(row,model))
    def test_native_returns_and_reference_capitalization_have_explicit_separate_units(self):
        p=Provider();native=p.row('source-id','brl');reference=p.row('source-id','usd');benchmark=p.row('bitcoin','brl')
        actual=metrics.calculate(native,benchmark,reference,currency='BRL',reference_currency='USD',regime=48.5,now=NOW)
        numeric={k:float(v) if isinstance(v,Decimal) else v for k,v in native.items()}
        expected=shared.score_asset(numeric,48.5,{'ch7':1.,'ch30':2.},None,capitalization_reference=1e9)
        for k,v in expected.items():self.assertEqual(actual[k],v)
        self.assertEqual(actual['capitalization_reference_currency'],'USD');self.assertFalse(actual['fx_performed'])
        copied=shared.score_asset({k:float(v) if isinstance(v,Decimal) else v for k,v in reference.items()},48.5,{'ch7':1.,'ch30':2.})
        self.assertNotEqual(actual['entry'],copied['entry'])
        self.assertEqual(actual['liquidity'],shared.score_asset(numeric,48.5,{'ch7':1.,'ch30':2.})['liquidity'])

class Pipeline(unittest.TestCase):
    def setUp(self):
        self.f=fixture.Acquisition();self.f.setUp();self.addCleanup(self.f.doCleanups);self.root=self.f.root;self.f.save([self.f.rows()]);self.demand=self.f.demand();self.provider=Provider()
        (self.root/'results').mkdir();self.snapshot={'timestamp':NOW.isoformat(),'training':{'trained':False},'scores':[{'asset':'REF','provider':'CoinGecko','provider_id':'source-id','quote_currency':'USD','quote_currency_source':'EXPLICIT_PROVIDER_REQUEST','metric_contract':'porquinho.standard-action-metrics/1.0','action':'MANTENHA'}]}
        self.save_snapshot(self.snapshot)
        (self.root/'config.json').write_text(json.dumps({'action_rules':dashboard.CFG}))
        self.holdings=lambda root,now:{'jobs':[],'contexts':set()}
    def save_snapshot(self,snapshot):(self.root/'results/latest.json').write_text(json.dumps(snapshot))
    def collect(self,**kwargs):
        current={(c['account_id'],c['currency'],c['context_fingerprint']) for c in self.demand['contexts']}
        options={'now':NOW,'transport':self.provider,'holdings_loader':self.holdings,'revalidate':lambda:current};options.update(kwargs)
        return metrics.collect(self.root,self.demand,**options)
    def read(self,now=NOW):return metrics.read(self.root,now=now)
    def test_current_native_metric_reaches_real_position_rule_without_touching_original_snapshot(self):
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()};r=self.collect();self.assertEqual(r['metric_count'],1,r)
        data=self.read();self.assertEqual(data['status'],'CURRENT_NATIVE_OPERATIONAL_METRICS_INSPECTED',data)
        overlay=metrics.supplement(self.snapshot,data);position={'instrument_id':fixture.IID,'account_id':'account-BRL','currency':'BRL','reference_provider':'CoinGecko','reference_provider_id':'source-id','reference_pnl_pct':'-4','reference_quote_at':NOW.isoformat(),'context_status':'EXACT_REGISTERED_CONTEXT'}
        reading=reader.project({'positions':[position]},overlay,dashboard.CFG,now=NOW)['rows'][0]
        self.assertEqual(reading['status'],'CURRENT_RULE_READING_NOT_SIZED_RECOMMENDATION');self.assertIsNotNone(reading['action']);self.assertEqual(reading['capitalization_reference_currency'],'USD');self.assertFalse(reading['daily_confirmation_available'])
        for p,raw in before.items():self.assertEqual(p.read_bytes(),raw)
        self.assertEqual(overlay['scores'][0],self.snapshot['scores'][0]);self.assertEqual(len(overlay['scores']),2)
        self.assertTrue(all('api_key' not in str(call[1]) for call in self.provider.calls))
    def test_only_explicit_bound_contexts_and_benchmark_are_requested(self):
        r=self.collect();self.assertEqual(r['network_requests'],3)
        self.assertEqual({c[1].get('vs_currency') for c in self.provider.calls if c[0]=='/coins/markets'},{'usd','brl'})
        self.assertTrue(all(set(c[1]['ids'].split(','))=={'source-id','bitcoin'} for c in self.provider.calls if c[0]=='/coins/markets'))
    def test_missing_native_components_stay_missing(self):
        for name in metrics.FIELDS:
            self.provider.missing=name;r=self.collect();self.assertEqual(r['metric_count'],0,(name,r))
            self.assertEqual(self.read()['metrics'],[])
    def test_stale_capture_and_changed_snapshot_or_bindings_withdraw_metrics(self):
        self.collect();self.assertEqual(self.read(NOW+dt.timedelta(minutes=31))['metrics'],[])
        changed=copy.deepcopy(self.snapshot);changed['timestamp']=(NOW+dt.timedelta(seconds=1)).isoformat();self.save_snapshot(changed);self.assertEqual(self.read()['metrics'],[])
        self.save_snapshot(self.snapshot);self.f.save([self.f.rows(identity_source_ref='new')]);self.assertEqual(self.read()['metrics'],[])
    def test_native_failure_does_not_replace_original_signals(self):
        self.provider.fail_native=True;r=self.collect();self.assertEqual(r['metric_count'],0);self.assertIn('PROVIDER_HTTP_429',r['blocked_reason_counts'])
        self.assertEqual(metrics.supplement(self.snapshot,self.read()),self.snapshot)
    def test_unknown_reference_context_no_http_or_guess_currency(self):
        self.save_snapshot({'timestamp':NOW.isoformat(),'scores':[]});r=self.collect();self.assertEqual(r['network_requests'],0);self.assertFalse(self.provider.calls)
    def test_calibration_from_reference_currency_not_reused_for_native_currency(self):
        self.snapshot['training']={'trained':True,'calibration_usable':True,'kpi_weights':[1,0,0,0,0]};self.save_snapshot(self.snapshot);self.collect();row=self.read()['metrics'][0]
        self.assertFalse(row['calibration_applied']);self.assertFalse(row['cross_currency_calibration_reused']);self.assertEqual(row['metric_generation'],'SHARED_ORIGINAL_ENGINE_NATIVE_CURRENCY_BASELINE')
    def test_changed_funding_or_holding_state_before_write_refused(self):
        r=self.collect(revalidate=lambda:set());self.assertEqual(r['reason'],'METRIC_FUNDING_CONTEXT_CHANGED');self.assertFalse((self.root/metrics.LATEST).exists())
        answers=iter([{'jobs':[],'contexts':set()},{'jobs':[],'contexts':{'changed'}}]);r=self.collect(holdings_loader=lambda root,now:next(answers));self.assertEqual(r['reason'],'METRIC_HOLDING_CONTEXT_CHANGED')
    def test_no_reference_currency_reclassification_or_duplicate_override(self):
        self.f.save([self.f.rows(quote_currency='USD')]);self.demand=self.f.demand(('USD',));r=self.collect();self.assertEqual(r['network_requests'],0)
        supplemental={'status':'CURRENT_NATIVE_OPERATIONAL_METRICS_INSPECTED','metrics':[dict(self.snapshot['scores'][0],action='VENDA')]}
        self.assertEqual(metrics.supplement(self.snapshot,supplemental)['scores'],self.snapshot['scores'])
    def test_macro_cache_must_have_matching_context_and_be_current(self):
        cache=self.root/'cache/api';cache.mkdir(parents=True);(cache/'global.json').write_text(json.dumps({'saved_at':NOW.timestamp(),'request_params':{},'data':{'data':{'market_cap_percentage':{'btc':55}}}}))
        r=self.collect();self.assertEqual(r['network_requests'],2);self.assertFalse(any(c[0]=='/global' for c in self.provider.calls))
    def test_two_completed_scoped_days_needed_for_daily_sell_confirmation(self):
        self.f.save([self.f.rows(effective_from='2026-01-01',confirmed_at='2025-12-31T00:00:00Z')])
        self.provider.native_change=Decimal('-90')
        for day in (NOW-dt.timedelta(days=2),NOW-dt.timedelta(days=1),NOW):
            snapshot=copy.deepcopy(self.snapshot);snapshot['timestamp']=day.isoformat();self.save_snapshot(snapshot)
            provider=Provider(day);provider.native_change=Decimal('-90');self.collect(now=day,transport=provider)
        result=self.read();row=result['metrics'][0]
        self.assertEqual(row['daily_confirmation_status'],'TWO_COMPLETED_SCOPED_UTC_DAYS');self.assertEqual(row['daily_sell_confirmation'],True)
        self.assertEqual(row['daily_confirmation_dates'],[(NOW.date()-dt.timedelta(days=2)).isoformat(),(NOW.date()-dt.timedelta(days=1)).isoformat()])
    def test_valid_capture_reused_without_http_or_timestamp_rewrite(self):
        self.collect();before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()};calls=len(self.provider.calls)
        later=NOW+dt.timedelta(minutes=5);snapshot=copy.deepcopy(self.snapshot);snapshot['timestamp']=later.isoformat();self.save_snapshot(snapshot)
        r=self.collect(now=later);self.assertEqual(r['network_requests'],0);self.assertEqual(r['status'],'CURRENT_NATIVE_OPERATIONAL_METRICS_REUSED');self.assertEqual(len(self.provider.calls),calls)
        data=self.read(later);self.assertEqual(data['computed_at'],NOW.isoformat());self.assertEqual(data['metrics'][0]['quote_freshness'],'FRESH_CACHE');self.assertEqual(data['metrics'][0]['quote_observed_at'],NOW.isoformat())
        for p,raw in before.items():
            if p.name!='latest.json' or p.parent.name!='results':self.assertEqual(p.read_bytes(),raw)

    def test_missing_reference_capitalization_not_filled_from_native_amount(self):
        original=self.provider.get_json
        def get(path,params,timeout):
            rows=original(path,params,timeout)
            if path=='/coins/markets' and params['vs_currency']=='usd':
                for row in rows:
                    if row['id']=='source-id':row['market_cap']=None
            return rows
        self.provider.get_json=get;r=self.collect();self.assertEqual(r['metric_count'],0)
    def test_held_context_can_be_observed_without_new_investment_budget(self):
        demand={**self.demand,'contexts':[],'research_requests':[]}
        held={'jobs':[{'binding':self.f.rows(),'holding_contexts':['proof'],'funding_contexts':[]}],'contexts':{'proof'}}
        self.demand=demand;r=self.collect(holdings_loader=lambda root,now:held)
        self.assertEqual(r['metric_count'],1,r)
    def test_other_native_currency_uses_same_producer_without_currency_default(self):
        self.f.save([self.f.rows(quote_currency='JPY')]);self.demand=self.f.demand(('JPY',))
        r=self.collect();self.assertEqual(r['currencies'],['JPY']);self.assertEqual(self.read()['metrics'][0]['capitalization_reference_currency'],'USD')
    def test_stale_and_future_native_source_not_accepted(self):
        self.provider.now=NOW-dt.timedelta(minutes=31);self.assertEqual(self.collect()['metric_count'],0)
        self.provider.now=NOW+dt.timedelta(seconds=1);self.assertEqual(self.collect()['metric_count'],0)
    def test_duplicate_response_id_not_chosen(self):
        original=self.provider.get_json
        def get(path,params,timeout):
            result=original(path,params,timeout)
            return result+[copy.deepcopy(result[0])] if path=='/coins/markets' else result
        self.provider.get_json=get;self.assertEqual(self.collect()['metric_count'],0)
    def test_nonfinancial_unrelated_snapshot_nan_does_not_invalidate_scoring_context(self):
        self.snapshot['unrelated_research_value']=float('nan');self.save_snapshot(self.snapshot)
        self.assertEqual(self.collect()['metric_count'],1)
    def test_current_day_not_counted_as_completed_daily_confirmation(self):
        self.collect();self.collect();row=self.read()['metrics'][0]
        self.assertFalse(row['daily_sell_confirmation']);self.assertEqual(row['daily_confirmation_status'],'INSUFFICIENT_SCOPED_DAILY_HISTORY')
    def test_no_metrics_from_unbound_catalog_source(self):
        self.f.save([]);r=self.collect();self.assertEqual(r['network_requests'],0);self.assertEqual(r['metric_count'],0)

    def test_quote_field_values_not_mixed_with_other_currency_position(self):
        self.collect();row=self.read()['metrics'][0];pos={'instrument_id':fixture.IID,'account_id':'A','currency':'EUR','reference_provider':'CoinGecko','reference_provider_id':'source-id','reference_pnl_pct':'-18','context_status':'EXACT_REGISTERED_CONTEXT'}
        out=reader.project({'positions':[pos]},metrics.supplement({'scores':[]},self.read()),dashboard.CFG,now=NOW)['rows'][0];self.assertIsNone(out['action'])

if __name__=='__main__':unittest.main()
