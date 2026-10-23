const assert=require('assert');let values={};const document={getElementById:id=>id==='modalBody'?{querySelector:selector=>values[selector.slice(1)]}:null};let R21386LS19A={accountId:'account'};let r21386ls19aPayload;

/* V105: validate the existing manual-trade form; zero fee is valid, missing is not zero. */
r21386ls19aPayload=function(){
 const body=document.getElementById('modalBody');
 const field=id=>body?.querySelector('#'+id)||document.getElementById(id);
 const text=(id,label)=>{const el=field(id);if(!el)throw Error(label+': campo não encontrado no formulário ativo.');if(el.validity?.badInput)throw Error(label+': o navegador não reconheceu o valor. Redigite usando o separador decimal aceito pelo campo.');const raw=String(el.value??'').trim();if(!raw)throw Error(label+': preenchimento obrigatório.');return raw;};
 const decimal=(id,label,allowZero=false)=>{
  let raw=text(id,label);
  if(raw.includes(',')){if(raw.includes('.')||(raw.match(/,/g)||[]).length!==1)throw Error(label+': use apenas um separador decimal e nenhum separador de milhares.');raw=raw.replace(',','.');}
  if(raw.length>80||!/^\+?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(raw))throw Error(label+': informe um número decimal válido, sem símbolo de moeda.');
  const value=Number(raw);if(!Number.isFinite(value)||(allowZero?value<0:value<=0))throw Error(label+(allowZero?': informe zero ou um valor positivo.':': informe um valor positivo.'));
  return {raw,value};
 };
 const instrument_id=text('r21386ls19aInstrument','Instrumento'),quantity=decimal('r21386ls19aQty','Quantidade'),price=decimal('r21386ls19aPrice','Preço unitário'),gross=decimal('r21386ls19aGross','Total'),currency=text('r21386ls19aCurrency','Moeda'),executed=text('r21386ls19aExecuted','Data/hora'),fee=decimal('r21386ls19aFee','Taxa',true),funding=text('r21386ls19aFunding','Origem dos recursos');
 if(!R21386LS19A.accountId)throw Error('Conta: contexto do formulário indisponível. Reabra o registro pela conta correta.');
 const date=new Date(executed);if(!Number.isFinite(date.getTime()))throw Error('Data/hora: informe uma data e hora válidas no campo.');
 const product=quantity.value*price.value;
 if(!Number.isFinite(product))throw Error('Quantidade × preço: resultado fora do intervalo numérico aceito.');
 if(Math.abs(product-gross.value)>Math.max(.01,Math.abs(gross.value)*.000001)){
  const format=v=>v.toLocaleString('pt-PT',{minimumFractionDigits:2,maximumFractionDigits:8});
  throw Error('Quantidade × preço = '+format(product)+' '+currency+', diferente do total '+format(gross.value)+' '+currency+'. Confira os dados da operação; a taxa é informada separadamente.');
 }
 return {transaction_type:'BUY',funding_source:funding,account_id:R21386LS19A.accountId,instrument_id,transaction_currency:currency,quantity:quantity.raw,unit_price:price.raw,gross_amount:gross.raw,executed_at:date.toISOString(),fee_amount:fee.raw,fee_currency:currency,funding_details:{source:'MANUAL_UI'}};
};

function fill(){values={};for(const [k,v] of Object.entries({Instrument:'asset',Qty:'2',Price:'50',Gross:'100',Currency:'BRL',Executed:'2026-10-23T11:22',Fee:'0',Funding:'REGISTERED_ACCOUNT_CASH'}))values['r21386ls19a'+k]={value:v,validity:{badInput:false}};}
fill();assert.equal(r21386ls19aPayload().fee_amount,'0');values.r21386ls19aFee.value='00';assert.equal(Number(r21386ls19aPayload().fee_amount),0);
for(const k of ['Qty','Price','Gross','Fee','Executed']){fill();values['r21386ls19a'+k].value='';assert.throws(()=>r21386ls19aPayload(),/obrigatório/);}
fill();values.r21386ls19aQty.validity.badInput=true;assert.throws(()=>r21386ls19aPayload(),/Quantidade: o navegador/);
fill();values.r21386ls19aQty.value='0.93570696';values.r21386ls19aPrice.value='534.12';values.r21386ls19aGross.value='500.00';assert.throws(()=>r21386ls19aPayload(),/Quantidade × preço.*diferente do total/);
fill();values.r21386ls19aQty.value='2,0';assert.equal(r21386ls19aPayload().quantity,'2.0');
fill();values.r21386ls19aQty.value='1.000,50';assert.throws(()=>r21386ls19aPayload(),/separador/);
fill();values.r21386ls19aFee.value='-1';assert.throws(()=>r21386ls19aPayload());
fill();values.r21386ls19aQty.value='0.000000010000000001';values.r21386ls19aPrice.value='100000000';values.r21386ls19aGross.value='1.0000000001';assert.equal(r21386ls19aPayload().quantity,'0.000000010000000001');
fill();values.r21386ls19aExecuted.value='bad-date';assert.throws(()=>r21386ls19aPayload(),/Data.hora/);
console.log('ZERO_FEE_ACTIVE_FIELDS_DECIMAL_PRESERVATION_AND_SPECIFIC_ERRORS_OK');
