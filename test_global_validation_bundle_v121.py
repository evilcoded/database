import copy,json,tempfile,unittest
from pathlib import Path
from collect_global_validation_v121 import collect,scrub

class Bundle(unittest.TestCase):
 def test_only_read_routes_no_files_modified_and_secrets_removed(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'config.json').write_text(json.dumps({'action_rules':{'sell_structural_risk':75},'api_key':'PRIVATE'}))
   (root/'model.json').write_text('PRESERVE');before={str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()};routes=[]
   def get(route):
    routes.append(route)
    return {'read_ok':True,'body':{'snapshot':{'timestamp':'2026-10-24T12:00:00Z'},'portfolio':{'scores':[{'asset':'TEST','risk':70,'quote_currency':'BRL','api_key':'PRIVATE'}]},'status':'BLOCKED','recommendations':[],'token':'PRIVATE'}}
   r=collect(root,get);self.assertEqual(routes,['/api/status','/api/research/monitor-consolidation','/api/recommendations/manual','/api/status'])
   self.assertEqual(before,{str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()});self.assertNotIn('PRIVATE',json.dumps(r));self.assertEqual(r['configured_action_rules']['sell_structural_risk'],75);self.assertTrue(r['snapshot_unchanged_during_collection']);self.assertFalse(r['cycle_requested'])
 def test_cycle_changes_are_reported_not_silently_merged(self):
  with tempfile.TemporaryDirectory() as tmp:
   n=[0]
   def get(route):
    n[0]+=1;return {'read_ok':True,'body':{'snapshot':{'timestamp':str(n[0])}}}
   self.assertFalse(collect(Path(tmp),get)['snapshot_unchanged_during_collection'])
 def test_read_failures_not_empty_success(self):
  with tempfile.TemporaryDirectory() as tmp:
   r=collect(Path(tmp),lambda _: {'read_ok':False,'error_type':'ConnectionError'})
   self.assertFalse(r['monitor']['read_ok']);self.assertFalse(r['snapshot_unchanged_during_collection'])
 def test_url_credentials_redacted(self):
  self.assertNotIn('PRIVATE',scrub('https://provider.test/quote?token=PRIVATE&symbol=TEST'))
if __name__=='__main__':unittest.main()
