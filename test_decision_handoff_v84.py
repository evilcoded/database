"""Execute the actual refresh handoff with synthetic stage outputs, no imports/network."""
import ast,datetime,unittest
from pathlib import Path
from types import SimpleNamespace as NS

class Handoff(unittest.TestCase):
 def execute(self,fail=None):
  tree=ast.parse((Path(__file__).resolve().parents[1]/'webapp/server.py').read_text())
  f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_refresh')
  block=next(n for n in f.body if isinstance(n,ast.Try) and any(isinstance(v,ast.Name) and v.id=='_a24_run_research_components' for v in ast.walk(n)))
  class NoImports(ast.NodeTransformer):
   def visit_ImportFrom(self,node):return ast.copy_location(ast.Pass(),node)
  block=NoImports().visit(block);events=[];state={'revision':0}
  def bridge(*a,**k):
   events.append('bridge');return NS(intelligence={'funded_currency_research':{'revision':state['revision']}})
  def stage(name):
   def run(root,demand):
    events.append(name)
    if fail==name:raise ValueError('synthetic failure')
    if name=='components':state['revision']=1
    return {'stage':name,'status':'UNCHANGED_OR_PRODUCED'}
   return run
  def compose(*a,**k):
   events.append('evaluate');b=bridge();return NS(bridge=NS(candidates=[],intelligence=b.intelligence),cycle=NS(status='DONE',context=NS(cycle_id='synthetic',observed_at=k['observed_at']),recommendation_snapshots=[],history_write_performed=False,financial_mutation=False,execution_performed=False),economic_decision_ui_projection={'revision':b.intelligence['funded_currency_research']['revision'],'canonical_investment_recommendation':None})
  ns={'ROOT':Path('/tmp/synthetic'), 'datetime':datetime.datetime,'timezone':datetime.timezone,'build_read_only_bridge':bridge,'compose_shadow_cycle':compose,'_a6_safe_projection':lambda v:v,'_A7_LAST_SHADOW_PROJECTION':None,'universal_shadow':None}
  for alias,name in [('_a24_collect_quotes','quotes'),('_a24_collect_history','history'),('_a24_run_global_lab','global_lab'),('_a24_reuse_existing_lab','existing_lab'),('_a24_learn_allocation_policy','allocation'),('_a24_track_policy_trials','trials'),('_a24_run_research_components','components')]:ns[alias]=stage(name)
  exec(compile(ast.fix_missing_locations(ast.Module(body=[block],type_ignores=[])),'refresh-handoff','exec'),ns)
  return events,ns
 def test_current_cycle_consumed_once(self):
  events,ns=self.execute();self.assertEqual(events,['bridge','quotes','history','global_lab','existing_lab','allocation','trials','components','evaluate','bridge']);self.assertEqual(ns['_A7_LAST_SHADOW_PROJECTION']['revision'],1)
  self.assertEqual(ns['universal_shadow']['decision_input_phase'],'AFTER_RESEARCH_STAGES');self.assertIn('research_economic_components',ns['universal_shadow']);self.assertIsNone(ns['_A7_LAST_SHADOW_PROJECTION']['canonical_investment_recommendation'])
 def test_failed_stage_does_not_publish_stale_projection(self):
  events,ns=self.execute('components');self.assertNotIn('evaluate',events);self.assertIsNone(ns['_A7_LAST_SHADOW_PROJECTION']);self.assertEqual(ns['universal_shadow']['status'],'SHADOW_ERROR')
 def test_acquisition_failure_stops_handoff(self):
  events,ns=self.execute('quotes');self.assertEqual(events,['bridge','quotes']);self.assertIsNone(ns['_A7_LAST_SHADOW_PROJECTION'])
if __name__=='__main__':unittest.main()
