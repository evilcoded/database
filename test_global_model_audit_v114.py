import io,json,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
import audit_global_models_v114 as a

class Audit(unittest.TestCase):
    def collect(self,root,fetch=lambda:{'global_existing_lab':{'status':'SYNTHETIC'}}):
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,'w') as z:manifest=a.collect(root,z,fetch=fetch)
        return manifest,zipfile.ZipFile(io.BytesIO(buf.getvalue()))
    def test_input_unchanged_and_secrets_redacted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/a.DATA[0];p.parent.mkdir(parents=True);p.write_text(json.dumps({'token':'SECRET_SENTINEL','ref':'https://example.test?token=SECRET_SENTINEL','value':42}))
            before={str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            manifest,z=self.collect(root)
            self.assertNotIn(b'SECRET_SENTINEL',z.read('project/'+a.DATA[0]))
            self.assertIn(b'42',z.read('project/'+a.DATA[0]))
            self.assertTrue(manifest['files'][len(a.CODE)]['content_redacted'])
            self.assertEqual(before,{str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()})
    def test_symlink_data_not_exported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/a.DATA[0];p.parent.mkdir(parents=True);p.symlink_to('/dev/null')
            _,z=self.collect(root)
            self.assertNotIn('project/'+a.DATA[0],z.namelist())
    def test_api_failure_still_produces_manifest(self):
        def failed():raise TimeoutError()
        with tempfile.TemporaryDirectory() as tmp:
            m,z=self.collect(tmp,failed)
            self.assertEqual(m['api_status'],'UNAVAILABLE');self.assertIn('manifest.json',z.namelist())
    def test_group_limits_and_currentness_not_inferred(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);base=root/'data/brain/global_existing_lab_a24/experiments/test';base.mkdir(parents=True)
            for n in range(4):(base/(str(n)+'.json')).write_text('{}')
            with patch.object(a,'GROUPS',((str(base.parent.relative_to(root)),'*/*.json',2),)):
                m,z=self.collect(root)
            self.assertTrue(m['groups'][0]['truncated']);self.assertEqual(m['groups'][0]['selected'],2)
            self.assertFalse(m['canonical_validation_granted'])
    def test_total_budget_preserves_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in a.DATA:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'large':'x'*12000}))
            with patch.object(a,'MAX_TOTAL',20000):m,z=self.collect(root)
            self.assertIn('manifest.json',z.namelist());self.assertTrue(any(x['status']=='UNAVAILABLE' for x in m['files']))
            self.assertLessEqual(sum(len(z.read(n)) for n in z.namelist()),20000)

if __name__=='__main__':unittest.main()
