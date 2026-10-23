import sys,copy
sys.path.insert(0,'/workspace/porquinho-a24/project')
from universal_portfolio.cash_documentary_cost_projection_a24 import project
s=dict(plan_id='p',budget_id='b',candidate_id='c',policy_version_digest='v',horizon_unit='OBSERVATIONS',horizon_value=30,cash_fraction_numerator=1,cash_fraction_denominator=2,legs=[dict(instrument_id='i',quote_currency='BRL',fraction_numerator=1,fraction_denominator=2)],common_research_unit=dict(reference_capital='5000',currency='BRL',expected_gross_change='200',horizon_unit='OBSERVATIONS',horizon_value=30))
a={k:s[k] for k in ('plan_id','budget_id','candidate_id','policy_version_digest')};a.update(status='EXISTING_RESEARCH_EVIDENCE_RECONCILED_NOT_A_FINAL_SUGGESTION',account_id='acct',currency='BRL',reference_capital='5000',expected_gross_change='200')
v=dict(status='ACTION_COST_REFERENCES_PROJECTED',execution_authorized=False,rows=[dict(status='PARTIAL_DOCUMENTARY_REFERENCES',account_id='acct',currency='BRL',instrument_id='i',side='BUY',bank_components={'brokerage':dict(amount='0',currency='BRL',status='DOCUMENTED_REFERENCE_NOT_PRETRADE_QUOTE',source_url='https://bank')},exchange_hypotheses=[dict(variant_id='continuous',total_rate_pct='0.03',source_url='https://exchange',conditions={'session':'CONTINUOUS'}),dict(variant_id='auction',total_rate_pct='0.032',source_url='https://exchange',conditions={'session':'AUCTION'})])])
before=copy.deepcopy((s,a,v));r=project(s,'BRL',a,'acct',v);assert r['status']=='SCENARIO_DOCUMENTARY_COMPONENTS_PROJECTED',r
assert [x['documented_component_subtotal'] for x in r['variants']]==['0.75','0.800'];assert r['variants'][0]['reference_purchase_debit']=='2500.75';assert r['variants'][0]['net_change'] is None;assert (s,a,v)==before
for mutate in ('currency','capital','fraction','ambiguity','unknown'):
 ss,aa,vv=copy.deepcopy((s,a,v))
 if mutate=='currency':aa['currency']='EUR'
 if mutate=='capital':aa['reference_capital']='6000'
 if mutate=='fraction':ss['legs'][0]['fraction_numerator']=2
 if mutate=='ambiguity':vv['rows'][0]['status']='AMBIGUOUS_LEG_REFERENCES'
 if mutate=='unknown':vv['rows'][0]['bank_components']={}
 assert not project(ss,'BRL',aa,'acct',vv)['variants'],mutate
print('SCENARIO_FRACTIONS_COSTS_AND_REFUSALS_OK')
