import copy,datetime as dt,json,unittest
from unittest.mock import patch
import test_a24_account_cost_evidence as fixture
from universal_portfolio import account_cost_evidence_a24 as costs
from universal_portfolio import scenario_reviewed_cost_a24 as bridge
NOW=fixture.NOW

class Scenario(unittest.TestCase):
 def setUp(self):
  self.f=fixture.Cost();self.f.setUp();self.addCleanup(self.f.doCleanups);self.row=self.f.row();self.registered=costs.accounts(self.f.root)[0]
  self.scenario={'plan_id':'p','budget_id':'b','candidate_id':'c','policy_version_digest':'v','horizon_unit':'OBSERVATIONS','horizon_value':30,'cash_fraction_numerator':0,'cash_fraction_denominator':1,'legs':[{'instrument_id':self.row['instrument_id'],'quote_currency':'BRL','fraction_numerator':1,'fraction_denominator':1}], 'common_research_unit':{'action':'RESEARCH_INCREMENTAL_CASH_DISTRIBUTION','currency':'BRL','reference_capital':'100','expected_gross_change':'10','horizon_unit':'OBSERVATIONS','horizon_value':30},'execution_authorized':False,'recommendation_created':False}
  self.assessment={k:self.scenario[k] for k in bridge.IDS};self.assessment.update(account_id='account-BRL',currency='BRL',status='EXISTING_RESEARCH_EVIDENCE_RECONCILED_NOT_A_FINAL_SUGGESTION',reference_capital='100',expected_gross_change='10',execution_authorized=False,recommendation_created=False)
 def project(self,rows=None,now=NOW):return bridge.project(self.scenario,self.assessment,'account-BRL','BRL',self.registered,[self.row] if rows is None else rows,now=now)
 def views(self):
  return {'schema':'porquinho.cash-plan-visibility-a24/1.0','status':'EXISTING_CASH_PLAN_CONTEXTS_TRANSPORTED','contexts':[{'account_id':'account-BRL','currency':'BRL','learned_scenario_transport':{'scenarios':[self.scenario]}}],'execution_authorized':False,'recommendation_created':False},{'schema':'porquinho.cash-plan-assessment-a24/1.0','status':'EXISTING_CASH_EVIDENCE_ASSESSED_WITHOUT_DECISION','rows':[self.assessment],'execution_authorized':False,'recommendation_created':False}
 def test_reviewed_cost_reaches_exact_existing_scenario_without_model_promotion(self):
  before=copy.deepcopy((self.scenario,self.assessment,self.row));r=self.project();self.assertEqual(r['purchase_execution_cost_estimate'],'0.60');self.assertEqual(r['research_gross_change_less_reviewed_costs'],'9.40');self.assertIsNone(r['expected_net_change']);self.assertFalse(r['reference_budget_covers_allocation_costs_and_preserved_cash']);self.assertEqual(r['research_notional_plus_reviewed_costs'],'100.60');self.assertFalse(r['comparison_authorized']);self.assertFalse(r['model_validation_proven']);self.assertEqual(before,(self.scenario,self.assessment,self.row))
 def test_unknown_component_never_totalled_as_zero(self):
  self.row['components']['taxes'].update(status='UNKNOWN',amount=None);r=self.project();self.assertIsNone(r['purchase_execution_cost_estimate']);self.assertEqual(r['legs'][0]['estimate']['missing_components'],['taxes'])
 def test_explicit_complete_zero_quote_is_not_missing_quote(self):
  for c in self.row['components'].values():c['amount']='0'
  r=self.project();self.assertEqual(r['purchase_execution_cost_estimate'],'0');self.assertFalse(r['model_validation_proven'])
 def test_absence_is_not_free(self):self.assertIsNone(self.project([])['purchase_execution_cost_estimate'])
 def test_other_amount_not_extrapolated(self):
  self.row['reference_amount']='200';r=self.project();self.assertEqual(r['legs'][0]['status'],'EXACT_CURRENT_ORDER_COST_EVIDENCE_REQUIRED');self.assertIsNone(r['purchase_execution_cost_estimate'])
 def test_sell_quote_not_used_as_buy_quote(self):
  self.row['side']='SELL';self.assertIsNone(self.project()['purchase_execution_cost_estimate'])
 def test_expired_quote_not_reused(self):self.assertEqual(self.project(now=NOW+dt.timedelta(hours=2))['legs'][0]['status'],'COST_EVIDENCE_OUTSIDE_VALIDITY')
 def test_multiple_venues_not_chosen_by_price(self):
  other=copy.deepcopy(self.row);other.update(evidence_id='OTHER',execution_venue_id='OTHER_VENUE');r=self.project([self.row,other]);self.assertEqual(r['legs'][0]['status'],'MULTIPLE_REVIEWED_EXECUTION_VENUES_NO_SELECTION');self.assertIsNone(r['purchase_execution_cost_estimate'])
 def test_same_venue_overlapping_reviews_not_arbitrarily_selected(self):
  other=copy.deepcopy(self.row);other['evidence_id']='OTHER';self.assertEqual(self.project([self.row,other])['legs'][0]['status'],'AMBIGUOUS_COST_EVIDENCE_EXPLICIT_SELECTION_REQUIRED')
 def test_plan_change_invalidates_old_quote_even_query_does_not_name_plan(self):
  self.row['pricing_plan']='OLD';self.registered['account-BRL']['pricing_plan']='NEW';r=self.project();self.assertEqual(r['legs'][0]['status'],'COST_EVIDENCE_ACCOUNT_CONTEXT_CHANGED');self.assertIsNone(costs.estimate_from_reviews(self.f.query(),self.registered,[self.row],now=NOW)['total_cost'])
 def test_changed_scenario_not_matched_by_candidate_only(self):
  self.assessment['reference_capital']='90';self.assertEqual(self.project()['status'],'EXACT_RECONCILED_SCENARIO_REQUIRED')
 def test_fractional_notional_not_rounded_to_match_quote(self):
  first=self.scenario['legs'][0];first['fraction_denominator']=3;second=copy.deepcopy(first);second.update(instrument_id='OTHER',fraction_numerator=2);self.scenario['legs'].append(second)
  r=self.project();self.assertEqual(r['legs'][0]['status'],'RESEARCH_NOTIONAL_REQUIRES_EXECUTABLE_AMOUNT_RULE_NO_ROUNDING');self.assertIsNone(r['purchase_execution_cost_estimate'])
 def test_only_cash_distribution_quotes_no_sell_or_holding_inference(self):
  self.scenario['common_research_unit']['action']='REALLOCATE';self.assertEqual(self.project()['status'],'CASH_DISTRIBUTION_COST_CONTEXT_REQUIRED')
 def test_build_calls_existing_store_and_is_read_only(self):
  self.f.apply();view,assessment=self.views();before={str(p):p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()};r=bridge.build(self.f.root,view,assessment,now=NOW);self.assertEqual(r['scenarios'][0]['purchase_execution_cost_estimate'],'0.60');self.assertEqual(before,{str(p):p.read_bytes() for p in self.f.root.rglob('*') if p.is_file()})
 def test_real_estimator_rejects_review_from_previous_registered_plan(self):
  registry=json.loads(self.f.registry.read_text());registry['accounts'][0]['pricing_plan']='OLD';self.f.registry.write_text(json.dumps(registry))
  self.row['pricing_plan']='OLD';self.f.apply([self.row]);registry['accounts'][0]['pricing_plan']='NEW';self.f.registry.write_text(json.dumps(registry))
  r=costs.estimate(self.f.root,self.f.query(),now=NOW);self.assertEqual(r['status'],'COST_EVIDENCE_ACCOUNT_CONTEXT_CHANGED');self.assertIsNone(r['total_cost'])
 def test_two_legs_sum_only_matching_purchase_reviews(self):
  first=self.scenario['legs'][0];first['fraction_denominator']=2;second=copy.deepcopy(first);second['instrument_id']='OTHER';self.scenario['legs'].append(second)
  self.row['reference_amount']='50';other=copy.deepcopy(self.row);other.update(evidence_id='OTHER_QUOTE',instrument_id='OTHER')
  r=self.project([self.row,other]);self.assertEqual(r['purchase_execution_cost_estimate'],'1.20');self.assertEqual(len(r['legs']),2)
 def test_changed_source_withdraws_all_derived_cost_results(self):
  self.f.apply();view,assessment=self.views();rows=costs.load(self.f.root,now=NOW)
  with patch.object(costs,'load',side_effect=[rows,{}]):r=bridge.build(self.f.root,view,assessment,now=NOW)
  self.assertEqual(r['status'],'SCENARIO_REVIEWED_COST_SOURCE_UNAVAILABLE');self.assertEqual(r['scenarios'],[])
if __name__=='__main__':unittest.main()
