"""Synthetic forecasts: arithmetic/scope tests, not real validation or trade evidence."""
import copy,datetime as dt,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from universal_portfolio import action_counterfactual_estimator_a24 as m
from universal_portfolio.action_research_handoff_a24 import project as handoff
from universal_portfolio.economic_action_plan_a24 import flags

NOW=dt.datetime(2026,10,24,12,tzinfo=dt.timezone.utc)
SRC='TEST:MKT:CRYPTO:SOURCE';DST='TEST:MKT:CRYPTO:DESTINATION'

def fixture(kind='REALLOCATE',q='BRL',h=30):
    action={'alternative_id':'TEST_ACTION','instrument_id':DST if kind=='REALLOCATE' else SRC,
      'source_instrument_id':SRC,'destination_instrument_id':DST if kind=='REALLOCATE' else None,
      'account_id':'TEST_ACCOUNT','currency':q,'horizon_unit':'OBSERVATIONS','horizon_value':h,
      'planning_context_fingerprint':'TEST_CONTEXT','kind':kind,'reference_capital':None}
    case={'case_id':'TEST_CASE','alternatives_mutually_exclusive':True,'alternatives':[action]}
    rows=[]
    for iid,value in ((SRC,.05),(DST,.12)):
        scope={**{k:action[k] for k in m.SCOPE},'instrument_id':iid}
        c={**scope,'value':value,'unit':'RETURN_FRACTION','authority':'NONE',
          'status':'EXPERIMENTAL_MODEL_OUTPUT','validation_status':'NOT_VALIDATED_FOR_COMPARATOR',
          'provenance':{'source_body_sha256':'a'*64,'experiment_sha256':('b' if iid==SRC else 'c')*64,
             'source_fetched_at':'2026-10-24T10:00:00+00:00','experiment_computed_at':'2026-10-24T10:01:00+00:00',
             'forecast_origin_observation_date':'2026-10-23','sampling':'SYNTHETIC_DAILY_OBSERVATIONS',
             'provider':'SYNTHETIC_PROVIDER','provider_id':iid,'identity_source_ref':'SYNTHETIC_BINDING'}}
        historical={**scope,'value':.90,'unit':'RETURN_FRACTION','authority':'NONE','validation_status':'NOT_VALIDATED_FOR_COMPARATOR','status':'REFERENCE_ONLY_NOT_ACTION_COUNTERFACTUAL'}
        rows.append({'instrument_id':iid,'account_id':action['account_id'],'quote_currency':q,
          'provider':'SYNTHETIC_PROVIDER','provider_id':iid,
          'context_fingerprint':action['planning_context_fingerprint'],'component_readings':{'forward_return':c,'counterfactual_return':historical}})
    research={'schema':'porquinho.research-economic-components-a24/1.0','status':'RESEARCH_COMPONENTS_INSPECTED',
      'model_validation_proven':False,'execution_authorized':False,'contexts':rows}
    return case,action,research

class Counterfactual(unittest.TestCase):
    def test_reallocation_uses_source_prediction_not_historical_mean(self):
        case,a,r=fixture();v=m.estimate(case,a,r,now=NOW)
        self.assertEqual(v['baseline_gross_return'],.05);self.assertAlmostEqual(v['gross_return_difference'],.07)
        self.assertEqual(v['counterfactual_component']['source_instrument_id'],SRC)
        self.assertEqual(v['counterfactual_component']['instrument_id'],DST)
        self.assertIsNone(v['net_advantage']);self.assertFalse(v['comparison_authorized'])
    def test_negative_difference_preserved_not_filtered(self):
        case,a,r=fixture();r['contexts'][1]['component_readings']['forward_return']['value']=-.10
        self.assertAlmostEqual(m.estimate(case,a,r,now=NOW)['gross_return_difference'],-.15)
    def test_keep_zero_difference_not_zero_risk(self):
        case,a,r=fixture('KEEP');v=m.estimate(case,a,r,now=NOW)
        self.assertEqual(v['gross_return_difference'],0);self.assertFalse(v['risk_or_utility_created'])
    def test_sell_reduce_do_not_invent_cash_returns_or_sizing(self):
        for kind in ('SELL','REDUCE'):
            case,a,r=fixture(kind);v=m.estimate(case,a,r,now=NOW)
            self.assertEqual(v['baseline_gross_return'],.05);self.assertIsNone(v['action_gross_return']);self.assertFalse(v['size_created'])
    def test_cash_returns_never_assumed_zero_including_increase(self):
        for kind in ('DEPLOY_CASH','INCREASE','NO_ALLOCATION'):
            case,a,r=fixture(kind);v=m.estimate(case,a,r,now=NOW)
            self.assertEqual(v['status'],'EXPLICIT_CASH_RETURN_MODEL_REQUIRED');self.assertIsNone(v['baseline_gross_return']);self.assertFalse(v['cash_yield_assumed_zero'])
    def test_brl_eur_same_estimator_no_conversion(self):
        for q in ('BRL','EUR'):
            case,a,r=fixture(q=q);v=m.estimate(case,a,r,now=NOW)
            self.assertEqual(v['currency'],q);self.assertAlmostEqual(v['gross_return_difference'],.07)
    def test_horizons_are_explicit_not_forced_to_thirty(self):
        for h in (30,60,90,120):
            case,a,r=fixture(h=h);self.assertEqual(m.estimate(case,a,r,now=NOW)['horizon_value'],h)
    def test_missing_source_not_resolved_by_symbol_or_alias(self):
        case,a,r=fixture();r['contexts'][0]['instrument_id']='OTHER_ID'
        self.assertIsNone(m.estimate(case,a,r,now=NOW)['counterfactual_component'])
    def test_account_currency_budget_context_never_crossed(self):
        for k in ('account_id','quote_currency','context_fingerprint'):
            case,a,r=fixture();r['contexts'][0][k]='OTHER'
            self.assertIsNone(m.estimate(case,a,r,now=NOW)['counterfactual_component'])
    def test_horizon_scope_mismatch_refused(self):
        case,a,r=fixture();r['contexts'][0]['component_readings']['forward_return']['horizon_value']=60
        self.assertIsNone(m.estimate(case,a,r,now=NOW)['counterfactual_component'])
    def test_duplicate_source_not_arbitrarily_selected(self):
        case,a,r=fixture();r['contexts'].append(copy.deepcopy(r['contexts'][0]))
        self.assertEqual(m.estimate(case,a,r,now=NOW)['status'],'AMBIGUOUS_KEEP_FORECAST_CONTEXT')
    def test_different_origin_or_sampling_no_difference(self):
        for k,value in [('forecast_origin_observation_date','2026-10-22'),('sampling','OTHER_SAMPLING')]:
            case,a,r=fixture();r['contexts'][1]['component_readings']['forward_return']['provenance'][k]=value
            v=m.estimate(case,a,r,now=NOW);self.assertEqual(v['baseline_gross_return'],.05);self.assertIsNone(v['gross_return_difference'])
    def test_future_and_stale_provenance_refused(self):
        for k,value in [('experiment_computed_at','2026-10-25T00:00:00Z'),('source_fetched_at','2026-10-25T00:00:00Z'),('forecast_origin_observation_date','2026-10-25'),('forecast_origin_observation_date','2026-10-01')]:
            case,a,r=fixture();r['contexts'][0]['component_readings']['forward_return']['provenance'][k]=value
            self.assertIsNone(m.estimate(case,a,r,now=NOW)['counterfactual_component'])
    def test_missing_provenance_and_bad_units_refused(self):
        for field,value in [('unit','PERCENT'),('value',True),('value',float('nan')),('authority','EXECUTION')]:
            case,a,r=fixture();r['contexts'][0]['component_readings']['forward_return'][field]=value
            self.assertIsNone(m.estimate(case,a,r,now=NOW)['counterfactual_component'])
    def test_model_output_cannot_predate_data_fetch(self):
        case,a,r=fixture();r['contexts'][0]['component_readings']['forward_return']['provenance']['experiment_computed_at']='2026-10-24T09:00:00Z'
        self.assertEqual(m.estimate(case,a,r,now=NOW)['status'],'KEEP_FORECAST_TIME_ORDER_MISMATCH')
    def test_invalid_action_geometry_refused(self):
        case,a,r=fixture();a['destination_instrument_id']=SRC
        self.assertIsNone(m.estimate(case,a,r,now=NOW)['counterfactual_component'])
    def test_provider_provenance_must_match_the_exact_source(self):
        case,a,r=fixture();r['contexts'][0]['component_readings']['forward_return']['provenance']['provider_id']='OTHER_SOURCE'
        self.assertEqual(m.estimate(case,a,r,now=NOW)['status'],'KEEP_FORECAST_PROVIDER_PROVENANCE_MISMATCH')
    def call_handoff(self,case,research):
        plan={'schema':'porquinho.economic-action-plan-a24/1.0','status':'ACTION_CONTEXTS_PROJECTED_NOT_COMPARATOR_READY',**flags(),'cases':[case]}
        estimate=m.estimate
        with patch.object(m,'estimate',side_effect=lambda *args,**kwargs:estimate(*args,now=NOW)):
            return handoff(plan,research)
    def test_handoff_preserves_original_packets_and_reference(self):
        case,a,r=fixture();before=copy.deepcopy((case,r));v=self.call_handoff(case,r)
        row=v['alternatives'][0]
        self.assertEqual(row['historical_counterfactual_reference']['value'],.90)
        self.assertEqual(row['research_readings']['counterfactual_return']['value'],.05)
        self.assertEqual(row['research_readings']['counterfactual_return']['validation_status'],'NOT_VALIDATED_FOR_COMPARATOR')
        self.assertEqual((case,r),before);self.assertFalse(row['comparator_ready'])
    def test_cash_historical_mean_not_left_as_cash_forecast(self):
        case,a,r=fixture('DEPLOY_CASH');v=self.call_handoff(case,r)['alternatives'][0]
        self.assertEqual(v['historical_counterfactual_reference']['value'],.90)
        self.assertIsNone(v['research_readings']['counterfactual_return']['value'])
    def test_known_keep_baseline_attached_when_destination_forecast_missing(self):
        case,a,r=fixture();r['contexts']=r['contexts'][:1];row=self.call_handoff(case,r)['alternatives'][0]
        self.assertEqual(row['research_readings']['counterfactual_return']['value'],.05)
        self.assertNotIn('forward_return',row['research_readings']);self.assertFalse(row['comparator_ready'])
    def test_existing_validated_action_component_not_overwritten(self):
        case,a,r=fixture();c=r['contexts'][1]['component_readings']['counterfactual_return']
        c.update(value=.03,validation_status='VALIDATED_FOR_SHADOW_COMPARATOR',source_ref='SYNTHETIC',model_ref='SYNTHETIC',model_version='SYNTHETIC',validation_ref='SYNTHETIC')
        c['action_context']={k:a.get(k) for k in ('alternative_id','kind','source_instrument_id','destination_instrument_id','reference_capital')};c['action_context']['case_id']=case['case_id']
        row=self.call_handoff(case,r)['alternatives'][0]
        self.assertEqual(row['research_readings']['counterfactual_return'],c)
        self.assertTrue(row['action_counterfactual_estimate']['existing_component_preserved'])
    def test_source_production_diagnostic_carries_estimates_without_promotion(self):
        from universal_portfolio.economic_source_producer_a24 import run
        case,a,r=fixture();h=self.call_handoff(case,r)
        plan={'schema':'porquinho.economic-action-plan-a24/1.0','status':'ACTION_CONTEXTS_PROJECTED_NOT_COMPARATOR_READY',**flags(),'cases':[case]}
        data={'economic_action_plan':plan,'action_research_handoff':h}
        with tempfile.TemporaryDirectory() as tmp:
            result=run(Path(tmp),data,revalidate=lambda:data)
            self.assertEqual(result['counterfactual_estimation']['keep_baseline_estimate_count'],1)
            self.assertFalse(result['source_written']);self.assertFalse(result['research_validation_granted'])

if __name__=='__main__':unittest.main()
