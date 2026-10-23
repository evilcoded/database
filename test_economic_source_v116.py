"""Synthetic complete contracts only, never installed as real model evidence."""
import copy,json,tempfile,unittest
from pathlib import Path
from test_a24_economic_component_set_producer import packet
from test_manual_publication_v115 import ready,NOW
from test_a24_governed_economic_integration import SRC,DST
from universal_portfolio import economic_source_producer_a24 as m
from universal_portfolio import economic_component_set_producer_a24 as assembler
from universal_portfolio import governed_economic_input_transport_a24 as transport
from universal_portfolio import scoped_economic_comparison_a24 as scoped
from universal_portfolio.manual_recommendation_producer_a24 import produce
from universal_portfolio.economic_action_plan_a24 import flags
import test_a24_economic_action_plan as action_fixture


def inputs():
    raw=packet()['sets'][0];rows=[];handoff=[]
    for source in raw['alternatives']:
        action={k:copy.deepcopy(v) for k,v in source.items() if k!='components'}
        if source['alternative_id']=='move':
            action['governed_sizing_candidate']=copy.deepcopy(raw['sizing_candidates'][0])
            for k in ('edge_model','sizing_model'):action['governed_sizing_candidate'][k]['effective_from']='2026-10-01T00:00:00Z'
            for k in ('edge_evidence','sizing_decision'):action['governed_sizing_candidate'][k]['observed_at']='2026-10-23T20:00:00Z'
        components=copy.deepcopy(source['components'])
        bound={k:action.get(k) for k in ('alternative_id','kind','source_instrument_id','destination_instrument_id','reference_capital')}
        bound['case_id']=raw['comparison_set_id']
        for c in components.values():c['action_context']=copy.deepcopy(bound)
        rows.append(action)
        handoff.append({**copy.deepcopy(action),'case_id':raw['comparison_set_id'],'research_readings':components})
    data={'economic_action_plan':{'schema':'porquinho.economic-action-plan-a24/1.0','status':'ACTION_CONTEXTS_PROJECTED_NOT_COMPARATOR_READY',**flags(),
      'cases':[{'case_id':raw['comparison_set_id'],'alternatives_mutually_exclusive':True,'alternatives':rows,'manual_publication':ready()['manual_publication']}]},
      'action_research_handoff':{'schema':'porquinho.action-research-handoff-a24/1.0','status':'CURRENT_RESEARCH_ATTACHED_TO_DRAFT_ACTIONS',**flags(),'alternatives':handoff}}
    # Bind the synthetic sizing output to the exact comparison including its
    # action-specific provenance. This is not a production rebinding fallback.
    _,sets=m.project(data)
    built=assembler.assemble_set(sets[0])
    from universal_portfolio.governed_comparison_producer_a2 import produce_governed_comparisons
    rows=produce_governed_comparisons({'governed_economic_alternatives':built['alternatives'],'governed_economic_source_refs':built['source_refs']})['comparison_rows']
    identity=transport.comparison_identity(rows)
    for a in data['economic_action_plan']['cases'][0]['alternatives']:
        if 'governed_sizing_candidate' in a:a['governed_sizing_candidate']['comparison_id']=identity
    return data

class Source(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
    def run_source(self,data):return m.run(self.root,data,revalidate=lambda:data)
    def test_complete_input_creates_existing_contract_without_changing_flags(self):
        data=inputs();original=copy.deepcopy(data);report=self.run_source(data)
        self.assertTrue(report['source_written']);self.assertEqual(report['complete_set_count'],1);self.assertEqual(data,original)
        stored=json.loads((self.root/m.TARGET).read_text());self.assertEqual(stored['_generated_by'],m.OWNER)
        parsed=transport.collect_inputs(self.root,observed_ids={SRC,DST})
        compared=scoped.size(scoped.compare(parsed),parsed)
        out=produce(self.root,parsed,compared,cycle_id='TEST',observed_at=NOW)
        self.assertEqual(len(out['recommendations']),1)
        self.assertEqual(out['recommendations'][0]['snapshot']['suggested_amount'],850)
    def test_unvalidated_research_does_not_create_empty_source(self):
        data=inputs()
        for r in data['action_research_handoff']['alternatives']:
            for c in r['research_readings'].values():c['validation_status']='NOT_VALIDATED_FOR_COMPARATOR'
        report=self.run_source(data);self.assertFalse(report['source_written']);self.assertFalse((self.root/m.TARGET).exists())
        self.assertEqual(report['complete_set_count'],0)
    def test_missing_component_cannot_be_filtered_from_comparison(self):
        data=inputs();data['action_research_handoff']['alternatives'][0]['research_readings'].pop('transaction_cost')
        report=self.run_source(data);self.assertEqual(report['complete_set_count'],0)
    def test_component_scope_mismatch_refused(self):
        data=inputs();data['action_research_handoff']['alternatives'][0]['research_readings']['forward_return']['currency']='OTHER'
        self.assertEqual(self.run_source(data)['complete_set_count'],0)
    def test_generic_instrument_components_not_action_specific(self):
        data=inputs();data['action_research_handoff']['alternatives'][0]['research_readings']['forward_return'].pop('action_context')
        report=self.run_source(data);self.assertEqual(report['complete_set_count'],0);self.assertIn('EXPLICIT_ACTION_SPECIFIC_COMPONENT_BINDING_REQUIRED',report['blocking_reason_counts'])
    def test_budget_not_invented_as_reference_capital(self):
        data=inputs();data['economic_action_plan']['cases'][0]['alternatives'][0]['reference_capital']=None
        self.assertEqual(self.run_source(data)['complete_set_count'],0)
    def test_foreign_governed_source_preserved(self):
        p=self.root/m.TARGET;p.parent.mkdir(parents=True);p.write_text('{"custom":"preserve"}')
        report=self.run_source(inputs());self.assertEqual(report['status'],'EXISTING_GOVERNED_SOURCE_PRESERVED');self.assertEqual(p.read_text(),'{"custom":"preserve"}')
    def test_changed_inputs_not_written(self):
        data=inputs();changed=copy.deepcopy(data);changed['economic_action_plan']['cases']=[]
        report=m.run(self.root,data,revalidate=lambda:changed)
        self.assertEqual(report['status'],'ACTION_INPUTS_CHANGED_SOURCE_NOT_WRITTEN');self.assertFalse((self.root/m.TARGET).exists())
    def test_repeat_is_idempotent(self):
        data=inputs();self.run_source(data);report=self.run_source(data)
        self.assertEqual(report['status'],'GENERATED_ECONOMIC_SOURCE_CURRENT');self.assertFalse(report['source_written'])
    def test_obsolete_own_sets_withdrawn_without_erasing_foreign_data(self):
        data=inputs();self.run_source(data)
        data['action_research_handoff']['alternatives']=[]
        report=self.run_source(data);self.assertEqual(report['status'],'OBSOLETE_GENERATED_SETS_WITHDRAWN')
        stored=json.loads((self.root/m.TARGET).read_text());self.assertEqual(stored[assembler.KEY]['sets'],[])
    def test_model_and_ledger_preserved(self):
        (self.root/'data').mkdir();(self.root/'data/transaction_ledger.jsonl').write_text('LEDGER_SENTINEL')
        (self.root/'results').mkdir();(self.root/'results/model_params.json').write_text('MODEL_SENTINEL')
        self.run_source(inputs());self.assertEqual((self.root/'data/transaction_ledger.jsonl').read_text(),'LEDGER_SENTINEL');self.assertEqual((self.root/'results/model_params.json').read_text(),'MODEL_SENTINEL')
    def test_source_symlink_refused(self):
        p=self.root/m.TARGET;p.parent.mkdir(parents=True);p.symlink_to('/dev/null')
        self.assertEqual(self.run_source(inputs())['status'],'ECONOMIC_SOURCE_PATH_REFUSED')
    def test_normal_server_stage_uses_real_emitter_and_rechecks_inputs(self):
        import ast,os
        from types import SimpleNamespace
        from unittest.mock import patch
        root=Path(os.environ.get('PORQUINHO_TEST_ROOT','/workspace/porquinho-a24/project'))
        tree=ast.parse((root/'webapp/server.py').read_text())
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_a116_produce_economic_source')
        ns={'ROOT':self.root};exec(compile(ast.Module(body=[fn],type_ignores=[]),'server_source_stage','exec'),ns)
        data=inputs()
        with patch('universal_portfolio.universal_observation_bridge.build_read_only_bridge',return_value=SimpleNamespace(intelligence=data)) as bridge:
            report=ns['_a116_produce_economic_source']()
        self.assertTrue(report['source_written']);self.assertEqual(bridge.call_count,2)
    def test_invalid_input_does_not_abort_legacy_cycle(self):
        self.assertEqual(self.run_source({'economic_action_plan':[]})['complete_set_count'],0)
    def test_actual_draft_directions_cover_buy_sell_and_reduce(self):
        fixture=action_fixture.Plan();plan=fixture.project()
        for case in plan['cases']:
            for a in case['alternatives']:
                if a['kind'] in ('DEPLOY_CASH','INCREASE'):self.assertEqual(a['destination_instrument_id'],a['instrument_id'])
                if a['kind'] in ('KEEP','SELL','REDUCE'):self.assertEqual(a['source_instrument_id'],a['instrument_id'])
    def test_draft_ids_remain_unchanged(self):
        fixture=action_fixture.Plan();plan=fixture.project()
        from universal_portfolio.funded_currency_research_a24 import fingerprint
        for case in plan['cases']:
            for a in case['alternatives']:
                original_source=a['source_instrument_id'] if a['kind']=='REALLOCATE' else None
                self.assertEqual(a['alternative_id'],fingerprint([case['case_id'],a['kind'],a['instrument_id'],original_source]))

if __name__=='__main__':unittest.main()
