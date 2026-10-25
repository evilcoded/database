import copy,datetime as dt,json,tempfile,unittest
from pathlib import Path
import test_route_costs_v101 as route_fixture
from universal_portfolio.route_documentary_cost_a24 import project,build as build_route
from universal_portfolio.reported_pretrade_preview_a24 import seal,inventory,record,inspect,build_inventory

class Routes(unittest.TestCase):
 def setUp(self):
  self.f=route_fixture.Tests();self.f.setUp()
 def test_other_instrument_requires_tariff_not_bank_and_exchange_fallback(self):
  f=self.f;f.s['legs'][0]['instrument_id']='TEST:NEW';f.catalog=[{'instrument_id':'TEST:NEW','asset_class':'CRYPTO'}]
  r=f.run_project();self.assertEqual(r['status'],'ROUTE_SPECIFIC_COMPONENTS_PENDING');self.assertEqual(r['legs'][0]['status'],'EXACT_ROUTE_POLICY_REQUIRED');self.assertIn('INSTRUMENT_NOT_COVERED_BY_TARIFF_DOCUMENT',r['legs'][0]['route_blocking_reasons']);self.assertIsNone(r['legs'][0]['total_cost']);self.assertFalse(r['variants'])
 def test_missing_plan_not_assumed_standard(self):
  self.f.accounts['account'].pop('pricing_plan');r=self.f.run_project();self.assertIn('ACCOUNT_PRICING_PLAN_REQUIRED',r['legs'][0]['route_blocking_reasons']);self.assertFalse(r['variants'])
 def test_uncovered_plan_is_explicit_not_silently_rerouted(self):
  self.f.accounts['account']['pricing_plan']='Metal';r=self.f.run_project();self.assertIn('PRICING_PLAN_NOT_COVERED_BY_DOCUMENT',r['legs'][0]['route_blocking_reasons']);self.assertFalse(r['variants'])
 def test_ambiguous_catalog_is_fail_closed(self):
  self.f.catalog.append({'instrument_id':self.f.iid,'asset_class':'EQUITY'});r=self.f.run_project();self.assertIn('EXPLICIT_UNIQUE_CATALOG_CLASS_REQUIRED',r['legs'][0]['route_blocking_reasons'])
 def test_documented_equity_exchange_path_remains_available(self):
  self.f.catalog=[{'instrument_id':self.f.iid,'asset_class':'EQUITY'}];self.assertIsNone(self.f.run_project())
 def test_other_bank_no_rate_or_market_venue_assumed(self):
  self.f.accounts['account']['_institution_name']='ANOTHER BANK';r=self.f.run_project();self.assertIn('ACCOUNT_ROUTE_TARIFF_DOCUMENT_REQUIRED',r['legs'][0]['route_blocking_reasons']);self.assertFalse(r['variants'])
 def test_input_catalog_and_accounts_not_changed(self):
  f=self.f;before=copy.deepcopy((f.s,f.a,f.accounts,f.catalog,f.doc));f.run_project();self.assertEqual(before,(f.s,f.a,f.accounts,f.catalog,f.doc))
 def test_malformed_policy_refused_not_fallback(self):
  self.f.doc['policies'][0]['scope']['asset_classes']='CRYPTO';self.assertEqual(self.f.run_project()['status'],'ROUTE_POLICY_CATALOG_INVALID')
 def test_other_class_uses_same_policy_engine_when_document_covers_it(self):
  self.f.catalog=[{'instrument_id':self.f.iid,'asset_class':'SYNTHETIC_CLASS'}];self.f.doc['policies'][0]['scope']['asset_classes']=['SYNTHETIC_CLASS']
  self.assertEqual(self.f.run_project()['status'],'ROUTE_DOCUMENTARY_COMPONENTS_PROJECTED')
 def test_account_plan_display_projection_does_not_change_registry(self):
  from universal_portfolio.universal_cockpit_a24 import project as cockpit
  registry={'institutions':[{'institution_id':'bank','country':'BR','name':'SYNTHETIC'}],'accounts':[{'account_id':'account','institution_id':'bank','currency':'BRL','pricing_plan':'EXPLICIT_PLAN'}]}
  before=copy.deepcopy(registry);r=cockpit([],[],registry,{'instruments':[]},[],observed_at='2026-10-23T09:00:00+00:00')
  self.assertEqual(r['accounts'][0]['pricing_plan'],'EXPLICIT_PLAN');self.assertEqual(registry,before)
 def test_missing_catalog_has_explicit_state(self):
  with tempfile.TemporaryDirectory() as tmp:self.assertEqual(build_route(tmp,{},'EUR',{},'account')['status'],'ROUTE_POLICY_CATALOG_MISSING')

class Previews(unittest.TestCase):
 def setUp(self):
  self.row=seal('account','TEST:ASSET','BRL','100','0','100','2',now=dt.datetime(2026,10,23,tzinfo=dt.timezone.utc));self.doc={'status':'USER_REPORTED_PREVIEWS_READ','execution_authorized':False,'records':[self.row]}
 def test_preview_visible_without_scenario_and_zero_fee_not_total_cost(self):
  before=copy.deepcopy(self.doc);r=inventory(self.doc,{'account':{'currency':'BRL'}})['rows'][0]
  self.assertEqual(r['explicit_commission'],'0');self.assertIsNone(r['total_cost']);self.assertIsNone(r['spread']);self.assertFalse(r['applies_to_other_amounts']);self.assertFalse(r['current_execution_quote_proven']);self.assertEqual(before,self.doc)
 def test_currency_change_not_attached_as_current_scope(self):
  r=inventory(self.doc,{'account':{'currency':'EUR'}})['rows'][0];self.assertEqual(r['status'],'REPORTED_PREVIEW_ACCOUNT_CONTEXT_CHANGED');self.assertFalse(r['current_account_scope_matches'])
 def test_missing_account_not_guessed_from_symbol(self):
  r=inventory(self.doc,{})['rows'][0];self.assertFalse(r['current_account_scope_matches'])
 def test_tampered_preview_not_accepted(self):
  self.row['explicit_commission']='5';r=inventory(self.doc,{});self.assertEqual(r['rows'][0]['status'],'REPORTED_PREVIEW_RECORD_INVALID')
 def test_failed_inspection_not_success_empty(self):
  self.assertEqual(inventory({'status':'PREVIEW_RECORDS_UNAVAILABLE'}, {})['status'],'REPORTED_PREVIEW_INVENTORY_UNAVAILABLE')
if __name__=='__main__':unittest.main()
