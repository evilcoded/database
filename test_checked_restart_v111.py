import importlib.util,os,signal,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch,call
path=Path(os.environ.get('PORQUINHO_PROJECT',Path.cwd()))/'tools/restart_porquinho_checked_a24.py'
spec=importlib.util.spec_from_file_location('restart',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.cwd=SimpleNamespace(returncode=0,stdout='p777\nfcwd\nn'+str(self.root)+'\n')
  self.api=[{'ok':True,'projection':{}},{'jobs':[{'status':'done'}]}]
 def test_stops_only_idle_verified_listener_then_waits_for_exit(self):
  with patch.object(m,'listeners',side_effect=[{777},{777},set()]),patch.object(m.subprocess,'run',return_value=self.cwd),patch.object(m,'read_api',side_effect=self.api) as api,patch.object(m.os,'kill',side_effect=[None,ProcessLookupError()]) as kill:
   self.assertTrue(m.stop_verified(self.root));self.assertEqual(kill.call_args_list,[call(777,signal.SIGTERM),call(777,0)]);self.assertEqual(api.call_args_list,[call('/api/portfolio/live-projection'),call('/api/status')])
 def test_no_listener_does_not_signal_any_process(self):
  with patch.object(m,'listeners',return_value=set()),patch.object(m.os,'kill') as kill:self.assertFalse(m.stop_verified(self.root));kill.assert_not_called()
 def test_active_cycle_does_not_get_interrupted(self):
  for state in ('running','queued','pending'):
   with patch.object(m,'listeners',return_value={777}),patch.object(m.subprocess,'run',return_value=self.cwd),patch.object(m,'read_api',side_effect=[self.api[0],{'jobs':[{'status':state}]}]),patch.object(m.os,'kill') as kill:
    with self.assertRaises(m.RestartError):m.stop_verified(self.root)
    kill.assert_not_called()
 def test_other_directory_not_terminated(self):
  with patch.object(m,'listeners',return_value={777}),patch.object(m.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='n/another/application\n')),patch.object(m.os,'kill') as kill:
   with self.assertRaises(m.RestartError):m.stop_verified(self.root)
   kill.assert_not_called()
 def test_changed_pid_not_terminated(self):
  with patch.object(m,'listeners',side_effect=[{777},{888}]),patch.object(m.subprocess,'run',return_value=self.cwd),patch.object(m,'read_api',side_effect=self.api),patch.object(m.os,'kill') as kill:
   with self.assertRaises(m.RestartError):m.stop_verified(self.root)
   kill.assert_not_called()
 def test_ambiguous_listener_not_terminated(self):
  with patch.object(m,'listeners',return_value={777,888}),patch.object(m.os,'kill') as kill:
   with self.assertRaises(m.RestartError):m.stop_verified(self.root)
   kill.assert_not_called()
 def test_unavailable_job_state_not_terminated(self):
  with patch.object(m,'listeners',return_value={777}),patch.object(m.subprocess,'run',return_value=self.cwd),patch.object(m,'read_api',side_effect=[self.api[0],{}]),patch.object(m.os,'kill') as kill:
   with self.assertRaises(m.RestartError):m.stop_verified(self.root)
   kill.assert_not_called()
if __name__=='__main__':unittest.main()
