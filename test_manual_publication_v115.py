"""Synthetic contracts only; no synthetic evidence is installed in user data."""
import copy,json,tempfile,hashlib,unittest
from pathlib import Path
from datetime import datetime,timezone
from test_a24_scoped_economic_comparison import context
from test_a24_governed_economic_integration import SRC,DST
from universal_portfolio.scoped_economic_comparison_a24 import compare,size,KEY
from universal_portfolio.manual_recommendation_producer_a24 import produce,public
from universal_portfolio.universal_runtime_composition import compose_shadow_cycle

NOW='2026-10-23T21:00:00Z'
def ready(cid='one',account='TEST_ACCOUNT',currency='TST'):
    c=context(cid,account,currency)
    c['manual_publication']={'valid_until':'2026-10-24T00:00:00Z','policy_refs':['SYNTHETIC_POLICY']}
    for item in c['sizing_candidates']:
        for key in ('edge_model','sizing_model'):item[key]['effective_from']='2026-10-01T00:00:00Z'
        for key in ('edge_evidence','sizing_decision'):item[key]['observed_at']='2026-10-23T20:00:00Z'
    return c

class Publication(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
    def inputs(self,sets):
        p=self.root/'results/governed_economic_components_a24.json';p.parent.mkdir(exist_ok=True)
        p.write_text(json.dumps({KEY:sets}))
        return {KEY:sets,'economic_input_transport':{'status':'OBSERVED_NOT_CERTIFIED','source_refs':['results/governed_economic_components_a24.json#sha256:'+hashlib.sha256(p.read_bytes()).hexdigest()]}}
    def evaluate(self,sets):
        data=self.inputs(sets);before={str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        out=produce(self.root,data,size(compare(data),data),cycle_id='SYNTHETIC',observed_at=NOW)
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        return out
    def test_complete_comparison_and_size_reuse_existing_snapshot_composer(self):
        out=self.evaluate([ready()]);row=out['recommendations'][0]['snapshot']
        self.assertEqual(row['action'],'REALLOCATE');self.assertEqual(row['suggested_amount'],850)
        self.assertEqual(row['authority'],'EVIDENCE_ONLY');self.assertFalse(out['execution_authorized']);self.assertFalse(out['research_validation_granted'])
    def test_brl_eur_same_template_separate_accounts(self):
        out=self.evaluate([ready('br','BR_ACCOUNT','BRL'),ready('eu','EU_ACCOUNT','EUR')])
        self.assertEqual({r['snapshot']['currency'] for r in out['recommendations']},{'BRL','EUR'})
    def test_missing_comparison_never_promoted(self):
        out=self.evaluate([]);self.assertEqual(out['recommendations'],[])
    def test_missing_cost_validation_never_promoted(self):
        c=ready();c['alternatives'][0]['evidence']['transaction_cost_validated']=False
        self.assertEqual(self.evaluate([c])['recommendations'],[])
    def test_missing_utility_validation_never_promoted(self):
        c=ready();c['alternatives'][0]['relative_utility_validated']=False
        self.assertEqual(self.evaluate([c])['recommendations'],[])
    def test_unknown_cost_never_zero(self):
        c=ready();c['alternatives'][0]['evidence']['transaction_cost']=None
        self.assertEqual(self.evaluate([c])['recommendations'],[])
    def test_wrong_account_sizing_never_used(self):
        c=ready();c['sizing_candidates'][0]['account_id']='WRONG'
        self.assertEqual(self.evaluate([c])['recommendations'],[])
    def test_wrong_comparison_sizing_never_used(self):
        c=ready();c['sizing_candidates'][0]['comparison_id']='WRONG'
        self.assertEqual(self.evaluate([c])['recommendations'],[])
    def test_missing_size_never_uses_budget(self):
        c=ready();c['sizing_candidates']=[]
        self.assertEqual(self.evaluate([c])['recommendations'],[])
    def test_ambiguous_sizing_refused(self):
        c=ready();c['sizing_candidates']*=2
        self.assertEqual(self.evaluate([c])['recommendations'],[])
    def test_two_same_account_sets_not_oversubscribed(self):
        out=self.evaluate([ready('one'),ready('two')])
        self.assertEqual(out['recommendations'],[]);self.assertIn('OVERLAPPING_ACCOUNT_COMPARISONS_REQUIRE_ONE_JOINT_DECISION',out['blocking_reason_counts'])
    def test_bad_set_does_not_hide_complete_other_account(self):
        bad=ready('bad');bad['alternatives'][0]['evidence']['risk_validated']=False
        out=self.evaluate([bad,ready('good','SECOND')]);self.assertEqual(len(out['recommendations']),1)
    def test_missing_validity_never_invents_expiration(self):
        c=ready();c.pop('manual_publication');self.assertEqual(self.evaluate([c])['recommendations'],[])
    def test_expired_not_published(self):
        c=ready();c['manual_publication']['valid_until']=NOW
        self.assertEqual(self.evaluate([c])['recommendations'],[])
    def test_future_model_and_output_refused(self):
        for field,timefield in [('edge_model','effective_from'),('sizing_decision','observed_at')]:
            c=ready();c['sizing_candidates'][0][field][timefield]='2026-10-25T00:00:00Z'
            self.assertEqual(self.evaluate([c])['recommendations'],[])
    def test_oversized_amount_refused_by_existing_authority(self):
        c=ready();c['sizing_candidates'][0]['sizing_decision']['model_amount']=999999
        self.assertEqual(self.evaluate([c])['recommendations'],[])
    def test_no_allocation_explicit_zero_is_preserved(self):
        c=ready();c['sizing_candidates'][0]['sizing_decision']['model_amount']=0
        out=self.evaluate([c]);self.assertEqual(out['recommendations'][0]['snapshot']['action'],'NO_ALLOCATION');self.assertEqual(out['recommendations'][0]['snapshot']['suggested_amount'],0)
    def test_expiration_rechecked_on_get(self):
        out=self.evaluate([ready()]);self.assertEqual(public(self.root,out,now=datetime(2026,10,25,tzinfo=timezone.utc))['recommendations'],[])
    def test_source_change_withdraws_old_publication(self):
        out=self.evaluate([ready()]);(self.root/'results/governed_economic_components_a24.json').write_text('{}')
        self.assertEqual(public(self.root,out)['recommendations'],[])
    def test_handoff_change_refused(self):
        data=self.inputs([ready()]);scoped=size(compare(data),data);scoped['contexts'][0]['ui_projection']['experimental_brain_proposal']['action']='SELL'
        self.assertEqual(produce(self.root,data,scoped,cycle_id='TEST',observed_at=NOW)['recommendations'],[])
    def test_existing_policy_rejection_is_preserved(self):
        c=ready();c['sizing_candidates'][0]['risk_policy_acceptable']=False
        self.assertEqual(self.evaluate([c])['recommendations'],[])
    def test_source_hash_or_transport_flag_cannot_be_forged_by_ui_payload(self):
        data=self.inputs([ready()]);data['economic_input_transport']['source_refs']=['../outside#sha256:'+'0'*64]
        self.assertEqual(produce(self.root,data,size(compare(data),data),cycle_id='TEST',observed_at=NOW)['recommendations'],[])
    def test_component_assembler_preserves_publication_metadata_without_promoting_validation(self):
        from test_a24_economic_component_set_producer import packet
        from universal_portfolio.economic_component_set_producer_a24 import produce as assemble
        raw=packet();raw['sets'][0]['manual_publication']=ready()['manual_publication']
        result=assemble(raw)
        self.assertEqual(result['sets'][0]['manual_publication'],raw['sets'][0]['manual_publication'])
        self.assertFalse(result['diagnostic']['models_certified_by_assembler'])
    def test_get_api_reuses_cache_without_cycle_or_training(self):
        import ast
        tree=ast.parse((Path(__import__('os').environ.get('PORQUINHO_TEST_ROOT','/workspace/porquinho-a24/project'))/'webapp/server.py').read_text())
        names={'_a115_manual_projection','api_manual_recommendations_a115'}
        nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
        class App:
            def get(self,route):
                self.route=route;return lambda fn:fn
        app=App();cached=self.evaluate([ready()])
        ns={'ROOT':self.root,'_A115_LAST_MANUAL_PUBLICATION':cached,'app':app,'jsonify':lambda v:v,'_clean_json':lambda v:v}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),'server_slice','exec'),ns)
        out=ns['api_manual_recommendations_a115']()
        self.assertEqual(app.route,'/api/recommendations/manual')
        self.assertFalse(out['execution_authorized']);self.assertNotIn('source_proof_refs',out)
    def test_real_runtime_publication_no_writes_or_shadow_snapshot_promotion(self):
        self.inputs([ready()])
        for rel,obj in [('data/universal_positions.json',{'positions':[{'instrument_id':SRC},{'instrument_id':DST}]}),('data/universal_instrument_catalog.json',{'instruments':[{'instrument_id':i,'asset_class':i.split(':')[2],'market':'MKT','jurisdiction':'TEST','currency':'TST'} for i in (SRC,DST)]})]:
            p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj))
        before={str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result=compose_shadow_cycle(self.root,observed_at=NOW,started_at=NOW,cycle_seed='TEST_MANUAL_PUBLICATION')
        self.assertEqual(result.cycle.recommendation_snapshots,())
        self.assertEqual(len(result.manual_recommendation_publication['recommendations']),1)
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

if __name__=='__main__':unittest.main()
