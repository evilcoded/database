"""Synthetic regression tests. Run with PYTHONPATH pointing to the application."""
import ast,copy,datetime as dt,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch,MagicMock
from universal_portfolio import runtime_read_shadow as legacy
from universal_portfolio import research_quote_acquisition_a24 as q
from universal_portfolio import explicit_market_bindings_a24 as bindings
from universal_portfolio import funded_currency_research_a24 as funding
from universal_portfolio import universal_cockpit_a24 as cockpit
from universal_portfolio.experience_panels_a24 import snapshot_point
from universal_portfolio.cockpit_intraday_a24 import snapshot_pnl
NOW=dt.datetime(2026,10,23,12,tzinfo=dt.timezone.utc)
IID='GLOBAL:CRYPTO:CRYPTO:EXAMPLE'
HEAD='a'*64
PROOF=dict(schema='porquinho.legacy-eur-holdings-scope/1.0',currency='EUR',explicit_currency_filter=True,cross_currency_aggregation=False,included_position_count=1,ledger_head_hash=HEAD)
class CurrencyTests(unittest.TestCase):
 def test_foreign_cost_never_enters_legacy_eur_same_asset(self):
  positions=[SimpleNamespace(instrument_id=IID,quantity='2',cost_basis='40',account_reference='eur',currency='EUR'),SimpleNamespace(instrument_id=IID,quantity='3',cost_basis='500',account_reference='brl',currency='BRL'),SimpleNamespace(instrument_id=IID,quantity='1',cost_basis='200',account_reference='unknown',currency=None)]
  runtime=dict(positions=positions,ledger_verified={'head_hash':HEAD});before=copy.deepcopy(runtime)
  with patch.object(legacy,'build',return_value=runtime),patch.object(legacy,'_purchase_meta',return_value={}):
   frame=legacy.crypto_dataframe('/unused');rows=legacy.crypto_rows('/unused')
  self.assertEqual(len(rows),1);self.assertEqual(rows[0]['amount_eur'],40);self.assertEqual(rows[0]['quantity'],'2')
  self.assertEqual(frame.copy().attrs['portfolio_currency_scope']['excluded_position_counts'],{'BRL':1,'UNSPECIFIED':1});self.assertEqual(runtime,before)
 def snapshot(self,proof=None):
  return dict(timestamp=NOW.isoformat(),total_wealth_eur='110',cash_eur='70',portfolio_value_eur='40',total_pnl_eur='-10',portfolio_currency_scope=proof,cash_reconciliation=dict(schema='porquinho.real-cash-reconciliation/2.0',currency='EUR',cross_currency_aggregation=False))
 def test_old_mixed_currency_snapshot_not_trusted(self):self.assertIsNone(snapshot_point(self.snapshot(),now=NOW))
 def test_verified_eur_snapshot_accepted(self):self.assertIsNotNone(snapshot_point(self.snapshot(PROOF),now=NOW))
 def test_false_or_incomplete_scope_rejected(self):
  for k,v in [('currency','BRL'),('explicit_currency_filter',False),('included_position_count',True),('ledger_head_hash','')]:
   proof={**PROOF,k:v};self.assertIsNone(snapshot_point(self.snapshot(proof),now=NOW))
 def test_explicit_global_snapshot_unchanged(self):
  raw=dict(timestamp=NOW.isoformat(),currency='BRL',total_wealth='100',cash='70',portfolio_value='30')
  self.assertEqual(snapshot_point(raw,now=NOW)['currency'],'BRL')
 def test_bad_historical_snapshot_preserved_but_excluded(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'snapshots').mkdir();p=root/'snapshots/snapshot_20261023_120000.json';p.write_text(json.dumps(self.snapshot()));before=p.read_bytes()
   self.assertEqual(snapshot_pnl(root,NOW)['series'],[]);self.assertEqual(p.read_bytes(),before)

class Transport:
 def __init__(self,now,price=100):self.now=now;self.price=price;self.calls=[]
 def get_json(self,path,params,timeout):
  self.calls.append(path)
  if path.endswith('supported_vs_currencies'):return ['eur','brl']
  return {'source-id':{'brl':self.price,'eur':self.price/5,'last_updated_at':int(self.now.timestamp())}}
class CollectionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  (self.root/'data/instruments').mkdir(parents=True)
  (self.root/'data/universal_instrument_catalog.json').write_text(json.dumps({'instruments':[{'instrument_id':IID}]}))
  self.rows=[dict(instrument_id=IID,provider='CoinGecko',provider_id='source-id',quote_currency=c,identity_source_ref='explicit-test',confirmed_by='reviewer',confirmed_at='2026-10-15T00:00:00+00:00',effective_from='2026-10-16') for c in ('BRL','EUR')]
  bindings.local(self.root,bindings.REGISTRY).write_text(bindings.canonical({'schema':bindings.SCHEMA,'bindings':self.rows}))
  accounts=[dict(account_id='account-'+c,institution_id='bank',currency=c) for c in ('BRL','EUR')]
  cash=[dict(account_id=a['account_id'],currency=a['currency'],amount='1000') for a in accounts]
  self.demand=funding.project(cash=cash,registry={'accounts':accounts,'institutions':[dict(institution_id='bank',country='PT')]},candidates=[dict(instrument_id=IID,asset_class='CRYPTO')])
  self.contexts={(c['account_id'],c['currency'],c['context_fingerprint']) for c in self.demand['contexts']}
 def collect(self,now=NOW,price=100):
  transport=Transport(now,price)
  return q._collect_coingecko(self.root,self.demand,now=now,transport=transport,revalidate=lambda:self.contexts),transport
 def test_refresh_prices_without_extra_daily_learning_rows(self):
  first,_=self.collect();self.assertEqual(first['observations_created'],2)
  p=q.storage_path(self.root,NOW.date());before=p.read_bytes()
  later=NOW+dt.timedelta(minutes=10);second,_=self.collect(later,price=110)
  self.assertEqual(second['observations_created'],0);self.assertEqual(second['current_references_refreshed'],2);self.assertEqual(p.read_bytes(),before)
  self.assertEqual(len(q.read_records(self.root)),2)
  current=q.valuation_records(self.root,now=later)
  self.assertEqual({(r['quote_currency'],r['price']) for r in current},{('BRL','110'),('EUR','22.0')})
  self.assertTrue(all(r['sampling']=='LATEST_REFERENCE_NOT_DAILY_TRAINING' for r in current))
 def test_same_cycle_does_not_repeat_network(self):
  self.collect();result,transport=self.collect(NOW+dt.timedelta(seconds=30))
  self.assertEqual(result['network_requests'],0);self.assertEqual(transport.calls,[])
 def test_old_reference_not_used_as_current(self):
  self.collect();self.assertEqual(q.valuation_records(self.root,now=NOW+dt.timedelta(minutes=31)),[])
 def test_next_day_still_one_daily_observation_per_currency(self):
  self.collect();first=q.storage_path(self.root,NOW.date()).read_bytes();tomorrow=NOW+dt.timedelta(days=1);out,_=self.collect(tomorrow)
  self.assertEqual(out['observations_created'],2);self.assertEqual(len(q.read_records(self.root)),4);self.assertEqual(q.storage_path(self.root,NOW.date()).read_bytes(),first)
 def test_changed_binding_does_not_reuse_cached_quote(self):
  self.collect();self.rows[0]['provider_id']='other-id';bindings.local(self.root,bindings.REGISTRY).write_text(bindings.canonical({'schema':bindings.SCHEMA,'bindings':self.rows}))
  self.assertEqual(q.valuation_records(self.root,now=NOW),[])
 def test_corrupt_cache_detected(self):
  self.collect();p=bindings.local(self.root,q.LATEST_PATH);p.write_text(p.read_text().replace('100','999'))
  with self.assertRaises(q.AcquisitionError):q.valuation_records(self.root,now=NOW)
 def test_lost_funding_context_no_refresh_or_model_writes(self):
  self.contexts=set();out,t=self.collect();self.assertEqual(out['status'],'ACQUISITION_FAILED_CLOSED');self.assertEqual(t.calls,[]);self.assertFalse((self.root/'data/brain').exists())

class ValuationTests(unittest.TestCase):
 def setUp(self):
  self.position=dict(instrument_id=IID,account_id='a',account_reference={'value':'a','status':'EXPLICIT_TRANSACTION_ACCOUNT'},account_status='EXPLICIT_TRANSACTION_ACCOUNT',currency='BRL',quantity='2',cost_basis='150',reference_not_before=(NOW-dt.timedelta(minutes=5)).isoformat())
  self.registry={'institutions':[dict(institution_id='bank',country='BR')],'accounts':[dict(account_id='a',institution_id='bank',currency='BRL')]}
  self.obs=dict(instrument_id=IID,quote_currency='BRL',provider='CoinGecko',provider_id='source-id',price='100',fetched_at=NOW.isoformat(),provider_observed_at=(NOW-dt.timedelta(minutes=1)).isoformat())
 def project(self):return cockpit.project([self.position],[],self.registry,{'instruments':[]},[self.obs],observed_at=NOW.isoformat())['positions'][0]
 def test_valid_post_trade_quote(self):
  row=self.project();self.assertEqual(row['reference_market_value'],'200');self.assertEqual(row['reference_pnl'],'50');self.assertEqual(row['reference_quote_age_seconds'],60)
 def test_provider_time_used_instead_of_fetch_time(self):self.assertEqual(self.project()['reference_quote_at'],self.obs['provider_observed_at'])
 def test_quote_before_purchase_cannot_show_loss(self):
  self.obs['provider_observed_at']=(NOW-dt.timedelta(minutes=6)).isoformat();row=self.project();self.assertIsNone(row['reference_pnl']);self.assertEqual(row['valuation_status'],'REFERENCE_PRECEDES_POSITION_CHANGE')
 def test_old_price_and_future_price_rejected(self):
  for at in (NOW-dt.timedelta(hours=2),NOW+dt.timedelta(minutes=1)):
   self.obs['provider_observed_at']=at.isoformat();self.assertIsNone(self.project()['reference_market_value'])
 def test_missing_or_naive_provider_time_not_inferred(self):
  for value in ('','2026-10-23T11:59:00'):
   self.obs['provider_observed_at']=value;self.assertIsNone(self.project()['reference_market_value'])
 def test_wrong_currency_and_wrong_account_not_valued(self):
  self.obs['quote_currency']='EUR';self.assertIsNone(self.project()['reference_market_value'])
  self.setUp();self.registry['accounts'][0]['currency']='EUR';self.assertIsNone(self.project()['reference_market_value'])
 def test_verified_ledger_execution_boundary(self):
  event=dict(transaction_type='BUY',asset_id=IID,account_id='a',currency='BRL',executed_at=(NOW-dt.timedelta(minutes=5)).isoformat())
  ledger=MagicMock();ledger.events.return_value=[event];ledger.verify.return_value={'head_hash':HEAD}
  runtime=dict(ledger_verified={'head_hash':HEAD},cutover_effective_from='2026-10-01T00:00:00+00:00')
  with patch('universal_portfolio.ledger.TransactionLedger',return_value=ledger):rows=cockpit.position_quote_boundaries('/unused',[self.position],runtime)
  self.assertEqual(rows[0]['reference_not_before'],event['executed_at']);self.assertFalse('reference_boundary_status' in rows[0])
 def test_ledger_changed_fail_closed(self):
  ledger=MagicMock();ledger.events.return_value=[];ledger.verify.return_value={'head_hash':'b'*64}
  with patch('universal_portfolio.ledger.TransactionLedger',return_value=ledger):rows=cockpit.position_quote_boundaries('/unused',[self.position],dict(ledger_verified={'head_hash':HEAD}))
  self.position=rows[0];self.assertIsNone(self.project()['reference_market_value'])
if __name__=='__main__':unittest.main()
