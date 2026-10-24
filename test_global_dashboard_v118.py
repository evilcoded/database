import ast,copy,datetime as dt,json,random,tempfile,unittest
from pathlib import Path
from universal_portfolio.global_dashboard_observations_a24 import summaries,capture,read,STORE
from universal_portfolio import global_action_readings_a24 as rules
from universal_portfolio.universal_action_rules_a24 import action

NOW=dt.datetime(2026,10,24,8,tzinfo=dt.timezone.utc)
CFG={'buy_min_promising':75,'buy_min_entry':70,'buy_max_risk':50,'sell_structural_risk':75,'sell_max_promising':50,'hold_min_promising':65,'hold_max_risk':60,'realize_min_pnl_pct':8,'realize_max_promising':65,'realize_reversal_risk':65,'realize_min_asymmetry':45,'realize_risk':60}

def cockpit():
    return {'execution_authorized':False,'financial_mutation':False,'positions':[
      {'instrument_id':'TEST:MKT:CRYPTO:ASSET','account_id':'BR_ACCOUNT','currency':'BRL','quantity':'1','cost_basis':'500','reference_market_value':'485','reference_pnl':'-15','reference_pnl_pct':'-3','reference_quote_at':NOW.isoformat(),'reference_provider':'TEST_PROVIDER','reference_provider_id':'asset','context_status':'EXACT_REGISTERED_CONTEXT'},
      {'instrument_id':'TEST:MKT:FIXED:UNKNOWN','account_id':'OTHER_BR_ACCOUNT','currency':'BRL','quantity':'1','cost_basis':'3000','reference_market_value':None,'reference_pnl':None,'context_status':'EXACT_REGISTERED_CONTEXT'},
      {'instrument_id':'TEST:MKT:CRYPTO:ASSET','account_id':'EU_ACCOUNT','currency':'EUR','quantity':'1','cost_basis':'100','reference_market_value':'82','reference_pnl':'-18','reference_pnl_pct':'-18','reference_quote_at':NOW.isoformat(),'reference_provider':'TEST_PROVIDER','reference_provider_id':'asset','context_status':'EXACT_REGISTERED_CONTEXT'}],
      'cash':[{'account_id':'BR_ACCOUNT','currency':'BRL','amount':'4500','context_status':'EXACT_REGISTERED_CONTEXT'},{'account_id':'EU_ACCOUNT','currency':'EUR','amount':'10','context_status':'EXACT_REGISTERED_CONTEXT'}]}

def metrics(q='BRL',risk=35,score=67):
    return {'metric_contract':'porquinho.standard-action-metrics/1.0','metric_unit':'INDEX_0_100','provider':'TEST_PROVIDER','provider_id':'asset','quote_currency':q,'quote_observed_at':NOW.timestamp(),'quote_freshness':'FRESH_API','asset':'ASSET','promising_pct':score,'entry':72,'risk':risk,'asymmetry':80,'reversal_risk':30}

class Dashboard(unittest.TestCase):
    def test_partial_brl_pnl_not_hidden_or_mixed_with_eur(self):
        rows=summaries(cockpit(),NOW);br=next(r for r in rows if r['currency']=='BRL' and r['account_id'] is None)
        eu=next(r for r in rows if r['currency']=='EUR' and r['account_id'] is None)
        self.assertEqual(br['pnl'],'-15');self.assertFalse(br['pnl_complete']);self.assertEqual(br['value'],'4985');self.assertEqual(br['pnl_position_count'],1);self.assertEqual(br['position_count'],2)
        self.assertEqual(eu['pnl'],'-18');self.assertEqual(eu['value'],'92')
    def test_unknown_price_never_book_cost_or_zero_pnl(self):
        r=next(r for r in summaries(cockpit(),NOW) if r['account_id']=='OTHER_BR_ACCOUNT')
        self.assertIsNone(r['pnl']);self.assertIsNone(r['value'])
    def test_stale_or_prepurchase_quote_not_counted(self):
        for field,value in [('reference_quote_at',(NOW-dt.timedelta(hours=2)).isoformat()),('reference_not_before',(NOW+dt.timedelta(minutes=1)).isoformat())]:
            c=cockpit();c['positions'][0][field]=value
            br=next(r for r in summaries(c,NOW) if r['account_id']=='BR_ACCOUNT')
            self.assertIsNone(br['pnl']);self.assertEqual(br['value'],'4500')
    def test_journal_observations_not_historical_reconstruction(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);c=cockpit();before=copy.deepcopy(c)
            capture(root,c,now=NOW,revalidate=lambda:c)
            result=read(root,NOW+dt.timedelta(seconds=1));br=next(s for s in result['series'] if s['currency']=='BRL' and s['account_id'] is None)
            self.assertEqual(len(br['points']),1);self.assertEqual(br['points'][0]['value'],'4985');self.assertFalse(result['backfill_performed']);self.assertEqual(c,before)
    def test_context_change_prevents_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            c=cockpit();changed=copy.deepcopy(c);changed['cash'][0]['amount']='4000'
            result=capture(Path(tmp),c,now=NOW,revalidate=lambda:changed)
            self.assertFalse(result['recorded']);self.assertFalse(list(Path(tmp).rglob('*.jsonl')))
    def test_same_population_pnl_change_and_deposit_not_profit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);c=cockpit();capture(root,c,now=NOW,revalidate=lambda:c)
            c['cash'][0]['amount']='5500';later=NOW+dt.timedelta(minutes=10);capture(root,c,now=later,revalidate=lambda:c)
            result=read(root,later);delta=next(r for r in result['changes'] if r['currency']=='BRL' and r['account_id'] is None)
            self.assertEqual(delta['value'],'0');self.assertEqual(delta['interval_seconds'],600)
    def test_purchase_population_change_not_pnl_performance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);c=cockpit();capture(root,c,now=NOW,revalidate=lambda:c)
            c['positions'][0]['quantity']='2';later=NOW+dt.timedelta(minutes=10);capture(root,c,now=later,revalidate=lambda:c)
            self.assertFalse([r for r in read(root,later)['changes'] if r['currency']=='BRL' and r['account_id'] is None])
    def test_get_reader_has_no_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);before=list(root.rglob('*'));read(root,NOW);self.assertEqual(list(root.rglob('*')),before)
    def test_corrupt_or_partial_journal_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/STORE/'2026-10-24.jsonl';p.parent.mkdir(parents=True);p.write_text('{partial')
            self.assertEqual(read(root,NOW)['series'],[])
    def test_provider_and_currency_do_not_change_rule(self):
        for provider,q in [('PROVIDER_ONE','BRL'),('PROVIDER_TWO','EUR')]:
            c=cockpit();m=metrics(q,risk=80)
            for p in c['positions']:
                if p['currency']==q:p['reference_provider']=provider
            m['provider']=provider
            out=rules.project(c,{'scores':[m]},CFG,now=NOW)
            selected=[r for r in out['rows'] if r['currency']==q and r['instrument_id']=='TEST:MKT:CRYPTO:ASSET']
            self.assertEqual(selected[0]['action'],'VENDA')
    def test_loss_eighteen_percent_not_new_stop_loss(self):
        c=cockpit();out=rules.project(c,{'scores':[metrics('EUR',35,67)]},CFG,now=NOW)
        eu=next(r for r in out['rows'] if r['currency']=='EUR')
        self.assertEqual(eu['action'],'MANTENHA');self.assertEqual(eu['position_pnl_pct'],'-18');self.assertFalse(eu['loss_stop_configured'])
    def test_eur_metrics_not_used_as_brl(self):
        out=rules.project(cockpit(),{'scores':[metrics('EUR')]},CFG,now=NOW)
        self.assertIsNone(next(r for r in out['rows'] if r['account_id']=='BR_ACCOUNT')['action'])
    def test_fractional_risk_not_mislabelled_index(self):
        m=metrics();m['metric_unit']='RETURN_FRACTION'
        out=rules.project(cockpit(),{'scores':[m]},CFG,now=NOW)
        self.assertTrue(all(r['action'] is None for r in out['rows']))
    def test_panels_integrate_global_finance_and_rules_read_only(self):
        from universal_portfolio.experience_panels_a24 import build
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'results').mkdir()
            (root/'config.json').write_text(json.dumps({'action_rules':CFG}))
            (root/'results/latest.json').write_text(json.dumps({'scores':[metrics('EUR')]}))
            before={str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            result=build(root,now=NOW,cockpit=cockpit(),funding={})
            self.assertTrue(result['global_finance']['current']);self.assertEqual(len(result['global_rule_readings']['rows']),3)
            self.assertFalse([x for x in result['issues'] if x.startswith('global_finance:')]);self.assertEqual(before,{str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()})
    def test_goal_keeps_existing_horizon_and_cash_is_not_order_amount(self):
        from unittest.mock import patch
        from universal_portfolio.global_goal_preview_a24 import build
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);policy=root/'policy.json';policy.write_text('{}')
            source={('VERSION','CANDIDATE'):{'research':{'quote_currency':'BRL','horizon_unit':'OBSERVATIONS','horizon_value':30},'nominal_cash_zero_return_projection_pct':'2','current_cash_fraction':'0/1','candidate':{'current_forecast_origin':'2026-10-24'}}}
            demand={'contexts':[{'account_id':'BR_ACCOUNT','currency':'BRL','context_fingerprint':'CURRENT'}]}
            with patch('brain.evolution.learned_allocation_policy_a24.work',return_value=(None,[{'path':policy,'pairs':[]}])),patch('brain.evolution.learned_allocation_policy_a24.check_stored',return_value={}),patch('universal_portfolio.global_history_source_a24.read_sealed',return_value={}),patch('universal_portfolio.learned_policy_economic_basis_a24.candidate_data',return_value=source):
                result=build(root,demand,cockpit(),now=NOW)
            self.assertEqual(len(result),1);r=result[0]
            self.assertEqual(r['horizon_value'],30);self.assertEqual(r['horizon_unit'],'OBSERVATIONS');self.assertEqual(r['projected_asset_gross_change'],'90')
            self.assertFalse(r['reference_cash_is_order_amount']);self.assertFalse(r['cash_yield_assumed_zero']);self.assertEqual(policy.read_text(),'{}')
    def test_rule_parity_with_original_code(self):
        baseline="def action(s, invested, pnl_pct=0.0):\n    r = CFG['action_rules']\n    if not invested:\n        if s['promising_pct'] >= r['buy_min_promising'] and s['entry'] >= r['buy_min_entry'] and (s['risk'] <= r['buy_max_risk']):\n            return 'COMPRE'\n        return 'ACOMPANHE'\n    if s['risk'] >= r['sell_structural_risk']:\n        return 'VENDA'\n    if s['promising_pct'] < r['sell_max_promising'] and prior_daily_sell_confirmed(s['asset']):\n        return 'VENDA'\n    realize_min = float(r.get('realize_min_pnl_pct', 8.0))\n    if pnl_pct >= realize_min and (s['promising_pct'] < r.get('realize_max_promising', 65) or s['reversal_risk'] >= r.get('realize_reversal_risk', 65) or s['asymmetry'] < r.get('realize_min_asymmetry', 45) or (s['risk'] > r.get('realize_risk', 60))):\n        return 'REALIZE'\n    if s['promising_pct'] >= r['hold_min_promising'] and s['risk'] <= r['hold_max_risk']:\n        return 'MANTENHA'\n    return 'ACOMPANHE'";tree=ast.parse(baseline)
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='action')
        namespace={'CFG':{'action_rules':CFG},'prior_daily_sell_confirmed':lambda _:True}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'original_action','exec'),namespace)
        random.seed(118)
        for _ in range(500):
            m={k:random.uniform(0,100) for k in ('promising_pct','entry','risk','reversal_risk','asymmetry')};m['asset']='SYNTHETIC'
            held=random.choice([True,False]);pnl=random.uniform(-50,50)
            self.assertEqual(action(m,held,pnl,rules=CFG,prior_daily_sell_confirmed=lambda _:True),namespace['action'](m,held,pnl))

if __name__=='__main__':unittest.main()
