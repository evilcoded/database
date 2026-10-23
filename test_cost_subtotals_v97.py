import sys,copy
sys.path.insert(0,'/workspace/porquinho-a24/project')
from universal_portfolio.action_cost_visibility_a24 import component_calculations
row=dict(status='PARTIAL_DOCUMENTARY_REFERENCES',alternative_id='a',account_id='x',currency='BRL',instrument_id='i',side='BUY',bank_components={'brokerage':dict(status='DOCUMENTED_REFERENCE_NOT_PRETRADE_QUOTE',currency='BRL',amount='0')},exchange_hypotheses=[dict(variant_id='continuous',reference_capital='5000',unrounded_reference_amount='1.50'),dict(variant_id='auction',reference_capital='5000',unrounded_reference_amount='1.60')])
before=copy.deepcopy(row);out=component_calculations([row]);assert [x['documented_component_subtotal'] for x in out]==['1.50','1.60'];assert all(x['total_cost'] is None for x in out);assert row==before
for field,value in [('reference_capital',None),('unrounded_reference_amount','NaN')]:
 x=copy.deepcopy(row);x['exchange_hypotheses'][0][field]=value;assert component_calculations([x])[0]['documented_component_subtotal'] is None
x=copy.deepcopy(row);x['bank_components']['brokerage']['currency']='EUR';assert component_calculations([x])[0]['documented_component_subtotal'] is None
x=copy.deepcopy(row);x['status']='AMBIGUOUS_LEG_REFERENCES';assert component_calculations([x])==[]
print('PARTIAL_COST_CALCULATIONS_OK')
