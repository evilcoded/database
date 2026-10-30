"""Synthetic integration checks; no real account/network/model operations."""
import copy,datetime as dt,unittest
from unittest.mock import patch
from pathlib import Path
from decimal import Decimal
import test_operational_plan_v137 as f
import test_a24_global_history_source as hf
from universal_portfolio import global_operational_plan_a24 as p,global_history_source_a24 as h
from universal_portfolio import common_action_metrics_a24 as common

class Decisions(f.Plans):
    def test_trace_preserves_real_buy_and_records_funded_amount(self):
        for q in ('BRL','EUR'):
            self.cockpit['cash']=[f.cash(q=q)];self.rows=[f.opportunity(q=q)]
            row=self.row();self.assertEqual(row['action'],'COMPRE');self.assertEqual(row['reference_amount'],'250.00')
            self.assertEqual(row['decision_path']['sizing_status'],'GROSS_REFERENCE_AVAILABLE')
            self.assertEqual(row['decision_path']['blocking_reasons'],[])
            self.assertTrue(row['decision_path']['rule_criteria'][0]['matched'])
            pipe=self.build()['contexts'][0]['decision_pipeline'];self.assertEqual((pipe['buy_signal_count'],pipe['funded_buy_count']), (1,1))
    def test_buy_signal_survives_missing_valuation_with_specific_reason(self):
        self.cockpit['positions']=[{'instrument_id':'OTHER','account_id':'A','currency':'BRL'}]
        row=self.row();self.assertEqual(row['action'],'COMPRE')
        self.assertEqual(row['decision_path']['blocking_reasons'],['COMPLETE_ACCOUNT_VALUATION_REQUIRED'])
        self.assertEqual(self.build()['contexts'][0]['decision_pipeline']['buy_sizing_pending_count'],1)
    def test_unknown_capital_zero_capital_and_missing_settings_are_distinct(self):
        self.cockpit['cash']=[]
        self.assertIn('CURRENT_CAPITAL_REFERENCE_REQUIRED',self.row()['decision_path']['blocking_reasons'])
        self.cockpit['cash']=[f.cash(value='0')]
        self.assertIn('POSITIVE_AVAILABLE_CAPITAL_REQUIRED',self.row()['decision_path']['blocking_reasons'])
        self.cfg.pop('position_sizing')
        self.assertIn('POSITION_SIZING_CONFIGURATION_REQUIRED',self.row()['decision_path']['blocking_reasons'])
    def test_threshold_failure_not_misrepresented_as_missing_data(self):
        self.rows=[f.opportunity(score=69)]
        r=self.row();self.assertEqual(r['action'],'ACOMPANHE');self.assertEqual(r['decision_path']['input_status'],'CURRENT_RULE_INPUTS_AVAILABLE')
        self.assertFalse(r['decision_path']['rule_criteria'][0]['matched'])
        self.assertEqual(r['decision_path']['blocking_reasons'],[])
    def test_missing_history_is_visible_in_context_coverage(self):
        self.rows=[{**f.opportunity(), 'action':None,'status':'STANDARDIZED_CURRENT_METRICS_REQUIRED','input_blockers':['EXACT_NATIVE_DAILY_HISTORY_REQUIRED']}]
        c=self.build()['contexts'][0];self.assertEqual(c['decision_pipeline']['input_pending_count'],1)
        self.assertEqual(c['decision_pipeline']['blocking_reason_counts'],{'EXACT_NATIVE_DAILY_HISTORY_REQUIRED':1})
    def test_sale_review_preserves_execution_convergence_reason(self):
        r=self.position(score=60,risk=35,pnl='10');self.assertEqual(r['action'],'REALIZE')
        self.assertEqual(r['decision_path']['blocking_reasons'],['ORIGINAL_EXECUTION_CONVERGENCE_REQUIRED'])
    def test_scoped_selection_limit_is_separate_from_entry_rule(self):
        self.cfg['max_positions']=1;self.rows=[f.opportunity('BEST',score=90),f.opportunity('SECOND',score=80)]
        rows=self.build()['contexts'][0]['rows'];self.assertEqual(rows[1]['action'],'COMPRE')
        self.assertIn('ORIGINAL_PORTFOLIO_SELECTION_OR_CAPACITY_LIMIT',rows[1]['decision_path']['blocking_reasons'])
    def test_metrics_apply_transports_pending_without_old_scores(self):
        pending=[{'instrument_id':'X','currency':'EUR','reason':'EXACT_NATIVE_DAILY_HISTORY_REQUIRED'}]
        s=common.apply({'scores':[{'asset':'OLD'}]},{'metrics':[],'pending':pending})
        self.assertEqual(s['scores'],[]);self.assertEqual(s['operational_input_pending'],pending)

class HistoryPriority(unittest.TestCase):
    def setUp(self):
        self.f=hf.History();self.f.setUp();self.addCleanup(self.f.doCleanups);self.root=self.f.root;self.now=hf.NOW
        a=self.f.f.rows();b={**a,'quote_currency':'EUR'}
        self.jobs=[{'binding':a,'funding_contexts':[]},{'binding':b,'funding_contexts':[]}]
    def bundle(self,j,age):
        at=self.now-dt.timedelta(days=age)
        response={'prices':[[int((at-dt.timedelta(days=k)).timestamp()*1000),100+k] for k in range(90,0,-1)]}
        body=h.bundle(j['binding'],response,now=at,binding_digest='synthetic')
        h.store_once(h.path_for(self.root,j,at),body)
    def plan(self):
        with patch.object(h.quotes,'plan',return_value={'jobs':copy.deepcopy(self.jobs),'blocked_reason_counts':{},'binding_digest':'synthetic'}):
            return h.plan(self.root,{},now=self.now)
    def test_missing_native_currency_history_goes_before_existing_history(self):
        self.bundle(self.jobs[0],1)
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        jobs=self.plan()['jobs'];self.assertEqual(jobs[0]['binding']['quote_currency'],'EUR')
        self.assertEqual(jobs[0]['history_priority'],'MISSING_HISTORY_FIRST')
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def test_oldest_source_observation_has_priority_after_initial_coverage(self):
        self.bundle(self.jobs[0],1);self.bundle(self.jobs[1],3)
        jobs=self.plan()['jobs'];self.assertEqual(jobs[0]['binding']['quote_currency'],'EUR')
        self.assertEqual(jobs[0]['history_priority'],'OLDEST_SOURCE_OBSERVATION_FIRST')
    def test_tampered_previous_bundle_cannot_drive_request_priority(self):
        self.bundle(self.jobs[0],1)
        path=h.path_for(self.root,self.jobs[0],self.now-dt.timedelta(days=1));path.write_text(path.read_text().replace('HISTORICAL_PROVIDER_RESPONSE_ACQUIRED_NOW','TAMPERED',1))
        with self.assertRaises(ValueError):self.plan()

if __name__=='__main__':unittest.main()
