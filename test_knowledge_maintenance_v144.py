import json,tempfile,unittest
from pathlib import Path
from brain.knowledge.system_registry import SystemKnowledgeRegistry
from brain.knowledge import maintenance_a24 as maintenance
from brain.patches import PatchRegistry

class Knowledge(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.source=self.root/'static/app.js';self.source.parent.mkdir();self.source.write_text('BASE')
        self.r=SystemKnowledgeRegistry(self.root);self.r.refresh()
    def drift(self):self.source.write_text('APPROVED_OR_UNREVIEWED_NEW_SOURCE')
    def test_current_knowledge_is_read_only_and_financial_data_does_not_create_drift(self):
        p=self.root/'data/institution_accounts.json';p.write_text('{"cash":"PRIVATE_VALUE"}')
        self.assertTrue(self.r.verify()['current'])
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.r.load();self.r.query('proteção venda');self.r.verify()
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        self.assertNotIn('PRIVATE_VALUE',json.dumps(self.r.build()))
    def test_drift_creates_one_data_only_patch_without_silently_refreshing_expected_hashes(self):
        before=self.r.path.read_bytes();self.drift();out=maintenance.maintain(self.root)
        self.assertEqual(out['status'],'KNOWLEDGE_REFRESH_PROPOSED');self.assertFalse(self.r.verify()['current'])
        self.assertEqual(self.r.path.read_bytes(),before);self.assertFalse(out['production_code_modified'])
        again=maintenance.maintain(self.root);self.assertEqual(out['patch_id'],again['patch_id'])
        self.assertEqual(len(PatchRegistry(self.root).list()),1)
        p=PatchRegistry(self.root).get(out['patch_id']);self.assertEqual(p['candidate']['target'],maintenance.TARGET)
        self.assertTrue(maintenance.validate_candidate(self.root,p['candidate']))
    def test_manual_application_updates_only_description_and_revalidates_live_hashes(self):
        self.drift();out=maintenance.maintain(self.root);source=self.source.read_bytes()
        result=PatchRegistry(self.root).implement(out['patch_id'])
        self.assertTrue(result['implemented'],result);self.assertEqual(self.source.read_bytes(),source)
        self.assertTrue(self.r.verify()['current']);self.assertFalse(result['validation']['financial_validation_granted'])
    def test_changed_code_or_candidate_content_prevents_patch_application(self):
        self.drift();out=maintenance.maintain(self.root);patch=PatchRegistry(self.root).get(out['patch_id'])
        self.source.write_text('CHANGED_AGAIN')
        self.assertFalse(PatchRegistry(self.root).implement(out['patch_id'])['implemented'])
        patch=PatchRegistry(self.root).get(maintenance.maintain(self.root)['patch_id'])
        p=self.root/patch['candidate']['path'];body=json.loads(p.read_text());body['principles'].append('FAKE_FINANCIAL_AUTHORITY');p.write_text(json.dumps(body))
        self.assertFalse(PatchRegistry(self.root).implement(patch['id'])['implemented'])
    def test_refresh_archives_previous_metadata_and_updated_profile_is_searchable(self):
        before=self.r.path.read_bytes();self.drift();self.r.refresh()
        self.assertTrue(self.r.verify()['current'])
        archives=list((self.r.path.parent/'history').glob('*.json'));self.assertTrue(archives)
        self.assertTrue(any(json.loads(p.read_text())==json.loads(before) for p in archives))
        found=self.r.query('proteção índices globais');self.assertTrue(any(r['id']=='global_operational_decisions' for r in found))
    def test_corrupt_cache_is_not_claimed_current_and_is_preserved_for_review(self):
        self.r.path.write_text('BROKEN');self.assertFalse(self.r.verify()['current'])
        out=maintenance.maintain(self.root);self.assertEqual(out['status'],'KNOWLEDGE_REFRESH_PROPOSED');self.assertEqual(self.r.path.read_text(),'BROKEN')
    def test_missing_cache_can_initialize_description_without_code_change(self):
        self.r.path.unlink();out=maintenance.maintain(self.root)
        self.assertEqual(out['status'],'DESCRIPTION_INITIALIZED');self.assertEqual(self.source.read_text(),'BASE')
    def test_self_model_describes_global_scope_without_mutating_learning_memory(self):
        from brain.core.self_model import SelfModel
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        answer=SelfModel(self.root).answer('Quem é você?')
        self.assertIn('investimentos globais',answer['answer'])
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def test_knowledge_http_views_are_readonly_and_show_proposed_patch_without_financial_authority(self):
        from flask import Flask
        from unittest.mock import patch
        from webapp import system_knowledge_api_v38268 as api
        self.drift();state=maintenance.maintain(self.root)
        app=Flask(__name__);app.register_blueprint(api.bp)
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with patch.object(api,'ROOT',self.root):
            for url in ('/api/system-knowledge','/api/system-knowledge/search?q=protecao'):
                response=app.test_client().get(url);self.assertEqual(response.status_code,200)
                body=response.get_json();self.assertFalse(body['integrity']['current'])
                self.assertEqual(body['maintenance']['patch_id'],state['patch_id'])
                self.assertFalse(body['financial_validation_granted'])
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def test_symlink_target_is_refused_before_candidate_promotion(self):
        self.drift();out=maintenance.maintain(self.root);target=self.r.path
        target.unlink();external=self.root/'outside.json';external.write_text('PRESERVED');target.symlink_to(external)
        result=PatchRegistry(self.root).implement(out['patch_id']);self.assertFalse(result['implemented']);self.assertEqual(external.read_text(),'PRESERVED')

if __name__=='__main__':unittest.main()
