import copy,datetime as dt,unittest
from universal_portfolio import capital_protection_review_a24 as review
from universal_portfolio import global_action_readings_a24 as readings
import test_operational_plan_v137 as fixture
NOW=fixture.NOW

class Protection(unittest.TestCase):
    def position(self,**kw):
        return {'instrument_id':'ETH','account_id':'A','currency':'EUR','context_status':'EXACT_REGISTERED_CONTEXT',
            'reference_provider':'CoinGecko','reference_provider_id':'ethereum','cost_basis':'100','reference_market_value':'81',
            'reference_pnl':'-19','reference_pnl_pct':'-19','reference_quote_at':NOW.isoformat(),**kw}
    def check(self,p=None,score=60,risk=40):
        p=p or self.position();m=fixture.metric(i='ethereum',q=p['currency'],score=score,risk=risk,provider='CoinGecko',quote_observed_at=NOW.isoformat())
        before=copy.deepcopy((p,m));r=readings.project({'positions':[p]},{'scores':[m]},fixture.CFG['action_rules'],now=NOW)
        out=review.build({'positions':[p]},r,now=NOW)
        self.assertEqual(before,(p,m));return out,r
    def test_nineteen_percent_loss_gets_review_without_forced_sell_or_hold(self):
        out,r=self.check();row=out['rows'][0]
        self.assertEqual(r['rows'][0]['action'],'ACOMPANHE');self.assertEqual(row['selected_action'],'ACOMPANHE')
        self.assertTrue(row['alert']);self.assertEqual(row['suggested_review'],'REVISAR_PROTECAO_DO_CAPITAL')
        self.assertAlmostEqual(float(row['recovery_to_recorded_cost_pct']),23.4567901234)
        self.assertFalse(row['loss_is_automatic_sell_trigger']);self.assertFalse(row['sell_risk_condition']['matched'])
        self.assertFalse(out['action_rules_modified']);self.assertFalse(row['execution_authorized'])
    def test_loss_does_not_hide_real_hold_or_sell_and_reports_actual_criteria(self):
        hold,_=self.check(score=70,risk=40);self.assertEqual(hold['rows'][0]['selected_action'],'MANTENHA');self.assertTrue(hold['rows'][0]['alert'])
        sell,_=self.check(score=45,risk=80);self.assertEqual(sell['rows'][0]['selected_action'],'VENDA');self.assertTrue(sell['rows'][0]['sell_risk_condition']['matched'])
    def test_alert_is_global_and_applies_to_any_verified_loss_not_new_percent_gate(self):
        for q in ('EUR','BRL','JPY'):
            for value in ('99.99','81','1','0'):
                out,_=self.check(self.position(currency=q,reference_market_value=value,reference_pnl=str(float(value)-100)))
                self.assertTrue(out['rows'][0]['alert']);self.assertEqual(out['rows'][0]['currency'],q)
        self.assertIsNone(out['rows'][0]['recovery_to_recorded_cost_pct'])
    def test_profit_break_even_and_no_cost_do_not_generate_loss_alert(self):
        for value in ('100','120'):
            out,_=self.check(self.position(reference_market_value=value,reference_pnl=str(int(value)-100)))
            self.assertFalse(out['rows'][0]['alert'])
        out,_=self.check(self.position(cost_basis=None));self.assertFalse(out['rows'][0]['alert']);self.assertEqual(out['pending_count'],1)
    def test_stale_unresolved_future_and_pre_purchase_quotes_are_pending(self):
        for fields in ({'reference_quote_at':(NOW-dt.timedelta(hours=1)).isoformat()}, {'context_status':'UNRESOLVED'}, {'reference_quote_at':(NOW+dt.timedelta(minutes=1)).isoformat()}, {'reference_not_before':(NOW+dt.timedelta(minutes=1)).isoformat()}):
            out,_=self.check(self.position(**fields));self.assertFalse(out['rows'][0]['alert']);self.assertEqual(out['pending_count'],1)
    def test_conflicting_recorded_pnl_is_not_reported_as_valid_current_alert(self):
        out,_=self.check(self.position(reference_pnl='-80'));self.assertEqual(out['rows'][0]['status'],'POSITION_PNL_RECONCILIATION_REQUIRED')
    def test_current_loss_alert_remains_visible_without_current_action_metrics(self):
        p=self.position();out=review.build({'positions':[p]},{'rows':[]},now=NOW)
        self.assertTrue(out['rows'][0]['alert']);self.assertIsNone(out['rows'][0]['selected_action'])
        self.assertFalse(out['rows'][0]['current_rule_evaluation_available'])

if __name__=='__main__':unittest.main()
