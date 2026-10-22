import copy,datetime as dt,json,unittest
from pathlib import Path
from decimal import Decimal
from universal_portfolio.exchange_fee_reference_a24 import calculate,project,INPUT_SCHEMA
NOW=dt.datetime(2026,10,22,23,tzinfo=dt.timezone.utc)
class Reference(unittest.TestCase):
 def setUp(self):
  self.p=json.loads((Path(__file__).resolve().parents[1]/'config/official_exchange_fee_policies_a24.json').read_text())['policies'][0]
  self.i={'instrument_id':'EXPLICIT:SYNTHETIC','market':'B3','currency':'BRL','asset_class':'EQUITY'}
 def quote(self,notional='5000',side='BUY'):return calculate(self.p,self.i,'BRL',side,notional,now=NOW)
 def test_known_per_side_components_and_total(self):
  h=self.quote()['hypotheses'][0];self.assertEqual(Decimal(h['total_rate_pct']),Decimal('.0300'));self.assertEqual(Decimal(h['unrounded_reference_amount']),Decimal('1.50'));self.assertEqual(Decimal(h['components']['trading']['unrounded_reference_amount']),Decimal('.25'));self.assertEqual(Decimal(h['components']['ccp']['unrounded_reference_amount']),Decimal('1.12'));self.assertEqual(Decimal(h['components']['asset_transfer']['unrounded_reference_amount']),Decimal('.13'))
 def test_auction_is_separate_not_added_to_regular(self):
  h=self.quote()['hypotheses'][1];self.assertEqual(Decimal(h['total_rate_pct']),Decimal('.0320'));self.assertEqual(Decimal(h['unrounded_reference_amount']),Decimal('1.60'))
 def test_fee_applies_each_side_without_assuming_equal_sale_proceeds(self):
  self.assertEqual(self.quote(side='SELL')['hypotheses'][0]['unrounded_reference_amount'],self.quote(side='BUY')['hypotheses'][0]['unrounded_reference_amount']);self.assertIsNone(self.quote()['total_cost'])
 def test_zero_profile_not_inferred_from_notional(self):
  r=self.quote('1');self.assertFalse(r['trade_profile_assumed']);self.assertFalse(r['hypotheses'][0]['conditions_verified_for_account']);self.assertEqual(r['hypotheses'][0]['conditions']['monthly_adtv_until'],'3000000')
 def test_missing_notional_keeps_rates_not_zero_amount(self):
  r=self.quote(None);self.assertIsNone(r['hypotheses'][0]['unrounded_reference_amount']);self.assertEqual(r['status'],'EXCHANGE_RATES_REQUIRE_RESEARCH_NOTIONAL')
 def test_monthly_adjustment_not_added_per_order(self):
  self.p['variants'][0]['monthly_band_adjustment']='225'
  with self.assertRaisesRegex(ValueError,'MONTHLY_ALLOCATION_FORMULA_REQUIRED'):self.quote()
 def test_scope_not_inferred_from_symbol(self):
  del self.i['market'];self.assertEqual(self.quote()['hypotheses'],[])
 def test_other_market_currency_crypto_refused(self):
  for k,v in [('market','OTHER'),('currency','EUR'),('asset_class','CRYPTO')]:
   old=self.i[k];self.i[k]=v;self.assertEqual(self.quote()['hypotheses'],[]);self.i[k]=old
 def test_no_extra_tax_added_to_inclusive_exchange_rate(self):
  h=self.quote()['hypotheses'][0];self.assertTrue(h['tariff_formation_taxes_already_included']);self.assertFalse(h['investment_capital_gains_tax_included']);self.assertFalse(h['spread_or_slippage_included'])
 def test_expired_source_does_not_compute(self):
  self.p['source']['review_until']='2026-10-21T00:00:00Z';self.assertEqual(self.quote()['hypotheses'],[])
 def test_candidates_and_models_preserved(self):
  before=copy.deepcopy((self.p,self.i));self.quote();self.assertEqual(before,(self.p,self.i))
 def test_cash_budget_is_reference_not_order(self):
  plan={'schema':'porquinho.economic-action-plan-a24/1.0','status':'ACTION_CONTEXTS_PROJECTED_NOT_COMPARATOR_READY','execution_authorized':False,'cases':[{'case_id':'case','resource_kind':'CASH','account_id':'a','currency':'BRL','capital_ceiling':'5000'}]}
  evidence={'schema':'porquinho.economic-action-evidence-a24/1.0','execution_authorized':False,'alternatives':[{'case_id':'case','alternative_id':'alt','account_id':'a','currency':'BRL','legs':[{'account_id':'a','currency':'BRL','instrument_id':self.i['instrument_id'],'side':'BUY'}]}]}
  r=project(plan,evidence,[self.i],{'schema':INPUT_SCHEMA,'policies':[self.p]},now=NOW);self.assertEqual(len(r['legs']),1);self.assertFalse(r['reference_capital_is_order_amount']);self.assertFalse(r['recommendation_created']);self.assertEqual(Decimal(r['legs'][0]['hypotheses'][0]['unrounded_reference_amount']),Decimal('1.50'))
if __name__=='__main__':unittest.main()
