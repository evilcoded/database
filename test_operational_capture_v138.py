import copy,datetime as dt,json,tempfile,unittest,ast
from pathlib import Path
from unittest.mock import patch
import test_operational_tracking_v137 as base
from universal_portfolio import operational_cycle_a24 as cycle
from universal_portfolio import operational_outcome_tracking_a24 as tracking

class Capture(base.Tracking):
    def test_changed_plan_prevents_capture(self):
        changed=copy.deepcopy(self.plan);changed['contexts'][0]['capital_reference']='99'
        result=tracking.run(self.root,self.plan,now=base.NOW,revalidate=lambda:changed)
        self.assertEqual(result['reason'],'OPERATIONAL_PLAN_CHANGED_BEFORE_CAPTURE');self.assertEqual(result['issues_created'],0)
    def test_display_universe_changes_do_not_invalidate_verified_decision_inputs(self):
        changed={**self.plan,'market_signals':[{'source_action':'ACOMPANHE'}]}
        result=tracking.run(self.root,self.plan,now=base.NOW,revalidate=lambda:changed)
        self.assertEqual(result['issues_created'],1,result)
    def test_missing_baseline_reports_pending_not_success(self):
        with patch.object(tracking.quotes,'valuation_records',return_value=[]):result=self.run_capture()
        self.assertEqual(result['status'],'OPERATIONAL_BASELINES_PENDING');self.assertEqual(result['skipped_reason_counts'],{'CURRENT_EXACT_BASELINE_REQUIRED':1});self.assertEqual(result['eligible_decision_count'],1)
    def test_duplicate_baseline_reports_ambiguity(self):
        prices=tracking.quotes.valuation_records(self.root,now=base.NOW)
        with patch.object(tracking.quotes,'valuation_records',return_value=prices*2):result=self.run_capture()
        self.assertEqual(result['skipped_reason_counts'],{'UNIQUE_CURRENT_BASELINE_REQUIRED':1})
    def test_stale_metrics_never_capture_using_fresh_quote(self):
        self.plan['contexts'][0]['rows'][0]['metric_at']=(base.NOW-dt.timedelta(hours=1)).isoformat()
        result=self.run_capture();self.assertEqual(result['issues_created'],0);self.assertEqual(result['skipped_reason_counts'],{'CURRENT_DECISION_METRICS_REQUIRED':1})
    def test_repeat_capture_explains_zero_new_daily_issues(self):
        self.run_capture();result=self.run_capture();self.assertEqual(result['already_recorded_count'],1);self.assertEqual(result['issues_created'],0)

class Cycle(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
    def test_refresh_orders_collectors_before_capture_and_persists_last_result(self):
        order=[]
        def record(name,value):
            def f(*a,**kw):order.append(name);return value
            return f
        with patch('universal_portfolio.universal_observation_bridge.observed_candidates',side_effect=record('discovery',(self.root,[]))),patch('universal_portfolio.funded_currency_research_a24.build',return_value={}),patch('universal_portfolio.research_quote_acquisition_a24.collect',side_effect=record('quotes',{'status':'OK','network_requests':2})),patch('universal_portfolio.global_operational_metrics_a24.collect',side_effect=record('metrics',{'status':'OK','network_requests':1})),patch.object(cycle,'run',side_effect=record('capture',{'status':'ORIGINAL_OPERATIONAL_CYCLE_EVALUATED','history_write_performed':True})):
            result=cycle.refresh(self.root,now=base.NOW)
        self.assertEqual(order,['discovery','quotes','metrics','capture']);self.assertEqual(cycle.last_result(self.root),result);self.assertEqual(result['network_requests'],3)
        self.assertTrue(result['history_write_performed']);self.assertFalse(result['financial_mutation'])
    def test_provider_failure_does_not_prevent_capture_or_other_collector(self):
        with patch('universal_portfolio.universal_observation_bridge.observed_candidates',return_value=(self.root,[])),patch('universal_portfolio.funded_currency_research_a24.build',return_value={}),patch('universal_portfolio.research_quote_acquisition_a24.collect',side_effect=RuntimeError('secret cannot leak')),patch('universal_portfolio.global_operational_metrics_a24.collect',return_value={'status':'OK'}) as metric,patch.object(cycle,'run',return_value={'status':'ORIGINAL_OPERATIONAL_CYCLE_EVALUATED'}) as capture:
            result=cycle.refresh(self.root,now=base.NOW)
        self.assertEqual(result['quote_acquisition']['reason'],'RuntimeError');self.assertNotIn('secret',json.dumps(result));metric.assert_called_once();capture.assert_called_once()
    def test_diagnostic_persistence_failure_does_not_change_decision_result(self):
        with patch('universal_portfolio.universal_observation_bridge.observed_candidates',side_effect=ValueError()),patch.object(cycle,'run',return_value={'status':'ORIGINAL_OPERATIONAL_CYCLE_EVALUATED'}),patch.object(cycle,'persist_result',side_effect=OSError()):
            result=cycle.refresh(self.root,now=base.NOW)
        self.assertEqual(result['status'],'ORIGINAL_OPERATIONAL_CYCLE_EVALUATED');self.assertEqual(result['diagnostic_persistence']['reason'],'OSError')
    def test_coverage_is_read_only_and_never_maps_legacy_score_to_common_rule(self):
        p=self.root/'data/equities/opportunity_latest.json';p.parent.mkdir(parents=True);p.write_text(json.dumps({'schema':'old-equity','assets':{'ABEV3':{'opportunity_score':.8}}}))
        before=p.read_bytes();result=cycle.input_coverage(self.root,{'contexts':[{'currency':'BRL','rows':[{'instrument_id':'ABEV3','provider':'brapi','provider_id':'ABEV3','plan_status':'CURRENT_EXACT_RULE_READING_REQUIRED'}]}]},now=base.NOW)
        self.assertEqual(result['pending_unique_count'],1);self.assertFalse(result['pending'][0]['legacy_equity_score_promoted']);self.assertFalse(result['new_scoring_formula_created']);self.assertEqual(p.read_bytes(),before)
        self.assertFalse(result['history_write_performed']);self.assertEqual(result['network_requests'],0)
    def test_missing_or_corrupt_diagnostic_does_not_look_like_capture(self):
        self.assertEqual(cycle.last_result(self.root)['status'],'OPERATIONAL_CYCLE_NOT_OBSERVED')
        p=self.root/cycle.RESULT_STORE;p.parent.mkdir(parents=True);p.write_text('{}')
        self.assertEqual(cycle.last_result(self.root)['status'],'OPERATIONAL_CYCLE_DIAGNOSTIC_UNAVAILABLE')
    def test_server_refresh_captures_before_economic_bridge_and_preserves_on_failure(self):
        tree=ast.parse(Path('/workspace/porquinho-a24/project/webapp/server.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_refresh')
        text=ast.unparse(node)
        self.assertLess(text.index('_a138_operational = refresh_original_operational_cycle(ROOT)'),text.index('_a24_input_bridge = build_read_only_bridge'))
        self.assertEqual(text.count('refresh_original_operational_cycle(ROOT)'),1)
        self.assertIn("'original_operational_cycle': _a138_operational",text)

if __name__=='__main__':unittest.main()
