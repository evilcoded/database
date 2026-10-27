import copy,datetime as dt,json,unittest
from decimal import Decimal
from unittest.mock import patch
import test_cost_review_flow_v129 as fixture
from universal_portfolio import cost_review_sources_a24 as sources
from universal_portfolio import account_cost_evidence_a24 as costs
from universal_portfolio import scenario_documentary_sources_a24 as documents
from webapp import research_cost_review_api_a24 as api

NOW=fixture.NOW

class Sources(unittest.TestCase):
    def setUp(self):
        self.f=fixture.ReviewFlow();self.f.setUp();self.addCleanup(self.f.doCleanups);self.root=self.f.root
        self.case=self.f.get().get_json()['cases'][0]
    def projection(self):
        return {'status':'ROUTE_DOCUMENTARY_COMPONENTS_PROJECTED','account_id':self.case['account_id'],'currency':self.case['currency'],'execution_authorized':False,
            'legs':[{'instrument_id':self.case['instrument_id'],'currency':self.case['currency'],'side':'BUY','reference_notional':self.case['reference_amount'],
             'status':'DOCUMENTED_ROUTE_COMMISSION_COMPUTED','policy_id':'synthetic-policy','execution_route':'BANK_APP','documented_component_subtotal':'1.50','rate_pct':'1.5','rounding':'CEILING_CURRENCY_QUANTUM','unresolved_components':['spread'],
             'source':{'url':'https://example.org/pricing','document_sha256':'a'*64,'observed_at':(NOW-dt.timedelta(days=1)).isoformat(),'review_until':(NOW+dt.timedelta(days=1)).isoformat()}}]}
    def test_documentary_rate_remains_reference_without_filling_or_validation(self):
        p=self.projection();before=copy.deepcopy(p);result=sources.guidance(p,self.case,now=NOW)
        self.assertEqual(result['documents'][0]['documented_component_subtotal'],'1.50');self.assertFalse(result['fills_review_fields']);self.assertFalse(result['complete_cost_estimate_created']);self.assertEqual(p,before)
    def test_other_amount_account_currency_instrument_or_side_not_reused(self):
        for key,value,where in [('account_id','other','projection'),('currency','EUR','projection'),('reference_notional','101','leg'),('instrument_id','other','leg'),('side','SELL','leg')]:
            p=self.projection();(p if where=='projection' else p['legs'][0])[key]=value
            self.assertEqual(sources.guidance(p,self.case,now=NOW)['documents'],[],(key,value))
    def test_expired_future_and_unsafe_links_are_not_documents(self):
        for field,value in [('review_until',(NOW-dt.timedelta(seconds=1)).isoformat()),('observed_at',(NOW+dt.timedelta(seconds=1)).isoformat()),('url','javascript:alert(1)'),('url','https://name:secret@example.org/')]:
            p=self.projection();p['legs'][0]['source'][field]=value;self.assertEqual(sources.guidance(p,self.case,now=NOW)['documents'],[])
    def test_quote_required_source_has_no_made_up_commission(self):
        p=self.projection();p['legs'][0].update(status='ROUTE_PRETRADE_QUOTE_REQUIRED',documented_component_subtotal=None)
        d=sources.guidance(p,self.case,now=NOW)['documents'][0];self.assertEqual(d['status'],'ROUTE_PRETRADE_QUOTE_REQUIRED');self.assertIsNone(d['documented_component_subtotal'])
    def test_current_review_reusable_only_with_same_exact_scope_and_validity(self):
        body=self.f.payload();body['components']['brokerage'].update(status='KNOWN',amount='0');self.assertEqual(self.f.post(body).status_code,201)
        data=self.f.get().get_json()['cases'][0];self.assertEqual(len(data['current_review_options']),1)
        option=data['current_review_options'][0];self.assertEqual(option['components']['brokerage']['amount'],'0');self.assertEqual(option['components']['spread']['status'],'UNKNOWN')
        self.assertEqual(option['valid_until'],body['valid_until']);self.assertTrue(option['confirmation_required_again']);self.assertFalse(option['validity_extended'])
        self.f.clock[0]=NOW+dt.timedelta(hours=2);self.assertEqual(self.f.get().get_json()['cases'][0]['current_review_options'],[])
    def test_old_review_not_reused_after_supersession(self):
        body=self.f.payload();self.assertEqual(self.f.post(body).status_code,201)
        self.f.clock[0]+=dt.timedelta(seconds=1);new=self.f.payload();new['execution_venue_id']=body['execution_venue_id'];new['components']['brokerage'].update(status='KNOWN',amount='2')
        self.assertEqual(self.f.post(new).status_code,201)
        options=self.f.get().get_json()['cases'][0]['current_review_options'];self.assertEqual(len(options),1);self.assertEqual(options[0]['components']['brokerage']['amount'],'2')
    def test_reading_sources_never_writes_files_or_grants_mutation(self):
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()};self.f.get();sources.guidance(self.projection(),self.case,now=NOW)
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def test_prior_quote_of_different_amount_is_not_reused(self):
        self.assertEqual(self.f.post(self.f.payload()).status_code,201)
        registered,_=costs.accounts(self.root);reviews=costs.load(self.root,now=NOW)
        self.assertEqual(sources.current_options({**self.case,'reference_amount':'101'},reviews,registered,now=NOW),[])
    def test_known_scientific_decimal_is_presented_without_rounding_for_existing_form(self):
        body=self.f.payload();body['components']['brokerage'].update(status='KNOWN',amount='1E-4');self.assertEqual(self.f.post(body).status_code,201)
        option=self.f.get().get_json()['cases'][0]['current_review_options'][0]
        self.assertEqual(option['components']['brokerage']['amount'],'0.0001')
    def test_scenario_documentary_adapter_is_shared_without_changing_sizing(self):
        view,assessment=self.f.f.views();before=copy.deepcopy(view);p=self.projection()
        with patch.object(documents.routes,'build',return_value=p):documents.attach(self.root,view,assessment,[],{},now=NOW)
        scenario=view['contexts'][0]['learned_scenario_transport']['scenarios'][0]
        self.assertEqual(scenario['documentary_cost_projection'],p);scenario.pop('documentary_cost_projection');self.assertEqual(view,before)
    def test_declared_unavailable_route_does_not_trigger_documentary_projection(self):
        view,assessment=self.f.f.views();view['contexts'][0]['learned_scenario_transport']['scenarios'][0]['manual_route_availability']={'status':'USER_REPORTED_UNAVAILABLE'}
        with patch.object(documents.routes,'build',side_effect=AssertionError('Do not project unavailable route')):documents.attach(self.root,view,assessment,[],{},now=NOW)
        self.assertEqual(view['contexts'][0]['learned_scenario_transport']['scenarios'][0]['documentary_cost_projection']['status'],'DECLARED_EXECUTION_ROUTE_UNAVAILABLE')
    def test_guidance_cannot_be_submitted_as_an_extra_review_field(self):
        body=self.f.payload();body['documentary_guidance']=sources.guidance(self.projection(),self.case,now=NOW)
        self.assertEqual(self.f.post(body).status_code,409);self.assertEqual(costs.load(self.root,now=NOW),{})
    def test_quote_sources_are_exposed_by_the_existing_cases_endpoint(self):
        monitor=self.f.monitor();scenario=monitor['cash_plan_visibility']['contexts'][0]['learned_scenario_transport']['scenarios'][0];scenario['documentary_cost_projection']=self.projection()
        cases,_,_=api.cases(self.root,monitor,now=NOW);self.assertEqual(next(iter(cases.values()))['documentary_guidance']['documents'][0]['source_url'],'https://example.org/pricing')
    def test_real_existing_route_adapter_supplies_hints_without_cost_review_write(self):
        registry=json.loads(self.f.f.f.registry.read_text());registry['institutions'][0]['name']='Synthetic Bank';registry['accounts'][0].update(management_mode='MANUAL',pricing_plan='Synthetic Plan');self.f.f.f.registry.write_text(json.dumps(registry))
        directory=self.root/'config';directory.mkdir(exist_ok=True)
        document={'schema':'porquinho.route-documentary-cost-policies-a24/1.0','policies':[{'policy_id':'synthetic-policy','execution_route':'BANK_APP',
            'scope':{'institution_name':'Synthetic Bank','registry_country':'PT','currency':'BRL','channel':'BANK_APP','management_mode':'MANUAL','channel_evidence':'USER_DECLARED_EXECUTION_CHANNEL','asset_classes':['CRYPTO'],'sides':['BUY'],'pricing_plans':['Synthetic Plan'],'instrument_ids':[self.case['instrument_id']]},
            'source':{'url':'https://example.org/pricing','document_sha256':'a'*64,'observed_at':(NOW-dt.timedelta(days=1)).isoformat(),'review_until':(NOW+dt.timedelta(days=1)).isoformat()},
            'commission':{'rule':'PERCENT_OF_TRADE_NOTIONAL','rate_pct':'1.5','rounding':'CEILING_CURRENCY_QUANTUM','currency_quantum':'0.01'},'unresolved_components':['spread','slippage']}]}
        (directory/'official_execution_route_policies_a24.json').write_text(json.dumps(document))
        _,assessment=self.f.f.views();view=self.f.monitor()['cash_plan_visibility'];documents.attach(self.root,view,assessment,[{'instrument_id':self.case['instrument_id'],'asset_class':'CRYPTO'}],{},now=NOW)
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        case=next(iter(api.cases(self.root,{'cash_plan_visibility':view},now=NOW)[0].values()))
        self.assertEqual(Decimal(case['documentary_guidance']['documents'][0]['documented_component_subtotal']),Decimal('1.50'));self.assertEqual(case['current_review_options'],[])
        self.assertEqual(costs.load(self.root,now=NOW),{});self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

if __name__=='__main__':unittest.main()
