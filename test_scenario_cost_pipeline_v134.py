import copy,datetime as dt,unittest
from decimal import Decimal
from unittest.mock import patch
import test_scenario_reviewed_cost_v125 as fixture
from universal_portfolio import scenario_reviewed_cost_a24 as reviewed
from universal_portfolio import scenario_cost_pipeline_a24 as pipeline
from universal_portfolio import account_cost_evidence_a24 as costs

NOW=fixture.NOW

class Pipeline(unittest.TestCase):
    def setUp(self):
        self.f=fixture.Scenario();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.scenario=self.f.scenario;self.scenario['common_research_unit']['expected_return_pct']='10'
        self.view,self.assessments=self.f.views()
    def attach(self,rows=None,*,now=NOW,document=None,cash_models=()):
        p=self.f.project(rows,now=now)
        document=document if document is not None else {'status':'SCENARIO_REVIEWED_COSTS_INSPECTED','scenarios':[p],'cost_source_digest':'source','account_context_digest':'registry'}
        summary=pipeline.attach(self.view,self.assessments,document,now=now,cash_models=cash_models)
        return summary,self.scenario['execution_cost_projection'],self.scenario['reviewed_pretrade_cost_projection']
    def test_latest_review_drives_existing_conditional_arithmetic(self):
        summary,value,p=self.attach();self.assertEqual(len(value['variants']),1,value)
        self.assertEqual(value['variants'][0]['reviewed_execution_cost'],'0.60');self.assertEqual(value['variants'][0]['research_change_less_execution_costs'],'9.40')
        self.assertEqual(value['cost_source_digest'],'source');self.assertEqual(summary['conditional_cost_variant_count'],1);self.assertFalse(value['legacy_cost_context_used'])
        self.assertFalse(value['variants'][0]['account_net_return_validated']);self.assertIsNone(value['net_advantage_vs_preserving_cash'])
    def test_two_venues_remain_separate_variants_without_winner(self):
        second=copy.deepcopy(self.f.row);second.update(evidence_id='other',execution_venue_id='other-venue')
        second['components']['brokerage']['amount']='1.10'
        summary,value,p=self.attach([self.f.row,second]);self.assertEqual(p['legs'][0]['status'],'MULTIPLE_REVIEWED_EXECUTION_VENUES_NO_SELECTION');self.assertFalse(p['cost_arithmetic_available'])
        self.assertEqual({v['reviewed_execution_cost'] for v in value['variants']},{'0.60','1.60'});self.assertEqual(summary['conditional_cost_variant_count'],2)
        self.assertTrue(all(v['execution_venue_selected'] is False for v in value['variants']))
    def test_multileg_venue_combinations_are_alternatives_not_summed_together(self):
        self.scenario['legs'][0]['fraction_denominator']=2
        self.scenario['legs'].append({**self.scenario['legs'][0],'instrument_id':'SECOND'})
        rows=[]
        for iid in (self.f.row['instrument_id'],'SECOND'):
            for venue,amount in [('route-1','0.10'),('route-2','1.10')]:
                row=copy.deepcopy(self.f.row);row.update(instrument_id=iid,execution_venue_id=venue,evidence_id=iid+venue,reference_amount='50')
                row['components']['brokerage']['amount']=amount;rows.append(row)
        summary,value,_=self.attach(rows);self.assertEqual(summary['conditional_cost_variant_count'],4)
        self.assertEqual(sorted(Decimal(v['reviewed_execution_cost']) for v in value['variants']),[Decimal('1.20'),Decimal('2.20'),Decimal('2.20'),Decimal('3.20')])
        self.assertTrue(all(len(v['cost_references'])==2 for v in value['variants']))
    def test_partial_components_have_known_subtotal_but_no_total_or_variant(self):
        self.f.row['components']['spread'].update(status='UNKNOWN',amount=None)
        summary,value,p=self.attach();source=p['legs'][0]['reviewed_candidates'][0]['source']
        self.assertEqual(source['known_component_subtotal'],'0.50');self.assertFalse(source['subtotal_is_total_cost']);self.assertIsNone(p['purchase_execution_cost_estimate']);self.assertEqual(value['variants'],[])
    def test_explicit_zero_stays_known_zero(self):
        for component in self.f.row['components'].values():component['amount']='0'
        _,value,p=self.attach();self.assertEqual(value['variants'][0]['reviewed_execution_cost'],'0');self.assertTrue(p['legs'][0]['reviewed_candidates'][0]['source']['subtotal_is_total_cost'])
    def test_absence_or_expiry_does_not_reuse_learned_cost_context(self):
        self.scenario['reviewed_cost_context']={'status':'CANDIDATE_COST_CONTEXTS_LINKED_RESEARCH_ONLY','execution_authorized':False,'legs':[{'invented':'old'}]}
        for rows,now in [([],NOW),([self.f.row],NOW+dt.timedelta(hours=2))]:
            _,value,p=self.attach(rows,now=now);self.assertEqual(value['variants'],[]);self.assertFalse(value['legacy_cost_context_used'])
    def test_same_venue_conflicting_reviews_not_selected(self):
        second=copy.deepcopy(self.f.row);second['evidence_id']='other'
        _,value,p=self.attach([self.f.row,second]);self.assertEqual(value['variants'],[]);self.assertIsNone(p['legs'][0]['reviewed_candidates'][0]['source'])
    def test_changed_scenario_digest_withdraws_results(self):
        p=self.f.project();self.scenario['candidate_id']='changed'
        _,value,_=self.attach(document={'status':'SCENARIO_REVIEWED_COSTS_INSPECTED','scenarios':[p]});self.assertEqual(value['variants'],[])
    def test_wrong_account_currency_side_notional_and_amount_never_reused(self):
        for key,value in [('account_id','other'),('currency','EUR'),('side','SELL'),('reference_amount','101'),('instrument_id','other')]:
            row=copy.deepcopy(self.f.row);row[key]=value
            _,result,_=self.attach([row]);self.assertEqual(result['variants'],[],(key,value))
    def test_no_purchase_does_not_invent_holding_cost_model(self):
        self.scenario['legs']=[];self.scenario['cash_fraction_numerator']=1
        _,value,p=self.attach();self.assertEqual(p['status'],'NO_PURCHASE_LEGS_NOT_A_HOLDING_COST_MODEL');self.assertEqual(value['variants'],[])
    def test_unavailable_route_stays_blocked(self):
        self.scenario['manual_route_availability']={'status':'USER_REPORTED_UNAVAILABLE'}
        _,value,p=self.attach();self.assertEqual(value['status'],'DECLARED_EXECUTION_ROUTE_UNAVAILABLE');self.assertEqual(value['variants'],[])
    def test_authoritative_source_error_cannot_fall_back(self):
        _,value,_=self.attach(document={'status':'SCENARIO_REVIEWED_COST_SOURCE_UNAVAILABLE','scenarios':[]});self.assertEqual(value['variants'],[])
    def test_expired_snapshot_is_withdrawn_even_before_recollection(self):
        p=self.f.project()
        with self.assertRaisesRegex(ValueError,'CURRENT_EXACT_REVIEW_SOURCE_REQUIRED'):
            pipeline.context(self.scenario,p,'account-BRL','BRL',now=NOW+dt.timedelta(hours=2))
    def test_reconstruction_rejects_changed_component_total_and_source_currency(self):
        for key,value in [('amount','100'),('currency','EUR')]:
            p=self.f.project();p['legs'][0]['reviewed_candidates'][0]['source']['components']['brokerage'][key]=value
            with self.assertRaises(ValueError):pipeline.context(self.scenario,p,'account-BRL','BRL',now=NOW)
    def test_projection_cannot_grant_authority(self):
        p=self.f.project();p['execution_authorized']=True
        with self.assertRaises(ValueError):pipeline.context(self.scenario,p,'account-BRL','BRL',now=NOW)
    def test_real_store_snapshot_has_no_writes_and_is_shared_by_both_views(self):
        self.f.f.apply();before={p:p.read_bytes() for p in self.f.f.root.rglob('*') if p.is_file()}
        doc=reviewed.build(self.f.f.root,self.view,self.assessments,now=NOW)
        summary,value,p=self.attach(document=doc)
        self.assertEqual(value['variants'][0]['reviewed_execution_cost'],p['purchase_execution_cost_estimate'])
        self.assertEqual(summary['cost_source_digest'],doc['cost_source_digest']);self.assertEqual(before,{p:p.read_bytes() for p in self.f.f.root.rglob('*') if p.is_file()})
    def test_complete_store_replacement_is_used_instead_of_old_snapshot_context(self):
        self.attach();self.f.row['components']['brokerage']['amount']='2'
        _,value,p=self.attach();self.assertEqual(value['variants'][0]['reviewed_execution_cost'],'2.50');self.assertEqual(p['purchase_execution_cost_estimate'],'2.50')
    def test_explicit_cash_model_reuses_existing_comparison_without_validating_return(self):
        from universal_portfolio.cash_counterfactual_comparison_a24 import MODEL_SCHEMA
        self.scenario['funding_context_fingerprint']='current'
        model={'schema':MODEL_SCHEMA,'status':'EXPLICIT_CASH_RETURN_ESTIMATE','account_id':'account-BRL','currency':'BRL','plan_id':'p','budget_id':'b','horizon_unit':'OBSERVATIONS','horizon_value':30,'reference_capital':'100','context_fingerprint':'current','source_ref':'synthetic-source','model_ref':'synthetic-model','model_version':'test','computed_at':(NOW-dt.timedelta(minutes=1)).isoformat(),'review_until':(NOW+dt.timedelta(hours=1)).isoformat(),'expected_net_change':'0.20','cash_cost_coverage':'NET_OF_MODELLED_CASH_COSTS_AND_TAXES','investment_carrying_cost_status':'KNOWN','investment_carrying_cost':'0.10','execution_authorized':False}
        _,value,_=self.attach(cash_models=[model]);comparison=value['variants'][0]['cash_counterfactual_comparison']
        self.assertEqual(comparison['net_advantage_vs_preserving_cash'],'9.10');self.assertFalse(comparison['comparison_authorized']);self.assertFalse(comparison['model_validation_proven']);self.assertIsNone(comparison['decision'])

if __name__=='__main__':unittest.main()
