"""Five-action closure controls plus sealed prospective evidence; no real funds."""
import copy,datetime as dt,unittest
from decimal import Decimal
from unittest.mock import patch
from universal_portfolio import consolidation_validation_a24 as control
from universal_portfolio import suggestion_consolidation_a24 as consolidated
from universal_portfolio import operational_outcome_tracking_a24 as tracking
import test_operational_tracking_v137 as old
import test_operational_plan_v137 as operational

class Contract(unittest.TestCase):
    def test_five_flows_for_both_native_currencies_and_providers(self):
        r=control.validate();self.assertEqual(len(r['scenarios']),3);self.assertFalse(r['uses_live_financial_data'])
    def setUp(self):self.cockpit,self.rows=control.scenario('BRL','brapi')
    def plan(self):return control.plan(self.cockpit,self.rows)
    def items(self):return self.plan()['consolidation']['contexts'][0]['suggestions']
    def test_missing_exit_quantity_does_not_create_reallocation_leg(self):
        next(p for p in self.cockpit['positions'] if p['instrument_id']=='CONTROL:EXIT').pop('quantity')
        items=self.items();sale=next(r for r in items if r['action']=='VENDA');self.assertEqual(sale['status'],'VALUE_PENDING')
        batch=next(r for r in items if r['action']=='REALLOCATE');self.assertEqual([m['instrument_id'] for m in batch['source_movements']],['CONTROL:PROFIT'])
    def test_no_complete_exit_means_no_reallocation(self):
        for p in self.cockpit['positions']:p.pop('quantity')
        self.assertFalse(any(r['action']=='REALLOCATE' for r in self.items()))
    def test_no_cash_preserves_entry_signal_without_spending_sale_proceeds(self):
        self.cockpit['cash'][0]['amount']='0';items=self.items()
        self.assertEqual(next(r for r in items if r['action']=='COMPRE')['status'],'VALUE_PENDING')
        self.assertFalse(any(r['action']=='REALLOCATE' for r in items))
    def test_expired_rows_never_reappear_as_consolidated_actions(self):
        for r in self.rows:r['metric_at']=(control.NOW-dt.timedelta(hours=1)).isoformat()
        items=self.items();self.assertTrue(all(r['action'] is None for r in items))
        self.assertTrue(all(r['rule_evaluation'] is None and r['reference_amount'] is None for r in items))
    def test_each_identity_is_scoped_by_account_and_currency(self):
        result=self.plan();first=result['consolidation']['contexts'][0]['suggestions'][0]['suggestion_id']
        for q,a in [('EUR','CONTROL_ACCOUNT'),('BRL','OTHER')]:
            p=copy.deepcopy(result);c=p['contexts'][0];c.update(account_id=a,currency=q)
            for r in c['rows']:r.update(account_id=a,currency=q)
            c['operational_reallocation_plan']=None
            r=consolidated.build(p,now=control.NOW)['contexts'][0]['suggestions'][0]
            self.assertNotEqual(first,r['suggestion_id'])
    def test_inconsistent_reallocation_child_amount_is_refused(self):
        p=self.plan();p['contexts'][0]['operational_reallocation_plan']['source_movements'][0]['reference_amount']='9999'
        result=consolidated.build(p,now=control.NOW)
        self.assertFalse(any(r['action']=='REALLOCATE' for r in result['contexts'][0]['suggestions']))
    def test_weak_thesis_sale_explains_actual_gate_not_structural_risk(self):
        p={'instrument_id':'WEAK','account_id':'A','currency':'EUR','context_status':'EXACT_REGISTERED_CONTEXT',
            'reference_provider':'CoinGecko','reference_provider_id':'weak','reference_quote_at':control.NOW.isoformat(),
            'reference_pnl_pct':'-19','reference_market_value':'81','quantity':'1'}
        m={'asset':'WEAK','provider':'CoinGecko','provider_id':'weak','quote_currency':'EUR','metric_unit':'INDEX_0_100',
            'metric_contract':'porquinho.standard-action-metrics/1.0','quote_observed_at':control.NOW.isoformat(),'quote_freshness':'FRESH_CACHE',
            'promising_pct':49,'entry':80,'risk':35,'asymmetry':60,'reversal_risk':30,
            'daily_sell_confirmation':True,'daily_sell_confirmation_currency':'EUR'}
        r=control.project({'positions':[p]},{'scores':[m]},control.RULES,now=control.NOW)['rows'][0]
        r.update(position_held=True,position_instrument_id='WEAK')
        cockpit={'execution_authorized':False,'financial_mutation':False,'positions':[p],'cash':[]}
        plan=control.plan(cockpit,[r]);r=plan['contexts'][0]['rows'][0]
        self.assertEqual(r['action'],'VENDA');self.assertEqual(r['operational_assessment']['decision_basis'],'SELL_WEAK_THESIS')
        self.assertEqual(r['reference_quantity'],'1');self.assertEqual(r['reference_amount'],'81')

class Evidence(old.Tracking):
    def test_legacy_daily_issue_gets_full_snapshot_without_rewriting_or_double_counting(self):
        self.run_capture();path=next((self.root/tracking.STORE/'issues').glob('*.json'))
        body=tracking.read_sealed(path)
        for k in ('capture_version','reference_quantity','rule_evaluation','operational_assessment','decision_path','capture_semantics','position_held','position_instrument_id'):body.pop(k,None)
        path.unlink();tracking.store_once(path,body)
        for p in (self.root/tracking.STORE/'snapshots').glob('*.json'):p.unlink()
        before=path.read_bytes();result=self.run_capture()
        self.assertEqual(result['issues_created'],0);self.assertEqual(result['decision_snapshots_created'],1)
        self.assertEqual(path.read_bytes(),before)
        summary=tracking.summary(self.root,now=old.NOW)
        self.assertEqual(summary['issue_count'],1);self.assertEqual(summary['decision_snapshot_count'],1)
    def test_snapshot_keeps_quantity_fraction_and_actual_rule_criteria(self):
        self.run_capture();i=tracking.issues(self.root,old.NOW)[0]
        self.assertEqual(i['capture_version'],2);self.assertIn('rule_evaluation',i)
        self.assertIn('reference_quantity',i);self.assertIn('operational_assessment',i)
        self.assertIn('NOT_A_TRADE',i['capture_semantics'])
    def batch_plan(self):
        p=copy.deepcopy(self.plan);c=p['contexts'][0];entry=c['rows'][0];entry['reference_amount']='25.00'
        exit=copy.deepcopy(entry);exit.update(instrument_id='CONTROL_EXIT',provider_id='exit-id',action='VENDA',position_held=True,
            reference_amount='100',reference_quantity='1')
        exit['operational_assessment'].update(execution_state='EXECUTE',execution_fraction_pct=100)
        c['rows'].append(exit)
        c['operational_reallocation_plan']={'source_movements':[{k:exit.get(k) for k in ('instrument_id','position_instrument_id','action','reference_amount','reference_quantity')}],
            'destination_movements':[{k:entry.get(k) for k in ('instrument_id','position_instrument_id','action','reference_amount','reference_quantity')}],
            'sale_proceeds_used_as_available_cash':False,'execution_authorized':False,'financial_mutation':False}
        p['consolidation']=consolidated.build(p,now=old.NOW)
        return p
    def test_reallocation_has_one_sealed_batch_with_complete_child_snapshots(self):
        p=self.batch_plan();base=tracking.quotes.valuation_records(self.root,now=old.NOW)[0]
        exit={**base,'instrument_id':'CONTROL_EXIT','provider_id':'exit-id'}
        with patch.object(tracking.quotes,'valuation_records',return_value=[base,exit]):
            first=self.run_capture(plan=p);second=self.run_capture(plan=p)
        self.assertEqual(first['reallocation_batches_created'],1,first);self.assertEqual(second['reallocation_batches_created'],0,second)
        path=next((self.root/tracking.STORE/'batches').glob('*.json'));body=tracking.read_sealed(path)
        self.assertEqual(len(body['child_snapshots']),2);self.assertEqual(body['action'],'REALLOCATE')
        self.assertFalse(body['suggestion']['net_advantage_validated']);self.assertFalse(body['financial_mutation'])
        summary=tracking.summary(self.root,now=old.NOW);self.assertEqual(summary['reallocation_batch_count'],1)
        self.assertEqual(summary['action_issue_counts'],{'COMPRE':1,'VENDA':1})
    def test_quote_with_different_time_cannot_become_decision_baseline(self):
        base=tracking.quotes.valuation_records(self.root,now=old.NOW)[0]
        base={**base,'provider_observed_at':(old.NOW-dt.timedelta(minutes=1)).isoformat()}
        with patch.object(tracking.quotes,'valuation_records',return_value=[base]):result=self.run_capture()
        self.assertEqual(result['issues_created'],0)
        self.assertEqual(result['skipped_reason_counts'],{'METRIC_AND_BASELINE_TIME_MISMATCH':1})
    def test_all_current_action_snapshots_and_batch_are_captured_without_financial_writes(self):
        with patch.object(control,'NOW',old.NOW):
            cockpit,rows=control.scenario('BRL','CoinGecko');plan=control.plan(cockpit,rows)
        base=tracking.quotes.valuation_records(self.root,now=old.NOW)[0]
        prices=[{**base,'instrument_id':r['instrument_id'],'provider_id':r['provider_id'],
            'identity_source_ref':r['identity_source_ref']} for r in rows]
        sentinel=self.root/'models/sentinel';sentinel.parent.mkdir();sentinel.write_text('UNCHANGED')
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with patch.object(tracking.quotes,'valuation_records',return_value=prices):result=self.run_capture(plan=plan)
        self.assertEqual(result['issues_created'],5,result);self.assertEqual(result['reallocation_batches_created'],1,result)
        issues=tracking.issues(self.root,old.NOW);by_action={i['action']:i for i in issues}
        self.assertEqual(set(by_action),{'COMPRE','VENDA','REALIZE','MANTENHA','ACOMPANHE'})
        self.assertEqual(Decimal(by_action['REALIZE']['reference_quantity']),Decimal('.5'))
        self.assertEqual(by_action['REALIZE']['operational_assessment']['execution_fraction_pct'],25)
        for p,value in before.items():self.assertEqual(p.read_bytes(),value)

if __name__=='__main__':unittest.main()
