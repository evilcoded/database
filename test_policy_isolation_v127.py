"""Synthetic regressions for independent cohort rejection and diagnostic integrity."""
import copy
import unittest
from unittest.mock import patch
import test_a24_global_existing_lab as existing
from brain.evolution import learned_allocation_policy_a24 as policy
from universal_portfolio.explicit_market_bindings_a24 import digest

class Isolation(unittest.TestCase):
    def setUp(self):
        self.fixture=existing.Reuse();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.fixture.runlab();self.root=self.fixture.root;self.demand=self.fixture.demand
        self.plan,self.jobs=policy.work(self.root,self.demand,existing.NOW)
        self.good=self.jobs[0]
        self.bad=copy.deepcopy(self.good)
        self.bad['version']={**self.bad['version'],'cohort':'synthetic-invalid-cohort'}
        self.bad['path']=self.root/policy.STORE/'versions'/f"{digest(self.bad['version'])}.json"
        self.bad['pairs'][0][1]['forecasts'].pop()

    def run_policy(self,current=None):
        with patch.object(policy,'work',return_value=(self.plan,[self.bad,self.good])):
            return policy.run(self.root,self.demand,now=existing.NOW,revalidate=current or self.fixture.current)

    def test_bad_first_cohort_does_not_suppress_valid_next_cohort(self):
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        r=self.run_policy()
        self.assertEqual(r['versions_created'],1)
        self.assertEqual(r['blocked_contexts'][0]['reason'],'COMPLETE_COMMON_CURRENT_FORECAST_REQUIRED')
        self.assertFalse(self.bad['path'].exists());self.assertTrue(self.good['path'].exists())
        for p,b in before.items():self.assertEqual(p.read_bytes(),b)
        for k,v in policy.flags().items():self.assertEqual(r[k],v)

    def test_global_funding_change_still_aborts_valid_cohort_write(self):
        r=self.run_policy(lambda:set())
        self.assertEqual(r['versions_created'],0)
        self.assertEqual(r['reason'],'FUNDED_SOURCE_CONTEXT_CHANGED')
        self.assertFalse(self.good['path'].exists());self.assertFalse(self.bad['path'].exists())

    def test_blocked_only_reports_no_version_and_exact_reason(self):
        with patch.object(policy,'work',return_value=(self.plan,[self.bad])):
            r=policy.run(self.root,self.demand,now=existing.NOW)
        self.assertEqual(r['status'],'POLICY_INPUT_CONTRACTS_BLOCKED')
        self.assertEqual(r['versions_created'],0)
        self.assertFalse(self.bad['path'].exists())

    def test_readonly_summary_exposes_rejection_without_fits_writes_or_network(self):
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with patch.object(policy,'work',return_value=(self.plan,[self.bad,self.good])),patch.object(existing.lab,'model_for',side_effect=AssertionError('NO_FIT')),patch.object(existing.h.Transport,'get_json',side_effect=AssertionError('NO_NETWORK')):
            r=policy.summary(self.root,self.demand,now=existing.NOW)
        self.assertEqual(r['contexts'][0]['status'],'POLICY_INPUT_CONTRACT_BLOCKED')
        self.assertEqual(r['contexts'][0]['reason'],'COMPLETE_COMMON_CURRENT_FORECAST_REQUIRED')
        self.assertEqual(r['contexts'][1]['status'],'AWAITING_POLICY_LEARNING')
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_arbitrary_exception_text_not_exported(self):
        self.assertEqual(policy.failure_reason(policy.PolicyError('private source body')),'POLICY_INPUT_INSPECTION_FAILED')
        self.assertEqual(policy.failure_reason(RuntimeError('private source body')),'POLICY_INPUT_INSPECTION_FAILED')

if __name__=='__main__':unittest.main()
