import copy,datetime as dt,unittest
from flask import Flask
import test_scenario_reviewed_cost_v125 as fixture
import test_a24_learned_policy_economic_basis as economic_fixture
from universal_portfolio import account_cost_evidence_a24 as costs
from universal_portfolio import research_cash_reference_a24 as cash_reference
from universal_portfolio import cash_plan_visibility_a24 as visibility
from universal_portfolio import learned_cash_plan_transport_a24 as transport
from universal_portfolio import cash_plan_assessment_a24 as assessment
from universal_portfolio import learned_policy_economic_basis_a24 as basis
from universal_portfolio.funded_currency_research_a24 import fingerprint
from webapp import research_cost_review_api_a24 as api
from webapp.local_human_mutation_security_http_r21386eo import LocalHumanHttpSecurity
NOW=fixture.NOW

class ReviewFlow(unittest.TestCase):
    def setUp(self):
        self.f=fixture.Scenario();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.root=self.f.f.root;self.clock=[NOW];self.security=LocalHumanHttpSecurity()
        self.app=Flask(__name__);self.app.register_blueprint(api.init(self.root,monitor_loader=self.monitor,authorize_mutation=self.security.authorize_request,clock=lambda:self.clock[0]));self.client=self.app.test_client()
        boot=self.security.public_bootstrap();self.headers={'Origin':'http://127.0.0.1:8765','X-Porquinho-Session':boot['session_id'],'X-Porquinho-Mutation-Token':boot['mutation_token']}
    def monitor(self):
        rows=list(costs.load(self.root,now=self.clock[0]).values())
        p=fixture.bridge.project(self.f.scenario,self.f.assessment,'account-BRL','BRL',costs.accounts(self.root)[0],rows,now=self.clock[0])
        return {'cash_plan_visibility':{'contexts':[{'account_id':'account-BRL','currency':'BRL','learned_scenario_transport':{'scenarios':[{**self.f.scenario,'reviewed_pretrade_cost_projection':p}]}}]}}
    def get(self):return self.client.get('/api/research/cost-reviews/cases',base_url='http://127.0.0.1:8765')
    def payload(self):
        case=self.get().get_json()['cases'][0]
        return {'case_id':case['case_id'],'review_context_digest':case['review_context_digest'],'execution_venue_id':'BANK_APP_REPORTED_ROUTE','observed_at':NOW.isoformat(),'valid_until':(NOW+dt.timedelta(hours=1)).isoformat(),'source_kind':'OFFICIAL_PRETRADE_QUOTE','source_ref':'synthetic-bank-preview','components':{name:{'status':'UNKNOWN','amount':None} for name in costs.COMPONENTS},'confirmed':True}
    def post(self,body,headers=None):return self.client.post('/api/research/cost-reviews',json=body,base_url='http://127.0.0.1:8765',headers=self.headers if headers is None else headers)
    def projection(self):return self.monitor()['cash_plan_visibility']['contexts'][0]['learned_scenario_transport']['scenarios'][0]['reviewed_pretrade_cost_projection']
    def test_readonly_cases_exact_scope_and_no_writes(self):
        before={str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        r=self.get();self.assertEqual(r.status_code,200);case=r.get_json()['cases'][0]
        self.assertEqual((case['account_id'],case['currency'],case['reference_amount']),('account-BRL','BRL','100'))
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def test_explicit_zero_costs_reach_scenario_without_any_financial_or_model_mutation(self):
        before={str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()};body=self.payload()
        for c in body['components'].values():c.update(status='KNOWN',amount='0')
        r=self.post(body);self.assertEqual(r.status_code,201,r.get_json());self.assertEqual(self.projection()['purchase_execution_cost_estimate'],'0')
        self.assertFalse(r.get_json()['execution_authorized']);self.assertFalse(r.get_json()['model_validation_proven'])
        for path,data in before.items():self.assertEqual(__import__('pathlib').Path(path).read_bytes(),data)
    def test_partial_saved_without_inventing_unknown_components(self):
        body=self.payload();body['components']['brokerage']={'status':'KNOWN','amount':'0'}
        self.assertEqual(self.post(body).status_code,201)
        p=self.projection();self.assertIsNone(p['purchase_execution_cost_estimate']);self.assertIn('taxes',p['legs'][0]['estimate']['missing_components'])
    def test_explicit_update_replaces_prior_only_for_same_scope_and_preserves_old_record(self):
        body=self.payload();self.assertEqual(self.post(body).status_code,201)
        before={p:p.read_bytes() for p in (self.root/costs.STORE/'reviews').glob('*.json')};self.clock[0]+=dt.timedelta(seconds=1)
        updated=self.payload()
        for c in updated['components'].values():c.update(status='KNOWN',amount='0.10')
        r=self.post(updated);self.assertEqual(r.status_code,201,r.get_json());self.assertEqual(r.get_json()['superseded_review_count'],1)
        self.assertEqual(self.projection()['purchase_execution_cost_estimate'],'0.60')
        self.assertEqual(len(costs.load(self.root,now=self.clock[0])),2)
        for p,data in before.items():self.assertEqual(p.read_bytes(),data)
    def test_replay_of_stale_form_not_duplicate_evidence(self):
        body=self.payload();self.assertEqual(self.post(body).status_code,201);self.assertEqual(self.post(body).status_code,409)
        self.assertEqual(len(costs.load(self.root,now=NOW)),1)
    def test_missing_security_and_foreign_origin_refused(self):
        body=self.payload();self.assertEqual(self.post(body,{}).status_code,403)
        self.assertEqual(self.post(body,{**self.headers,'Origin':'https://external.example'}).status_code,403)
        self.assertFalse((self.root/costs.STORE/'reviews').exists())
    def test_unknown_or_changed_case_and_broad_client_authority_refused(self):
        for change in ({'case_id':'unknown'},{'review_context_digest':'old'},{'authority':'BROKER'}):
            body=self.payload();body.update(change);self.assertEqual(self.post(body).status_code,409)
        self.assertFalse((self.root/costs.STORE/'reviews').exists())
    def test_expired_future_naive_dates_and_unconfirmed_refused(self):
        for change in ({'valid_until':NOW.isoformat()},{'observed_at':(NOW+dt.timedelta(seconds=1)).isoformat()},{'observed_at':'2026-01-01T10:00:00'},{'confirmed':False}):
            body=self.payload();body.update(change);self.assertEqual(self.post(body).status_code,409)
    def test_inapplicability_evidence_and_unknown_not_encoded_zero(self):
        body=self.payload();body['components']['exchange_fees']={'status':'NOT_APPLICABLE','amount':None}
        self.assertEqual(self.post(body).status_code,201)
        row=next(iter(costs.load(self.root,now=NOW).values()))
        self.assertEqual(row['components']['exchange_fees']['source_kind'],'APPLICABILITY_EVIDENCE');self.assertIsNone(self.projection()['purchase_execution_cost_estimate'])
    def test_other_amount_or_currency_not_reused(self):
        body=self.payload()
        for c in body['components'].values():c.update(status='KNOWN',amount='0')
        self.assertEqual(self.post(body).status_code,201)
        query={k:next(iter(costs.load(self.root,now=NOW).values()))[k] for k in costs.SCOPE};query['reference_amount']='101'
        self.assertIsNone(costs.estimate(self.root,query,now=NOW)['total_cost'])
    def test_supersession_of_other_scope_refused(self):
        row=self.f.row;self.f.f.apply([row]);new=copy.deepcopy(row);new.update(evidence_id='new',reviewed_at=(NOW+dt.timedelta(seconds=1)).isoformat(),instrument_id='OTHER',supersedes_evidence_ids=[row['evidence_id']])
        with self.assertRaisesRegex(ValueError,'EXACT_PRIOR'):costs.apply_reviewed(self.root,{'schema':costs.SCHEMA,'reviews':[new]},now=NOW+dt.timedelta(seconds=1))
    def test_replaced_review_not_revived_when_successor_expires(self):
        body=self.payload()
        for c in body['components'].values():c.update(status='KNOWN',amount='0')
        self.assertEqual(self.post(body).status_code,201);self.assertEqual(self.projection()['purchase_execution_cost_estimate'],'0');self.clock[0]+=dt.timedelta(seconds=1)
        body=self.payload();body['valid_until']=(NOW+dt.timedelta(seconds=2)).isoformat();self.assertEqual(self.post(body).status_code,201)
        self.clock[0]+=dt.timedelta(seconds=3);self.assertIsNone(self.projection()['purchase_execution_cost_estimate'])
    def test_new_pricing_plan_invalidates_review_that_observed_no_plan(self):
        import json
        body=self.payload()
        for c in body['components'].values():c.update(status='KNOWN',amount='0')
        self.assertEqual(self.post(body).status_code,201)
        registry=json.loads(self.f.f.registry.read_text());registry['accounts'][0]['pricing_plan']='NEW';self.f.f.registry.write_text(json.dumps(registry))
        p=self.projection();self.assertIsNone(p['purchase_execution_cost_estimate']);self.assertEqual(p['legs'][0]['status'],'COST_EVIDENCE_ACCOUNT_CONTEXT_CHANGED')

    def test_changed_evidence_cas_does_not_write(self):
        body=self.payload();case=api.cases(self.root,self.monitor(),now=NOW)[0][body['case_id']]
        row=api.build_row(case,body,{},self.f.registered,now=NOW,actor='PORQUINHO_LOCAL_HUMAN')
        self.f.f.apply()
        with self.assertRaisesRegex(ValueError,'SOURCE_CHANGED'):costs.apply_reviewed(self.root,{'schema':costs.SCHEMA,'reviews':[row]},now=NOW,expected_reviews_digest=api.digest({}))

class ResearchCash(unittest.TestCase):
    def inputs(self):
        f=economic_fixture.EconomicBasis();f.setUp();_,policies,experiments=f.inputs()
        kw=copy.deepcopy(f.fixture.kw);context=kw['funding']['contexts'][0]
        context['canonical_cash_observed']='40';context['capital_status']='ACTIVE_BUDGETS_EXCEED_CURRENT_CASH';context['investment_budget_amount']=None
        context['context_fingerprint']=fingerprint({k:v for k,v in context.items() if k!='context_fingerprint'})
        for r in kw['funding']['research_requests']:r['context_fingerprint']=context['context_fingerprint']
        for row in kw['cash']:row['amount']='40'
        action=economic_fixture.context.a.m.project(**kw)
        return kw,action,policies,experiments
    def test_research_cap_chain_reaches_costs_without_changing_budget_cash_or_order_gate(self):
        kw,action,policies,experiments=self.inputs();before=copy.deepcopy((kw,action,policies,experiments))
        context=kw['funding']['contexts'][0];ref=cash_reference.reference(context)
        self.assertEqual(ref['reference_capital'],'40');self.assertEqual(ref['declared_budget_amount'],'50')
        case=next(c for c in action['cases'] if c['resource_kind']=='CASH');self.assertIsNone(case['capital_ceiling'])
        scope=basis.scoped.project(action,kw['funding'],policies);self.assertTrue(scope['scenarios'])
        econ=basis.project(scope,policies,experiments)
        view=visibility.project(kw['funding'],action);view=transport.attach(view,kw['funding'],scope,econ)
        assessed=assessment.project(view);self.assertTrue(assessed['rows'])
        for row in assessed['rows']:
            self.assertEqual(row['reference_capital'],'40');self.assertEqual(row['checks']['current_plan_capital'],'CURRENT_CASH_CAPPED_RESEARCH_REFERENCE')
            self.assertIn('DECLARED_BUDGET_EXCEEDS_CURRENT_CASH_RESEARCH_REFERENCE_ONLY',row['remaining_source_requirements']);self.assertFalse(row['execution_authorized']);self.assertIsNone(row['requested_amount'])
        self.assertEqual(before,(kw,action,policies,experiments))
        self.assertEqual(view['contexts'][0]['capital_status'],'ACTIVE_BUDGETS_EXCEED_CURRENT_CASH')
    def test_multiple_budgets_not_prorated_or_selected(self):
        kw,*_=self.inputs();c=kw['funding']['contexts'][0];c['planning_budget_intents'].append({'budget_id':'other','amount':'1'})
        self.assertIsNone(cash_reference.reference(c))
    def test_ambiguous_plans_or_disabled_research_not_auto_reconciled(self):
        for key,value in [('active_plan_contexts',[]),('research_enabled',False),('canonical_cash_observed','0')]:
            kw,*_=self.inputs();c=kw['funding']['contexts'][0];c[key]=value;self.assertIsNone(cash_reference.reference(c))
    def test_changed_cash_does_not_accept_old_research_reference(self):
        kw,action,policies,experiments=self.inputs();scope=basis.scoped.project(action,kw['funding'],policies);econ=basis.project(scope,policies,experiments)
        view=transport.attach(visibility.project(kw['funding'],action),kw['funding'],scope,econ);view['contexts'][0]['canonical_cash_observed']='39'
        self.assertTrue(all(r['reference_capital'] is None for r in assessment.project(view)['rows']))

if __name__=='__main__':unittest.main()
