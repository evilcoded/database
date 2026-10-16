import importlib.util,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).with_name('PORQUINHO_A24_AUDITAR_MOEDAS.py');spec=importlib.util.spec_from_file_location('currency_audit',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Audit(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name).resolve()
 def write(self,p,value):
  p=self.root/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value if isinstance(value,str) else json.dumps(value));return p
 def fixture(self,q='EUR'):
  self.write('data/database/market_daily.csv','asset,date,price_eur,quote_currency\nETH,2026-09-01,100,'+q+'\nETH,2026-10-01,110,'+q+'\n')
  self.write('data/brain_experimental_episodes/outcomes_latest.json',{'episodes':[{'asset':'ETH','reference_date':'2026-09-01','reference_price_eur':100,'horizons':[{'status':'MATURED','maturity_date':'2026-10-01','maturity_price_eur':110,'return_pct':10}]}]})
 def test_declared_eur_reference_and_maturity(self):
  self.fixture();r=m.audit(self.root);self.assertEqual(r['episode_market_cross_check']['counts']['matured_same_declared_quote'],1);self.assertFalse(r['currency_attribution_performed'])
 def test_suffix_only_is_unresolved(self):
  self.fixture('');r=m.audit(self.root);self.assertEqual(r['episode_market_cross_check']['counts']['matured_quote_pair_unresolved'],1);self.assertEqual(r['market']['rows_without_explicit_quote'],2)
 def test_different_reference_and_maturity_quotes_flagged(self):
  self.fixture();p=self.root/'data/database/market_daily.csv';p.write_text(p.read_text().replace('110,EUR','110,BRL'));r=m.audit(self.root);self.assertEqual(r['episode_market_cross_check']['counts']['matured_conflicting_declared_quotes'],1)
 def test_currency_is_not_quote(self):
  self.write('results/latest.json',{'scores':[{'price_eur':1,'currency':'EUR'}]});s=m.audit(self.root)['sections']['results/latest.json'];self.assertEqual(s['object_currency_declarations'],{'EUR':1});self.assertEqual(s['object_quote_declarations'],{});self.assertEqual(s['coverage']['price_objects_without_explicit_quote'],1)
 def test_duplicate_market_rows_remain_ambiguous(self):
  self.fixture();p=self.root/'data/database/market_daily.csv';p.write_text(p.read_text()+'ETH,2026-10-01,110,EUR\n');r=m.audit(self.root);self.assertEqual(r['episode_market_cross_check']['counts']['matured_AMBIGUOUS_ASSET_DATE_ROWS'],1)
 def test_source_code_contract_not_historical_certification(self):
  self.write('tools/fetch_history.py',"quote='EUR' if legacy_call else quote_currency\n");r=m.audit(self.root);c=r['source_code_contracts']['tools/fetch_history.py'];self.assertTrue(c['default_quote_eur_branch_present']);self.assertFalse(c['historical_row_provenance_proven'])
 def test_no_mutation_or_export_of_financial_values(self):
  self.fixture();before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
  with patch('socket.socket.connect',side_effect=AssertionError('network')),patch('subprocess.Popen',side_effect=AssertionError('process')):r=m.audit(self.root)
  self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()});self.assertNotIn('"return_pct"',json.dumps(r));self.assertNotIn('"reference_price_eur": 100',json.dumps(r))
 def test_current_snapshot_brazil_scope_count(self):
  self.write('results/latest.json',{'scores':[{'instrument_id':'BR:B3:BDR:AAPL34','quote_currency':'BRL','price':1}]});s=m.audit(self.root)['sections']['results/latest.json'];self.assertEqual(s['explicit_identity_scope_object_counts'],{'BRAZIL_EXPLICIT_ID_PREFIX':1})
 def test_partial_journal_refused(self):
  self.write('results/p35e_research_forecast_issuance.jsonl','{}')
  r=m.audit(self.root);self.assertEqual(r['status'],'PARTIAL_INSPECTION_NOT_CERTIFIED');self.assertEqual(r['issues'][0]['reason'],'PARTIAL_JOURNAL_LINE')
 def test_symlink_refused(self):
  target=self.write('outside.json',{});p=self.root/'results';p.mkdir();(p/'latest.json').symlink_to(target)
  with self.assertRaisesRegex(ValueError,'SYMLINK'):m.audit(self.root)
 def record(self,body,previous='GENESIS'):
  import hashlib
  h=hashlib.sha256((previous+'|'+json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)).encode()).hexdigest()
  return json.dumps({'body':body,'previous_hash':previous,'hash':h}),h
 def test_standard_lf_journal(self):
  text,h=self.record({'quote_currency':'EUR'});rows,f=m.journal((text+'\n').encode());self.assertEqual(f,{'LF':1});self.assertEqual(rows[0]['quote_currency'],'EUR')
 def test_legacy_literal_separator_journal(self):
  text,h=self.record({'quote_currency':'EUR'});second,_=self.record({'quote_currency':'BRL'},h);rows,f=m.journal((text+'\\n'+second+'\\n').encode());self.assertEqual(len(rows),2);self.assertEqual(f,{'LEGACY_LITERAL_BACKSLASH_N':2})
 def test_escaped_newline_inside_body_not_replaced(self):
  body={'note':'literal \\n and actual \n newline'};text,h=self.record(body);rows,_=m.journal((text+'\\n').encode());self.assertEqual(rows,[body])
 def test_wrong_chain_not_accepted(self):
  text,h=self.record({'quote_currency':'EUR'});obj=json.loads(text);obj['hash']='wrong'
  with self.assertRaisesRegex(ValueError,'CHAIN'):m.journal((json.dumps(obj)+'\n').encode())
 def test_unknown_separator_refused(self):
  text,h=self.record({})
  with self.assertRaisesRegex(ValueError,'FRAMING'):m.journal((text+'junk').encode())
 def test_crlf_journal(self):
  text,h=self.record({});rows,f=m.journal((text+'\r\n').encode());self.assertEqual(f,{'CRLF':1})
 def test_partial_journal_does_not_hide_snapshot_results(self):
  self.fixture();self.write('results/latest.json',{'quote_currency':'EUR','price':123});self.write('results/p35e_research_forecast_issuance.jsonl','{}');r=m.audit(self.root);self.assertEqual(r['status'],'PARTIAL_INSPECTION_NOT_CERTIFIED');self.assertEqual(r['market']['row_count'],2);self.assertIn('results/latest.json',r['sections'])
 def test_error_reason_never_exports_arbitrary_exception_text(self):
  self.assertEqual(m.reason(ValueError('SECRET-CONTENT')),'ValueError');self.assertEqual(m.reason(ValueError('SOURCE_SIZE_LIMIT')),'SOURCE_SIZE_LIMIT')
 def test_directory_over_old_2000_limit_streams_all(self):
  directory='data/brain/shadow/outcomes'
  for n in range(2001):self.write(directory+'/'+str(n)+'.json',{'status':'MATURED','quote_currency':'EUR'})
  out=m.summarize_directory(m.Audit(self.root),directory);self.assertEqual(out['status'],'READ');self.assertEqual(out['scanned_file_count'],2001);self.assertEqual(out['stored_matured_status_counts']['objects_with_stored_matured_status'],2001)
 def test_directory_budget_returns_explicit_partial_counts(self):
  directory='data/brain/shadow/outcomes'
  for n in range(3):self.write(directory+'/'+str(n)+'.json',{'status':'MATURED','quote_currency':'EUR'})
  out=m.summarize_directory(m.Audit(self.root),directory,limit=2);self.assertEqual(out['status'],'PARTIAL_DIRECTORY_INSPECTION');self.assertEqual(out['scanned_file_count'],2);self.assertEqual(out['issues'][0]['reason'],'DIRECTORY_FILE_LIMIT')
 def test_directory_bad_file_keeps_global_results(self):
  self.fixture();self.write('data/brain/shadow/outcomes/bad.json','not-json');out=m.audit(self.root);self.assertEqual(out['status'],'PARTIAL_INSPECTION_NOT_CERTIFIED');self.assertEqual(out['market']['row_count'],2);self.assertTrue(out['episode_market_cross_check']);self.assertEqual(out['issues'][0]['reason'],'JSONDecodeError')
 def test_directory_summaries_match_combined_object_counts(self):
  directory='data/brain/shadow/outcomes';values=[{'status':'MATURED','quote_currency':'EUR'},{'assets':[{'currency':'BRL','price_eur':2}]}]
  for n,value in enumerate(values):self.write(directory+'/'+str(n)+'.json',value)
  out=m.summarize_directory(m.Audit(self.root),directory);expected=m.summarize_json(values)
  for key,val in expected.items():
   if isinstance(val,dict):self.assertEqual(out.get(key,{}),val)
if __name__=='__main__':unittest.main()
