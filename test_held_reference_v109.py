"""Regressions for persisted manual BUY events and holding valuation after cash use."""
import copy,datetime as dt,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import test_currency_valuation_v108 as v108
from universal_portfolio import research_quote_acquisition_a24 as q
from universal_portfolio import funded_currency_research_a24 as funding
from universal_portfolio import universal_cockpit_a24 as cockpit
from universal_portfolio.ledger import TransactionLedger
NOW=v108.NOW;IID=v108.IID
class Holdings(unittest.TestCase):
 def setUp(self):
  self.f=v108.CollectionTests();self.f.setUp();self.addCleanup(self.f.tmp.cleanup);self.root=self.f.root
  self.registry={'accounts':[dict(account_id='account-BRL',institution_id='bank',currency='BRL')],'institutions':[dict(institution_id='bank',country='BR')]}
  import json
  (self.root/'data/institution_accounts.json').write_text(json.dumps(self.registry))
  self.ledger=TransactionLedger(self.root/'data/transaction_ledger.jsonl')
  self.ledger.append(dict(event_type='BUY',asset_id=IID,account_id='account-BRL',currency='BRL',quantity='2',unit_price='100',gross_amount='200',executed_at=(NOW-dt.timedelta(minutes=5)).isoformat()))
  self.runtime=dict(authority='NONE',ledger_write=False,ledger_verified=self.ledger.verify(),cutover_effective_from='2026-10-01T00:00:00+00:00',positions=[dict(account_reference='account-BRL',account_status='EXPLICIT_TRANSACTION_ACCOUNT',instrument_id=IID,currency='BRL',quantity='2',cost_basis='200')])
 def demand(self,cash='800',budget='1000'):
  b=dict(budget_id='budget',account_id='account-BRL',currency='BRL',amount=budget,status='ACTIVE',authority='NONE',ledger_semantics='NONE',creates_cash=False,mutates_ledger=False)
  return funding.project(cash=[dict(account_id='account-BRL',currency='BRL',amount=cash)],registry=self.registry,budgets=[b],candidates=[dict(instrument_id=IID,asset_class='CRYPTO')])
 def collect(self,demand=None,now=NOW):
  transport=v108.Transport(now)
  with patch('universal_portfolio.canonical_runtime_read_model.build',return_value=self.runtime):
   result=q._collect_coingecko(self.root,demand or self.demand(),now=now,transport=transport,revalidate=lambda:set())
  return result,transport
 def test_budget_exceeds_cash_still_values_existing_holding_without_new_daily_sample(self):
  demand=self.demand();before=copy.deepcopy((demand,self.runtime))
  self.assertEqual(demand['contexts'][0]['capital_status'],'ACTIVE_BUDGETS_EXCEED_CURRENT_CASH');self.assertEqual(demand['research_requests'],[])
  result,transport=self.collect(demand)
  self.assertEqual(result.get('current_references_refreshed'),1,result);self.assertEqual(result['observations_created'],0);self.assertEqual(len(transport.calls),2);self.assertEqual(q.read_records(self.root),[])
  self.assertEqual(len(q.valuation_records(self.root,now=NOW)),1);self.assertEqual((demand,self.runtime),before)
 def test_zero_cash_does_not_disable_held_market_data(self):
  result,_=self.collect(self.demand(cash='0'));self.assertEqual(result.get('current_references_refreshed'),1,result);self.assertEqual(result['observations_created'],0)
 def test_held_and_funded_jobs_share_same_calls_and_daily_key(self):
  demand=self.f.demand;contexts=self.f.contexts;transport=v108.Transport(NOW)
  with patch('universal_portfolio.canonical_runtime_read_model.build',return_value=self.runtime):result=q._collect_coingecko(self.root,demand,now=NOW,transport=transport,revalidate=lambda:contexts)
  self.assertEqual(len(transport.calls),2);self.assertEqual(result['observations_created'],2);self.assertEqual(result['current_references_refreshed'],2);self.assertEqual(len(q.read_records(self.root)),2)
 def test_wrong_registered_currency_prevents_market_binding(self):
  self.runtime['positions'][0]['currency']='EUR';result,t=self.collect();self.assertEqual(result['held_reference_job_count'],0);self.assertEqual(t.calls,[])
 def test_closed_position_not_collected(self):
  self.runtime['positions'][0]['quantity']='0';result,t=self.collect();self.assertEqual(result['held_reference_job_count'],0);self.assertEqual(t.calls,[])
 def test_duplicate_position_scope_not_collected(self):
  self.runtime['positions']*=2;result,t=self.collect();self.assertEqual(result['held_reference_job_count'],0);self.assertEqual(t.calls,[])
 def test_changed_holding_after_http_does_not_write_any_capture(self):
  with patch('universal_portfolio.canonical_runtime_read_model.build',return_value=self.runtime):initial=q.held_reference_jobs(self.root,now=NOW)
  changed={'jobs':[],'contexts':set()};transport=v108.Transport(NOW)
  with patch.object(q,'held_reference_jobs',side_effect=[initial,initial,changed]):result=q._collect_coingecko(self.root,self.demand(),now=NOW,transport=transport)
  self.assertEqual(result['status'],'ACQUISITION_FAILED_CLOSED');self.assertEqual(len(transport.calls),2);self.assertEqual(q.read_records(self.root),[]);self.assertFalse((self.root/q.LATEST_PATH).exists())
 def test_budget_and_ledger_are_not_modified_by_quote_collection(self):
  before=self.ledger.path.read_bytes();self.collect();self.assertEqual(self.ledger.path.read_bytes(),before);self.assertEqual(self.runtime['positions'][0]['cost_basis'],'200')
 def test_cache_repeated_call_no_new_provider_request(self):
  self.collect();result,t=self.collect(now=NOW+dt.timedelta(seconds=30));self.assertEqual(t.calls,[]);self.assertEqual(result['network_requests'],0)
 def test_refresh_holding_only_still_no_daily_learning_rows(self):
  self.collect();later=NOW+dt.timedelta(minutes=10);result,t=self.collect(now=later);self.assertEqual(len(t.calls),2);self.assertEqual(result.get('current_references_refreshed'),1,result);self.assertEqual(q.read_records(self.root),[])
 def test_zero_closed_row_does_not_hide_positive_holding(self):
  closed={**self.runtime['positions'][0],'quantity':'0'};self.runtime['positions'].append(closed)
  result,_=self.collect();self.assertEqual(result.get('current_references_refreshed'),1,result)
 def test_health_records_real_collector_progress_and_budget_state(self):
  import json
  result,_=self.collect();health=json.loads((self.root/'results/current_crypto_reference_acquisition_a24.json').read_text())
  self.assertEqual(health['checked_at'],NOW.isoformat());self.assertEqual(health['current_references_refreshed'],1);self.assertEqual(health['funding_context_status_counts'],{'ACTIVE_BUDGETS_EXCEED_CURRENT_CASH':1});self.assertFalse(health['financial_mutation'])
 def test_collection_to_valuation_after_real_durable_trade(self):
  from universal_portfolio.monitor_consolidation_a24 import position_records
  self.collect();rows=cockpit.position_quote_boundaries(self.root,position_records(self.runtime['positions']),self.runtime)
  facts=cockpit.project(rows,[],self.registry,{'instruments':[]},q.valuation_records(self.root,now=NOW),observed_at=NOW.isoformat())
  row=facts['positions'][0];self.assertEqual(row['reference_market_value'],'200');self.assertEqual(row['reference_pnl'],'0');self.assertEqual(row['reference_quote_at'],NOW.isoformat());self.assertEqual(row['reference_not_before'],self.ledger.events()[0]['executed_at'])
 def test_actual_durable_event_type_sets_execution_boundary(self):
  # Durable manual trades intentionally have event_type/asset_id and no transaction_type.
  event=self.ledger.events()[0];self.assertNotIn('transaction_type',event)
  rows=cockpit.position_quote_boundaries(self.root,[dict(instrument_id=IID,account_id='account-BRL',currency='BRL',quantity='2',cost_basis='200',account_status='EXPLICIT_TRANSACTION_ACCOUNT')],self.runtime)
  self.assertEqual(rows[0]['reference_not_before'],event['executed_at']);self.assertNotIn('reference_boundary_status',rows[0])
 def test_real_event_boundaries_reject_pre_purchase_reference(self):
  positions=[dict(instrument_id=IID,account_id='account-BRL',currency='BRL',quantity='2',cost_basis='200',account_status='EXPLICIT_TRANSACTION_ACCOUNT')]
  rows=cockpit.position_quote_boundaries(self.root,positions,self.runtime)
  quote=dict(instrument_id=IID,quote_currency='BRL',provider='CoinGecko',provider_id='source-id',price='100',fetched_at=NOW.isoformat(),provider_observed_at=(NOW-dt.timedelta(minutes=6)).isoformat())
  out=cockpit.project(rows,[],self.registry,{'instruments':[]},[quote],observed_at=NOW.isoformat())['positions'][0]
  self.assertIsNone(out['reference_pnl']);self.assertEqual(out['valuation_status'],'REFERENCE_PRECEDES_POSITION_CHANGE')
 def test_following_sell_sets_later_boundary_same_position(self):
  self.ledger.append(dict(event_type='SELL',asset_id=IID,account_id='account-BRL',currency='BRL',quantity='1',unit_price='100',gross_amount='100',executed_at=(NOW-dt.timedelta(minutes=2)).isoformat()));self.runtime['ledger_verified']=self.ledger.verify()
  position=dict(instrument_id=IID,account_id='account-BRL',currency='BRL',quantity='1',cost_basis='100',account_status='EXPLICIT_TRANSACTION_ACCOUNT')
  row=cockpit.position_quote_boundaries(self.root,[position],self.runtime)[0];self.assertEqual(row['reference_not_before'],(NOW-dt.timedelta(minutes=2)).isoformat())
if __name__=='__main__':unittest.main()
