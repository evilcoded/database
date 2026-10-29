from unittest.mock import patch
import copy,datetime as dt,json,unittest
import test_global_opportunities_v132 as fixture
from universal_portfolio import global_opportunity_readings_a24 as opportunities
from universal_portfolio import position_reference_reconciliation_a24 as references

NOW=fixture.NOW

class Links(unittest.TestCase):
    def setUp(self):
        self.f=fixture.Opportunities();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.position=self.f.position(instrument_id='REGISTERED:OLD:IDENTITY');self.f.cockpit['positions']=[self.position]
        self.links=[self.chain()]
    def chain(self):
        return {'schema':references.SCHEMA,'account_id':'account-BRL','currency':'BRL','position_instrument_id':self.position['instrument_id'],'research_instrument_id':fixture.fixture.IID,
            'provider':'CoinGecko','provider_id':'source-id','canonical_binding_id':'synthetic-binding','canonical_confirmation_digest':'a'*64,'research_evidence_ref':'synthetic-review','quote_binding_ref':'explicit-test-source','portfolio_id':'synthetic-portfolio','effective_from':'2026-10-16'}
    def build(self):
        return opportunities.build(self.f.root,self.f.demand,self.f.cockpit,self.f.snapshot,fixture.dashboard.CFG,now=NOW,reference_links=self.links)
    def row(self,aid='account-BRL'):
        result=self.build();self.assertEqual(result['status'],'GLOBAL_OPPORTUNITY_RULE_READINGS_INSPECTED',result)
        return next(r for r in result['rows'] if r['account_id']==aid)
    def test_registered_alias_uses_existing_position_rule_not_new_purchase(self):
        before=copy.deepcopy((self.position,self.links,self.f.snapshot));files={p:p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()}
        r=self.row();self.assertTrue(r['position_held']);self.assertEqual(r['action'],'MANTENHA');self.assertTrue(r['rule_evaluation']['position_held'])
        self.assertEqual(r['instrument_id'],fixture.fixture.IID);self.assertEqual(r['position_instrument_id'],self.position['instrument_id']);self.assertEqual(r['position_pnl_pct'],'-18');self.assertTrue(r['position_reference_compatibility_used'])
        self.assertEqual(self.row('second')['action'],'COMPRE');self.assertEqual(before,(self.position,self.links,self.f.snapshot));self.assertEqual(files,{p:p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()})
    def test_alias_hold_matches_registered_position_reading_using_same_market_metrics(self):
        from universal_portfolio.global_action_readings_a24 import project
        direct=project(self.f.cockpit,self.f.snapshot,fixture.dashboard.CFG,now=NOW)['rows'][0]
        r=self.row();self.assertEqual(r['action'],direct['action']);self.assertEqual(r['rule_evaluation'],direct['rule_evaluation'])
    def test_embedded_verified_chain_reused_without_creating_new_mapping(self):
        self.position['reference_identity_chain']=self.links[0];self.links=[];self.assertEqual(self.row()['action'],'MANTENHA')
    def test_duplicate_of_same_chain_from_cockpit_is_not_ambiguity(self):
        self.position['reference_identity_chain']=copy.deepcopy(self.links[0]);self.assertEqual(self.row()['action'],'MANTENHA')
    def test_missing_compatibility_cannot_merge_on_provider_id_or_claim_new_entry(self):
        self.links=[];r=self.row();self.assertIsNone(r['action']);self.assertIsNone(r['position_held']);self.assertEqual(r['status'],'POSITION_REFERENCE_COMPATIBILITY_REVIEW_REQUIRED')
    def test_quote_binding_provider_or_date_change_requires_review(self):
        for key,value in [('quote_binding_ref','changed'),('provider_id','other'),('provider','other'),('effective_from','2026-10-17'),('canonical_binding_id','')]:
            self.links=[{**self.chain(),key:value}];self.assertIsNone(self.row()['action'],(key,value))
    def test_other_account_and_currency_links_do_not_grant_compatibility(self):
        for key,value in [('account_id','second'),('currency','EUR')]:
            self.links=[{**self.chain(),key:value}];self.assertIsNone(self.row()['action'])
    def test_other_account_position_is_not_reused(self):
        self.position['account_id']='unrelated';self.assertEqual(self.row()['action'],'COMPRE');self.assertFalse(self.row()['position_held'])
    def test_valid_identity_remains_held_when_price_is_missing(self):
        self.position.update(reference_provider=None,reference_provider_id=None,reference_pnl_pct=None,reference_quote_at=None)
        r=self.row();self.assertTrue(r['position_held']);self.assertIsNone(r['action']);self.assertEqual(r['status'],'POSITION_PNL_REQUIRED_FOR_COMPLETE_RULE_EVALUATION')
    def test_ambiguous_multiple_financial_positions_never_combined(self):
        other=self.f.position();self.f.cockpit['positions'].append(other)
        r=self.row();self.assertIsNone(r['action']);self.assertEqual(r['status'],'AMBIGUOUS_REGISTERED_POSITION_CONTEXT')
    def test_conflicting_reference_documents_are_not_arbitrarily_selected(self):
        self.links.append({**self.links[0],'canonical_confirmation_digest':'b'*64});self.assertIsNone(self.row()['action'])
    def test_runtime_ledger_chain_uses_same_existing_index_contract(self):
        c=self.chain();c.update(schema=references.LEDGER_SCHEMA,ledger_head_hash='a'*64,position_context_digest='b'*64,authority='NONE',ledger_write=False)
        self.links=[c];self.assertEqual(self.row()['action'],'MANTENHA')
        self.links[0]['ledger_write']=True;self.assertIsNone(self.row()['action'])
    def test_summary_counts_held_and_entry_within_each_account_and_currency(self):
        result=self.build();counts=next(r for r in result['context_counts'] if r['account_id']=='account-BRL');self.assertEqual(counts['held_reading_count'],1);self.assertEqual(counts['entry_reading_count'],0);self.assertEqual(counts['action_counts'],{'MANTENHA':1})
        self.assertEqual(result['action_counts'],{'MANTENHA':1,'COMPRE':2})
    def test_panel_composition_transports_verified_reference_links(self):
        from universal_portfolio.experience_panels_a24 import build
        (self.f.root/'config.json').write_text(json.dumps({'action_rules':fixture.dashboard.CFG}));(self.f.root/'results').mkdir()
        (self.f.root/'results/latest.json').write_text(json.dumps(self.f.snapshot))
        with patch('universal_portfolio.common_action_metrics_a24.read_metrics',return_value={'metrics':self.f.snapshot['scores']}):
            result=build(self.f.root,now=NOW,cockpit=self.f.cockpit,funding=self.f.demand,reference_links=self.links)
        rows=result['global_opportunity_readings']['rows'];r=next(r for r in rows if r['account_id']=='account-BRL')
        self.assertEqual(r['action'],'MANTENHA');self.assertTrue(r['position_reference_compatibility_used'])

if __name__=='__main__':unittest.main()
