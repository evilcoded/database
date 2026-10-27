import copy,unittest
from types import SimpleNamespace
from unittest.mock import patch
import test_cost_review_flow_v129 as fixture
from webapp import research_cost_review_api_a24 as api

class NarrowContext(unittest.TestCase):
    def setUp(self):
        self.f=fixture.ReviewFlow();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.root=self.f.root
    def read(self,route=None):
        view,assessment=self.f.f.views();view=copy.deepcopy(view)
        with patch('universal_portfolio.universal_observation_bridge.build_read_only_bridge',return_value=SimpleNamespace(intelligence={})),patch('universal_portfolio.cash_plan_visibility_a24.project',return_value=view),patch('universal_portfolio.learned_cash_plan_transport_a24.attach',return_value=view),patch('universal_portfolio.cash_plan_assessment_a24.project',return_value=assessment),patch('universal_portfolio.monitor_consolidation_a24.inspect',side_effect=AssertionError('FULL_MONITOR_NOT_NEEDED')):
            if route:
                with patch('universal_portfolio.manual_execution_availability_a24.scenario_status',return_value=route):return api.read_case_context(self.root,now=fixture.NOW)
            return api.read_case_context(self.root,now=fixture.NOW)
    def test_cases_match_existing_projection_without_full_monitor_or_writes(self):
        before={str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        expected=api.cases(self.root,self.f.monitor(),now=fixture.NOW)[0]
        got=api.cases(self.root,self.read(),now=fixture.NOW)[0]
        self.assertEqual({k:{n:v for n,v in r.items() if n!='documentary_guidance'} for k,r in got.items()},{k:{n:v for n,v in r.items() if n!='documentary_guidance'} for k,r in expected.items()})
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def test_unavailable_manual_route_not_bypassed(self):
        data=self.read({'status':'USER_REPORTED_UNAVAILABLE'})
        self.assertEqual(api.cases(self.root,data,now=fixture.NOW)[0],{})
    def test_reviewed_costs_use_same_estimator_and_scope(self):
        body=self.f.payload()
        for row in body['components'].values():row.update(status='KNOWN',amount='0.10')
        self.assertEqual(self.f.post(body).status_code,201)
        expected=api.cases(self.root,self.f.monitor(),now=fixture.NOW)[0]
        data=self.read();got=api.cases(self.root,data,now=fixture.NOW)[0]
        self.assertEqual({k:{n:v for n,v in r.items() if n!='documentary_guidance'} for k,r in got.items()},{k:{n:v for n,v in r.items() if n!='documentary_guidance'} for k,r in expected.items()})
        p=data['cash_plan_visibility']['contexts'][0]['learned_scenario_transport']['scenarios'][0]['reviewed_pretrade_cost_projection']
        self.assertEqual(p['purchase_execution_cost_estimate'],'0.60');self.assertFalse(p['model_validation_proven']);self.assertFalse(p['execution_authorized'])
if __name__=='__main__':unittest.main()
