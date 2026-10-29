import copy,datetime as dt,json,math,random,unittest
from unittest.mock import patch
import test_equity_analysis_pipeline_v139 as fixture
import test_operational_plan_v137 as operational
from universal_portfolio import common_action_metrics_a24 as common
from universal_portfolio import research_quote_acquisition_a24 as quotes
from universal_portfolio import brapi_research_acquisition_a24 as brapi
from universal_portfolio import global_history_source_a24 as history
from universal_portfolio import explicit_market_bindings_a24 as bindings
from universal_portfolio import global_action_readings_a24 as readings
from universal_portfolio import operational_outcome_tracking_a24 as tracking

NOW=fixture.NOW

def points(rate=.002,scale=1,days=100,weekdays=False):
    return [{'provider_observed_at':(NOW-dt.timedelta(days=days-i)).isoformat(),'price':str(scale*100*math.exp(rate*i))}
            for i in range(days) if not weekdays or (NOW-dt.timedelta(days=days-i)).weekday()<5]

class Formula(unittest.TestCase):
    def test_common_formula_is_scale_invariant_for_native_currencies(self):
        a=common.calculate(points(),100*math.exp(.2),at=NOW)
        for scale in (.001,5,1000000):
            b=common.calculate(points(scale=scale),scale*100*math.exp(.2),at=NOW)
            for k in (*common.METRICS,'opportunity','regime'):self.assertEqual(a[k],b[k],(scale,k))
    def test_identical_price_path_uses_no_source_or_asset_class_argument(self):
        result=common.calculate(points(),100*math.exp(.2),at=NOW)
        self.assertEqual(result['profile'],common.PROFILE)
        for k in ('btc_reference_used','capitalization_used','liquidity_estimated','probability_estimate'):self.assertFalse(result[k])
    def test_flat_prices_are_finite_and_do_not_force_buy(self):
        r=common.calculate(points(rate=0),100,at=NOW)
        self.assertEqual(r['risk'],25);self.assertEqual(r['entry'],72)
        self.assertEqual(r['observed_features']['annualized_calendar_volatility_pct'],0)
        self.assertEqual(r['observed_features']['positive_observation_fraction_pct'],50)
        self.assertLess(r['promising_pct'],75)
    def test_weekends_do_not_turn_calendar_horizons_into_session_counts(self):
        r=common.calculate(points(weekdays=True),100*math.exp(.2),at=NOW)
        self.assertEqual(r['horizon_unit'],'CALENDAR_DAYS')
        self.assertLess(r['observed_features']['window_point_count'],60)
        self.assertAlmostEqual(r['observed_features']['return_30_calendar_days_pct'],100*(math.exp(.06)-1))
    def test_missing_future_duplicate_and_large_gaps_do_not_become_zero_metrics(self):
        cases=[points(days=10),points()[:-20],points()+[points()[0]],points()+[{'provider_observed_at':NOW.isoformat(),'price':'100'}],points()[:10]+points()[50:]]
        for p in cases:
            with self.assertRaises(ValueError):common.calculate(p,100,at=NOW)
        for bad in (0,-1,True,float('nan'),float('inf')):
            with self.assertRaises(ValueError):common.calculate(points(),bad,at=NOW)
    def test_random_price_paths_stay_finite_and_bounded(self):
        rng=random.Random(143)
        for _ in range(300):
            p=points(rate=0);value=100
            for row in p:value*=math.exp(rng.uniform(-.08,.08));row['price']=str(value)
            r=common.calculate(p,value,at=NOW)
            self.assertTrue(all(0<=r[k]<=100 and math.isfinite(r[k]) for k in (*common.METRICS,'opportunity','regime')))
    def test_same_configured_rules_cover_buy_hold_sell_and_realize_without_provider_dispatch(self):
        scenarios=[(.002,False,0,False,'COMPRE'),(0,True,0,False,'MANTENHA'),(-.01,True,-18,True,'VENDA'),(-.01,True,10,False,'REALIZE')]
        for rate,held,pnl,confirmed,expected in scenarios:
            values=common.calculate(points(rate),100*math.exp(rate*100),at=NOW)
            for provider,currency in [('brapi','BRL'),('CoinGecko','BRL'),('CoinGecko','EUR')]:
                m={**values,'asset':'X','provider':provider,'provider_id':'id','currency':currency,'quote_currency':currency,
                   'quote_observed_at':NOW.isoformat(),'quote_freshness':'FRESH_CACHE','daily_sell_confirmation':confirmed,'daily_sell_confirmation_currency':currency}
                p={'instrument_id':'X','account_id':'A','currency':currency,'context_status':'EXACT_REGISTERED_CONTEXT',
                   'reference_provider':provider,'reference_provider_id':'id','reference_pnl_pct':str(pnl),'reference_quote_at':NOW.isoformat()}
                result=readings.project({'positions':[p]},{'scores':[m]},operational.CFG['action_rules'],now=NOW,invested=held)
                self.assertEqual(result['rows'][0]['action'],expected,(rate,provider,result))
    def test_no_legacy_score_fallback_when_common_inputs_are_missing(self):
        original={'scores':[{'asset':'BTC','promising_pct':99}]}
        self.assertEqual(common.apply(original,{'metrics':[]})['scores'],[])
        self.assertEqual(original['scores'][0]['promising_pct'],99)

class Sources(unittest.TestCase):
    def setUp(self):
        self.f=fixture.Pipeline();self.f.setUp();self.addCleanup(self.f.doCleanups);self.root=self.f.root
    def quote(self,price=110,now=NOW,b=None):
        b=b or self.f.b
        row,_=brapi.capture(b,{'symbol':b['provider_id'],'currency':b['quote_currency'],'regularMarketPrice':price,'regularMarketTime':int(now.timestamp())},
            fetched=now,binding_digest=bindings.digest(bindings.load(self.root)),response_digest='0'*64)
        quotes._write_latest_captures(self.root,[row]);return row
    def test_real_sealed_brapi_history_and_quote_produce_common_not_rescaled_equity_score(self):
        self.quote();result=common.build(self.root,now=NOW)
        self.assertEqual(result['metric_count'],1,result)
        row=result['metrics'][0]
        self.assertEqual(row['metric_generation'],common.PROFILE);self.assertEqual(row['currency'],'BRL')
        expected=common.calculate(self.f.bundle['observations'],110,at=NOW)
        for k in common.METRICS:self.assertEqual(row[k],expected[k])
        self.assertEqual(result['network_requests'],0)
    def test_real_coingecko_and_brapi_bindings_of_same_currency_share_exact_formula(self):
        self.quote();first=common.build(self.root,now=NOW)['metrics'][0]
        b={**self.f.b,'provider':'CoinGecko','provider_id':'test-coin','instrument_id':'GLOBAL:CRYPTO:CRYPTO:TEST'}
        self.f.write('data/universal_instrument_catalog.json',{'instruments':[self.f.identity,{'instrument_id':b['instrument_id'],'symbol':'TEST','asset_class':'CRYPTO','market':'CRYPTO','jurisdiction':'GLOBAL','currency':'BRL'}]})
        self.f.write(bindings.REGISTRY,{'schema':bindings.SCHEMA,'bindings':[self.f.b,b]})
        obs=self.f.bundle['observations'];response={'prices':[[int(common.instant(r['provider_observed_at']).timestamp()*1000),float(r['price'])] for r in obs]}
        body=history.bundle(b,response,now=NOW,binding_digest=bindings.digest(bindings.load(self.root)))
        history.store_once(history.path_for(self.root,{'binding':b},NOW),body)
        self.quote(b=b);self.quote()
        result=common.build(self.root,now=NOW);self.assertEqual(result['metric_count'],2,result)
        for k in common.METRICS:self.assertEqual(result['metrics'][0][k],result['metrics'][1][k])
    def test_read_only_build_does_not_modify_financial_models_or_inputs(self):
        self.quote();self.f.write('models/sentinel',{'weight':1});self.f.write('data/ledger.json',{'cash':500})
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        common.read_metrics(self.root,now=NOW,rules={'sell_max_promising':50})
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        out=common.collect(self.root,now=NOW);self.assertTrue(out['history_write_performed'])
        for p,value in before.items():self.assertEqual(p.read_bytes(),value)
        self.assertFalse(common.collect(self.root,now=NOW)['history_write_performed'])
    def test_old_quote_and_changed_binding_cannot_supply_current_indices(self):
        self.quote();self.assertEqual(common.build(self.root,now=NOW+dt.timedelta(hours=1))['metric_count'],0)
        self.f.write(bindings.REGISTRY,{'schema':bindings.SCHEMA,'bindings':[{**self.f.b,'identity_source_ref':'OTHER'}]})
        self.assertEqual(common.build(self.root,now=NOW)['metric_count'],0)
    def test_historical_bundles_do_not_create_past_daily_sell_confirmations(self):
        self.quote();common.collect(self.root,now=NOW)
        self.assertEqual(common.daily_confirmations(self.root,now=NOW,rules={'sell_max_promising':50}),{})
    def test_two_completed_days_use_only_prospective_common_captures(self):
        for offset in (2,1,0):
            at=NOW-dt.timedelta(days=offset)
            rows=[r for r in self.f.rows if r['date']<at.timestamp()]
            response={'results':[{'symbol':self.f.b['provider_id'],'currency':'BRL','historicalDataPrice':rows}]}
            if offset:
                body=history.bundle(self.f.b,response,now=at,binding_digest=bindings.digest(bindings.load(self.root)))
                history.store_once(history.path_for(self.root,{'binding':self.f.b},at),body)
            self.quote(now=at);common.collect(self.root,now=at)
        # High test threshold checks evidence plumbing, not production gates.
        yes=common.read_metrics(self.root,now=NOW,rules={'sell_max_promising':100})['metrics'][0]
        no=common.read_metrics(self.root,now=NOW,rules={'sell_max_promising':0})['metrics'][0]
        self.assertTrue(yes['daily_sell_confirmation']);self.assertFalse(no['daily_sell_confirmation'])
        self.assertEqual(yes['daily_confirmation_status'],'TWO_COMPLETED_SCOPED_UTC_DAYS')
    def test_actual_common_inputs_flow_to_funded_buy_plan_and_prospective_capture(self):
        from universal_portfolio import funded_currency_research_a24 as funding
        from universal_portfolio import global_operational_plan_a24 as plans
        from universal_portfolio import operational_cycle_a24 as cycle
        # Replace the synthetic source with a stronger, smooth observed path.
        for p in (self.root/history.STORE/'bundles').rglob('*.json'):p.unlink()
        rows=[]
        for i in range(100):
            price=100*math.exp(.002*i);stamp=int((NOW-dt.timedelta(days=100-i)).timestamp())
            rows.append({'date':stamp,'open':price,'high':price,'low':price,'close':price,'volume':1000})
        response={'results':[{'symbol':self.f.b['provider_id'],'currency':'BRL','historicalDataPrice':rows}]}
        body=history.bundle(self.f.b,response,now=NOW,binding_digest=bindings.digest(bindings.load(self.root)))
        history.store_once(history.path_for(self.root,{'binding':self.f.b},NOW),body)
        self.quote(price=100*math.exp(.2));self.f.write('config.json',operational.CFG)
        registry={'accounts':[{'account_id':'A','currency':'BRL','institution_id':'BANK'}],'institutions':[{'institution_id':'BANK','country':'BR'}]}
        self.f.write('data/institution_accounts.json',registry)
        demand=funding.project(cash=[{'account_id':'A','currency':'BRL','amount':'1000'}],registry=registry,candidates=[self.f.identity])
        cockpit={'execution_authorized':False,'financial_mutation':False,'positions':[],'cash':[operational.cash()]}
        plan=plans.from_root(self.root,demand,cockpit,now=NOW)
        row=plan['contexts'][0]['rows'][0]
        self.assertEqual(row['action'],'COMPRE',plan);self.assertEqual(row['metric_generation'],common.PROFILE)
        self.assertIsNotNone(row['reference_amount']);self.assertFalse(plan['execution_authorized'])
        captured=tracking.run(self.root,plan,now=NOW,revalidate=lambda:plans.from_root(self.root,demand,cockpit,now=NOW))
        self.assertEqual(captured['issues_created'],1,captured)
        self.assertEqual(tracking.issues(self.root,NOW)[0]['decision_profile'],common.PROFILE)
    def test_old_and_common_profile_issue_ids_are_distinct_without_rewriting_old_id(self):
        row=dict(day_utc='2026-10-29',account_id='A',currency='BRL',instrument_id='X',action='MANTENHA',rules_digest='R',sizing_digest='S')
        old=bindings.digest(row)
        self.assertEqual(tracking.issue_id(row),old)
        self.assertNotEqual(tracking.issue_id({**row,'decision_profile':common.PROFILE}),old)

if __name__=='__main__':unittest.main()
