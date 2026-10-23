import unittest,sys,copy,json,datetime
from pathlib import Path
from fractions import Fraction
sys.path.insert(0,'/workspace/porquinho-a24/project')
from universal_portfolio.conditional_reference_budget_fit_a24 import fit,display
from universal_portfolio.route_documentary_cost_a24 import project
class Tests(unittest.TestCase):
 def make(self,capital='100',weights=(Fraction(1),),cash=Fraction(0)):
  s={'common_research_unit':{'currency':'EUR','reference_capital':capital,'horizon_unit':'OBSERVATIONS','horizon_value':30},'horizon_unit':'OBSERVATIONS','horizon_value':30,'cash_fraction_numerator':cash.numerator,'cash_fraction_denominator':cash.denominator,'legs':[dict(instrument_id=str(i),quote_currency='EUR',fraction_numerator=w.numerator,fraction_denominator=w.denominator) for i,w in enumerate(weights)]}
  p={'status':'ROUTE_DOCUMENTARY_COMPONENTS_PROJECTED','execution_authorized':False,'currency':'EUR','reference_capital':capital,'horizon_unit':'OBSERVATIONS','horizon_value':30,'legs':[dict(instrument_id=str(i),currency='EUR',side='BUY',status='DOCUMENTED_ROUTE_COMMISSION_COMPUTED',rounding='CEILING_CURRENCY_QUANTUM',reference_notional=display(Fraction(capital)*w),rate_pct='1.5',currency_quantum='0.01') for i,w in enumerate(weights)]}
  return s,p
 def test_fee_inclusive_common_base(self):
  s,p=self.make();before=copy.deepcopy((s,p));r=fit(s,p);self.assertEqual(r['common_reference_base'],'98.52');self.assertEqual(r['documented_commission_total'],'1.48');self.assertEqual(r['reference_purchase_debit'],'100');self.assertFalse(r['complete_budget_feasibility_proven']);self.assertIsNone(r['unknown_cost_allowance']);self.assertEqual((s,p),before)
 def test_small_budget_cent_ceiling(self):
  s,p=self.make('1');r=fit(s,p);self.assertEqual(r['common_reference_base'],'0.98');self.assertEqual(r['documented_commission_total'],'0.02')
 def test_original_cash_fraction_preserved(self):
  s,p=self.make(weights=(Fraction(1,2),),cash=Fraction(1,2));r=fit(s,p);self.assertEqual(r['preserved_cash_reference'],'50');self.assertLessEqual(Fraction(r['reference_purchase_debit'])+50,100)
 def test_multileg_preserves_exact_ratio(self):
  s,p=self.make(weights=(Fraction(1,3),Fraction(2,3)));r=fit(s,p);self.assertEqual(r['status'],'CONDITIONAL_REFERENCE_BUDGET_FIT_COMPUTED');amounts=[Fraction(l['reference_notional_exact']['numerator'],l['reference_notional_exact']['denominator']) for l in r['legs']];self.assertEqual(amounts[1]/amounts[0],2);self.assertTrue(r['maximal_on_common_base_grid'])
 def test_unknown_tariff_refuses(self):
  s,p=self.make();p['legs'][0]['status']='ROUTE_PRETRADE_QUOTE_REQUIRED';self.assertNotEqual(fit(s,p)['status'],'CONDITIONAL_REFERENCE_BUDGET_FIT_COMPUTED')
 def test_very_small_budget_no_positive_scale(self):
  s,p=self.make('.01');self.assertEqual(fit(s,p)['status'],'NO_POSITIVE_REFERENCE_SCALE_WITH_DOCUMENTED_FEES')
 def test_mismatch_refuses(self):
  for key,value in [('currency','BRL'),('reference_capital','200'),('horizon_value',60)]:
   s,p=self.make();p[key]=value;self.assertNotEqual(fit(s,p)['status'],'CONDITIONAL_REFERENCE_BUDGET_FIT_COMPUTED')
 def test_exact_notional_mismatch(self):
  s,p=self.make();p['legs'][0]['reference_notional']='50';self.assertEqual(fit(s,p)['status'],'EXACT_LEG_NOTIONAL_REQUIRED')
 def test_no_duplicate_leg(self):
  s,p=self.make(weights=(Fraction(1,2),Fraction(1,2)));s['legs'][1]['instrument_id']='0';self.assertNotEqual(fit(s,p)['status'],'CONDITIONAL_REFERENCE_BUDGET_FIT_COMPUTED')
if __name__=='__main__':unittest.main()
