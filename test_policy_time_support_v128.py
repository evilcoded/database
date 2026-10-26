"""Global structural grouping, unchanged learner, economic reconstruction, fairness."""
import copy
import datetime as dt
import unittest
from unittest.mock import patch
import test_a24_learned_allocation_policy as fixture
import test_a24_learned_policy_economic_basis as basis_fixture
from brain.evolution import learned_allocation_policy_a24 as learner
from brain.evolution import global_existing_lab_a24 as lab
from brain.evolution import prospective_allocation_policy_a24 as trials
from universal_portfolio import learned_policy_economic_basis_a24 as basis
from universal_portfolio import explicit_market_bindings_a24 as bindings

NOW=fixture.NOW

def heterogeneous():
    e=fixture.experiment()
    for row in e['folds']:
        if row['provider_id']=='source-1':
            row['target']=(dt.date.fromisoformat(row['target'])+dt.timedelta(days=2)).isoformat()
    for row in e['forecasts']:
        if row['provider_id']=='source-1':row['origin']='2026-10-15';row['last_training_label_end']='2026-10-14'
    return e

def grouped(e):
    return [(g,learner.input_groups.project({'input_partition':g},[e])[0]) for g in learner.input_groups.partitions([e])]

class TimeSupport(unittest.TestCase):
    def test_staggered_history_reproduces_current_server_error_without_dropping_rows(self):
        e=fixture.experiment();first=sorted({r['origin'] for r in e['folds']})[:2]
        e['folds']=[r for r in e['folds'] if not (r['provider_id']=='source-1' and r['origin'] in first)]
        with self.assertRaisesRegex(ValueError,'COMPLETE_COMMON_CROSS_SECTION_REQUIRED'):
            learner.learn([e],now=NOW)
        groups=grouped(e)
        self.assertEqual(sum(len(x['folds']) for _,x in groups),len(e['folds']))
        self.assertTrue(all(learner.learn([x],now=NOW)['status']=='ALLOCATION_POLICY_CANDIDATES_LEARNED_RESEARCH_ONLY' for _,x in groups))

    def test_missing_history_stays_insufficient_instead_of_imputed(self):
        e=heterogeneous();e['folds']=[r for r in e['folds'] if r['provider_id']=='source-0' or r['origin']<'2024-04-01']
        statuses=[learner.learn([x],now=NOW)['status'] for _,x in grouped(e)]
        self.assertIn('INSUFFICIENT_POLICY_RESEARCH_PERIODS',statuses)

    def test_grouping_cannot_bypass_sample_limit_or_currency_guard(self):
        e=heterogeneous();e['folds']*=51
        with self.assertRaisesRegex(ValueError,'POLICY_SAMPLE_LIMIT'):learner.input_groups.partitions([e])
        e=heterogeneous();e['forecasts'][0]['quote_currency']='OTHER'
        with self.assertRaisesRegex(ValueError,'CROSS_CURRENCY'):learner.input_groups.partitions([e])

    def test_original_learner_still_refuses_heterogeneous_population(self):
        with self.assertRaisesRegex(ValueError,'COMMON_REALIZED_INTERVAL'):learner.learn([heterogeneous()],now=NOW)

    def test_every_row_and_source_preserved_once_and_each_group_passes(self):
        e=heterogeneous();groups=grouped(e)
        self.assertEqual(len(groups),2)
        for field in ('folds','forecasts'):
            self.assertCountEqual([repr(r) for _,x in groups for r in x[field]],[repr(r) for r in e[field]])
        self.assertEqual({tuple(k) for g,_ in groups for k in g['identities']},{learner.identity(r) for r in e['forecasts']})
        for _,x in groups:
            r=learner.learn([x],now=NOW)
            self.assertEqual(r['status'],'ALLOCATION_POLICY_CANDIDATES_LEARNED_RESEARCH_ONLY')
            self.assertTrue(all(v is False for k,v in r.items() if k.endswith('_authorized')))

    def test_grouping_does_not_use_outcomes_predictions_or_provider_specific_rules(self):
        e=heterogeneous();a=learner.input_groups.partitions([e])
        x=copy.deepcopy(e)
        for row in x['folds']:row['actual_pct']=97;row['prediction_pct']=-90
        for row in x['forecasts']:row['value_pct']=-99
        self.assertEqual(a,learner.input_groups.partitions([x]))
        x=fixture.experiment()
        for field in ('folds','forecasts'):
            for row in x[field]:row['provider']='bank' if row['provider_id']=='source-0' else 'global-feed'
        self.assertEqual(len(learner.input_groups.partitions([x])),1)

    def test_same_support_keeps_original_input_and_result(self):
        e=fixture.experiment();self.assertEqual(len(learner.input_groups.partitions([e])),1)
        self.assertEqual(learner.input_groups.project({},[e]),[e])

    def test_unequal_model_populations_still_refused(self):
        a=heterogeneous();b=copy.deepcopy(a);b['algorithm']='SVR';b['folds'].pop()
        failures=0
        for marker in learner.input_groups.partitions([a,b]):
            inputs=learner.input_groups.project({'input_partition':marker},[a,b])
            try:learner.learn(inputs,now=NOW)
            except learner.PolicyError:failures+=1
        self.assertGreater(failures,0)

    def test_imposed_subset_not_an_exact_partition_is_refused(self):
        e=heterogeneous();marker=learner.input_groups.partitions([e])[0];marker['time_support_digest']='fake'
        with self.assertRaisesRegex(ValueError,'EXACT_TIME_SUPPORT'):learner.input_groups.project({'input_partition':marker},[e])

    def test_population_is_not_restored_by_filling_missing_forecast(self):
        e=heterogeneous();e['forecasts'].pop()
        rejected=0
        for _,x in grouped(e):
            try:learner.learn([x],now=NOW)
            except learner.PolicyError:rejected+=1
        self.assertEqual(rejected,1)

    def test_same_currency_partitions_have_distinct_prospective_daily_ids(self):
        groups=learner.input_groups.partitions([heterogeneous()])
        self.assertNotEqual(trials.daily_id('2026-10-17','TST',groups[0]),trials.daily_id('2026-10-17','TST',groups[1]))
        self.assertEqual(trials.daily_id('2026-10-17','TST'),bindings.digest({'protocol':trials.PROTOCOL,'day_utc':'2026-10-17','quote_currency':'TST'}))

    def test_complete_global_batch_interleaves_currency_without_provider_policy(self):
        work=[{'metadata':{'quote_currency':q,'algorithm':a}} for q in ('BRL','EUR') for a in lab.legacy.ALGORITHMS]
        ordered=lab.balanced_jobs(work)
        self.assertEqual([j['metadata']['quote_currency'] for j in ordered[:4]],['BRL','EUR','BRL','EUR'])
        self.assertCountEqual([repr(j) for j in work],[repr(j) for j in ordered])

class Persistence(unittest.TestCase):
    def test_all_partitions_persist_reconstruct_and_repeat_without_rewriting_sources(self):
        import tempfile
        from pathlib import Path
        from universal_portfolio import global_history_source_a24 as sealed
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);raw=heterogeneous()
            raw.update(quote_currency='TST',status='EXISTING_LAB_REUSED_GLOBAL_RESEARCH_ONLY')
            source=root/'experiments'/'fixture.json';sealed.store_once(source,raw)
            sentinel=root/'active-model';sentinel.write_bytes(b'UNCHANGED')
            job={'metadata':{'cohort_digest':'fixture'},'path':source,'pairs':[],'eligible':{}}
            plan={'binding_digest':bindings.digest({})}
            with patch.object(lab,'jobs',return_value=(plan,[job])),patch.object(lab,'input_frame',return_value=(None,None)),patch.object(lab,'validate',side_effect=lambda result,*a,**kw:result),patch.object(learner,'load',return_value={}):
                r=learner.run(root,{},now=NOW,revalidate=lambda:set())
                self.assertEqual(r['versions_created'],2)
                self.assertEqual(learner.run(root,{},now=NOW,revalidate=lambda:set())['versions_created'],0)
                for j in learner.work(root,{},NOW)[1]:
                    body=learner.check_stored(sealed.read_sealed(j['path']),j,NOW)
                    self.assertEqual(body['research']['status'],'ALLOCATION_POLICY_CANDIDATES_LEARNED_RESEARCH_ONLY')
                summary=learner.summary(root,{},now=NOW)
                self.assertEqual(len(summary['contexts']),2)
                self.assertEqual(summary['candidate_count'],2)
            self.assertEqual(sealed.read_sealed(source),raw)
            self.assertEqual(sentinel.read_bytes(),b'UNCHANGED')

    def test_full_existing_algorithm_batch_keeps_legacy_files_unchanged(self):
        f=fixture.existing.Reuse();f.setUp();self.addCleanup(f.doCleanups)
        sentinel=f.root/'active-model';sentinel.write_bytes(b'UNCHANGED')
        r=f.runlab(max_jobs=20)
        self.assertEqual(r['experiments_created'],len(lab.legacy.ALGORITHMS))
        self.assertEqual(f.runlab(max_jobs=20)['experiments_created'],0)
        self.assertEqual(sentinel.read_bytes(),b'UNCHANGED')

    def test_batch_limit_does_not_allow_unbounded_or_boolean_values(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            for bound in (0,21,True):
                r=learner.run(tmp,{},now=NOW,max_versions=bound)
                self.assertEqual(r['reason'],'BOUNDED_POLICY_VERSION_COUNT_REQUIRED')
                self.assertEqual(r['versions_created'],0)


class EconomicIntegration(unittest.TestCase):
    def test_two_disjoint_partitions_scope_and_reconstruct_with_exact_raw_sources(self):
        f=basis_fixture.EconomicBasis();f.setUp()
        _,_,refs=f.inputs()
        raw=next(iter(refs.values()))
        for row in raw['folds']:
            if row['provider_id']=='source-1':row['target']=(dt.date.fromisoformat(row['target'])+dt.timedelta(days=2)).isoformat()
        for row in raw['forecasts']:
            if row['provider_id']=='source-1':row['origin']='2026-10-15';row['last_training_label_end']='2026-10-14'
        policies=[]
        for marker in learner.input_groups.partitions([raw]):
            version={'method':learner.METHOD,'input_experiments':{path:bindings.digest(value) for path,value in refs.items()},'input_partition':marker}
            policies.append({'version':version,'computed_at':NOW.isoformat(),'research':learner.learn(learner.input_groups.project(version,[raw]),now=NOW)})
        scope=basis.scoped.project(f.fixture.action,f.fixture.funding,policies)
        self.assertEqual(len(scope['scenarios']),2)
        result=basis.project(scope,policies,refs)
        self.assertEqual(len(result['rows']),2)
        self.assertTrue(all(row['expected_net_change'] is None for row in result['rows']))
        self.assertEqual(len({r['policy_version_digest'] for r in result['rows']}),2)
        for body in policies:
            sources=[{**dict(zip(trials.learner.KEY,k)),'identity_source_ref':'fixture'} for k in body['version']['input_partition']['identities']]
            trial=trials.issue(body,sources,now=NOW)
            self.assertEqual(trials.validate_issue(trial,now=NOW),trial)
        altered=copy.deepcopy(refs);next(iter(altered.values()))['folds'][0]['actual_pct']+=1
        with self.assertRaisesRegex(ValueError,'EXACT_POLICY_SOURCE'):basis.project(scope,policies,altered)

if __name__=='__main__':unittest.main()
