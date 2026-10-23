import unittest,sys,tempfile,datetime,json
from pathlib import Path
sys.path.insert(0,'/workspace/porquinho-a24/project')
from universal_portfolio.reported_pretrade_preview_a24 import seal,record,inspect,attach
class Tests(unittest.TestCase):
 def setUp(self):self.row=seal('account','asset','BRL','100','0','100','2',now=datetime.datetime(2026,10,23,tzinfo=datetime.timezone.utc))
 def scenario(self,amount='100',currency='BRL'):return {'common_research_unit':{'reference_capital':amount},'legs':[{'instrument_id':'asset','quote_currency':currency,'fraction_numerator':1,'fraction_denominator':1}]}
 def test_no_zero_cost_promotion(self):self.assertIsNone(self.row['spread']);self.assertIsNone(self.row['total_cost']);self.assertIsNone(self.row['quote_observed_at']);self.assertEqual(self.row['explicit_commission'],'0');self.assertEqual(self.row['implied_debit_per_unit'],'50')
 def test_record_repeat_and_read(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertEqual(record(d,self.row)['status'],'USER_REPORTED_PREVIEW_RECORDED');self.assertEqual(record(d,self.row)['status'],'REPORTED_PREVIEW_ALREADY_RECORDED');self.assertEqual(len(inspect(d)['records']),1)
 def test_exact_scope_does_not_prove_current_quote(self):
  r=attach(self.scenario(),'account','BRL',{'status':'USER_REPORTED_PREVIEWS_READ','records':[self.row]});self.assertEqual(r['legs'][0]['status'],'EXACT_AMOUNT_REPORTED_PREVIEW_NOT_CURRENT_QUOTE');self.assertFalse(r['current_execution_quote_proven'])
 def test_no_extrapolation_to_other_notional(self):
  r=attach(self.scenario('500'),'account','BRL',{'status':'USER_REPORTED_PREVIEWS_READ','records':[self.row]});self.assertEqual(r['legs'][0]['status'],'REPORTED_PREVIEW_NOTIONAL_DIFFERS')
 def test_currency_and_account_isolation(self):
  for account,currency in [('other','BRL'),('account','EUR')]:
   r=attach(self.scenario(currency=currency),account,currency,{'status':'USER_REPORTED_PREVIEWS_READ','records':[self.row]});self.assertFalse(r['legs'][0]['observations'])
 def test_tamper_refused(self):
  with tempfile.TemporaryDirectory() as d:
   record(d,self.row);p=next((Path(d)/'data/reported_pretrade_previews_a24').glob('*.json'));r=json.loads(p.read_text());r['explicit_commission']='3';p.write_text(json.dumps(r));self.assertEqual(inspect(d)['status'],'PREVIEW_RECORDS_UNAVAILABLE')
 def test_negative_and_zero_quantity_refused(self):
  for amount,quantity in [('-1','2'),('100','0')]:
   with self.assertRaises(ValueError):seal('account','asset','BRL',amount,'0','100',quantity,now=datetime.datetime.now(datetime.timezone.utc))
if __name__=='__main__':unittest.main()
