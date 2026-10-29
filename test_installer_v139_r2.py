import ast,base64,contextlib,hashlib,io,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
REPO=Path(__file__).resolve().parent
BASE=Path(os.environ.get('V139_BASELINE_DIR','/tmp/v139-old'))
SCRIPT=(REPO/'PORQUINHO_ANALISE_ACOES_V139_R2.command').read_text().split("<<'PYTHON'\n",1)[1].split('\nPYTHON',1)[0]
FILES=ast.literal_eval(next(line[6:] for line in SCRIPT.splitlines() if line.startswith('FILES=')))

class Installer(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)/'app';shutil.copytree(BASE,self.root)
        for name in ('data/ledger.json','models/weights.json','config.json','data/brain/legacy/unchanged.json'):
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'PRESERVE')
    def apply(self):
        code=SCRIPT.replace("ROOT=Path('/Applications/Bridge_Companion/porquinho_v33_web_foundation-2')",'ROOT=Path('+repr(str(self.root))+')')
        with contextlib.redirect_stdout(io.StringIO()):exec(compile(code,'installer','exec'),{})
    def snapshot(self):return {str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
    def check_package(self):
        source="import sys;sys.path.insert(0,sys.argv[1]);import equities;from equities import technical,risk_regime,opportunity,historical;assert len(historical.normalize_points([{'date':1,'open':10,'high':12,'low':9,'close':11}])[0])==1;assert technical.compute('TEST',[])['history_points']==0"
        subprocess.run([sys.executable,'-I','-B','-c',source,str(self.root)],check=True,capture_output=True,text=True)
    def test_entire_package_absent_is_installed_and_importable_without_credentials(self):
        shutil.rmtree(self.root/'equities');before=self.snapshot();self.apply()
        for name,encoded in FILES.items():self.assertEqual((self.root/name).read_bytes(),base64.b64decode(encoded))
        for name,value in before.items():
            if name not in FILES:self.assertEqual((self.root/name).read_bytes(),value)
        self.check_package();before=self.snapshot();self.apply();self.assertEqual(self.snapshot(),before)
    def test_partial_existing_package_is_completed_preserving_known_history_baseline(self):
        self.apply();self.check_package()
        self.assertEqual(len(list((self.root/'equities').glob('*.py'))),8)
    def test_local_math_changes_are_rejected_before_any_write(self):
        p=self.root/'equities/technical.py';p.write_text('LOCAL CALCULATION CHANGE')
        before=self.snapshot()
        with self.assertRaisesRegex(AssertionError,'BASE_DIVERGENTE_PRESERVADA'):self.apply()
        self.assertEqual(self.snapshot(),before)
    def test_missing_core_file_still_refuses_installation(self):
        (self.root/'universal_portfolio/operational_cycle_a24.py').unlink();before=self.snapshot()
        with self.assertRaisesRegex(AssertionError,'BASE_AUSENTE'):self.apply()
        self.assertEqual(self.snapshot(),before)
    def test_package_symlink_is_refused_before_any_write(self):
        shutil.rmtree(self.root/'equities');outside=Path(self.temp.name)/'outside';outside.mkdir();(self.root/'equities').symlink_to(outside,target_is_directory=True)
        before=self.snapshot()
        with self.assertRaisesRegex(AssertionError,'SYMLINK_RECUSADO'):self.apply()
        self.assertEqual(self.snapshot(),before);self.assertEqual(list(outside.iterdir()),[])

if __name__=='__main__':unittest.main()
