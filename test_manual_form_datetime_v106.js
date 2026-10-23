const assert=require('assert');let body={},field={value:'2026-10-23T11:29:00+01:00'};const document={getElementById:id=>id==='modalBody'?{querySelector:()=>field}:field};let r21386ls19aOpenManualTrade=async()=>{};let r21386ls19aPayload=()=>({executed_at:field.value});

/* V106: explicit timezone input in the same manual-investment form; no native date control. */
function v106ExecutedAt(raw){
 const value=String(raw??'').trim();
 const m=/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,3}))?)?(Z|[+-]\d{2}:\d{2})$/.exec(value);
 if(!m)throw Error('Data/hora: use AAAA-MM-DDTHH:mm:ss com fuso, por exemplo 2026-01-15T10:30:00-03:00.');
 const [year,month,day,hour,minute,second]=[m[1],m[2],m[3],m[4],m[5],m[6]||'0'].map(Number);
 const calendar=new Date(0);calendar.setUTCFullYear(year,month-1,day);calendar.setUTCHours(hour,minute,second,0);
 if(year<1||calendar.getUTCFullYear()!==year||calendar.getUTCMonth()!==month-1||calendar.getUTCDate()!==day||hour>23||minute>59||second>59)throw Error('Data/hora: data ou hora inexistente.');
 const zone=m[8];
 if(zone!=='Z'){
  const hours=Number(zone.slice(1,3)),minutes=Number(zone.slice(4,6));
  if(hours>14||minutes>59||(hours===14&&minutes!==0)||zone==='-00:00')throw Error('Data/hora: informe um fuso UTC válido e conhecido.');
 }
 const date=new Date(value);if(!Number.isFinite(date.getTime()))throw Error('Data/hora: valor não reconhecido.');
 return date.toISOString();
}
const v106OriginalManualTradeOpen=r21386ls19aOpenManualTrade;
r21386ls19aOpenManualTrade=async function(...args){
 await v106OriginalManualTradeOpen(...args);
 const body=document.getElementById('modalBody');if(!body)return;
 const field=body.querySelector('#r21386ls19aExecuted');
 if(field){field.type='text';field.placeholder='AAAA-MM-DDTHH:mm:ss+HH:mm';field.setAttribute('autocomplete','off');field.setAttribute('aria-label','Data e hora executadas com fuso UTC explícito');const label=field.closest('label');if(label&&label.firstChild?.nodeType===3)label.firstChild.textContent='Data/hora da operação (com fuso)';
 const hint=document.createElement('small');hint.textContent='Informe o horário e o fuso do comprovante. Não será usada a data atual automaticamente.';field.insertAdjacentElement('afterend',hint);}
 const select=body.querySelector('#r21386ls19aInstrument');
 if(select){const placeholder=document.createElement('option');placeholder.value='';placeholder.textContent='Selecione o instrumento comprado';placeholder.disabled=true;placeholder.selected=true;select.insertBefore(placeholder,select.firstChild);select.value='';}
};
const v106OriginalManualTradePayload=r21386ls19aPayload;
r21386ls19aPayload=function(){
 const body=document.getElementById('modalBody'),field=body?.querySelector('#r21386ls19aExecuted')||document.getElementById('r21386ls19aExecuted');
 if(!field)throw Error('Data/hora: campo não encontrado no formulário ativo.');
 const raw=field.value,iso=v106ExecutedAt(raw);
 try{field.value=iso;return v106OriginalManualTradePayload();}finally{field.value=raw;}
};

assert.equal(v106ExecutedAt('2026-10-23T11:29:00+01:00'),'2026-10-23T10:29:00.000Z');
assert.equal(v106ExecutedAt('2026-10-23T11:29:00-03:00'),'2026-10-23T14:29:00.000Z');
assert.equal(v106ExecutedAt('2024-02-29T11:29Z'),'2024-02-29T11:29:00.000Z');
for(const date of ['2026-02-29T11:29Z','2026-04-31T11:29Z','2026-01-01T24:00Z','2026-01-01T12:60Z','2026-10-23T11:29','23/10/2026, 11:29','2026-10-23T11:29+14:30','2026-10-23T11:29-00:00'])assert.throws(()=>v106ExecutedAt(date));
const original=field.value;const result=r21386ls19aPayload();assert.equal(result.executed_at,'2026-10-23T10:29:00.000Z');assert.equal(field.value,original);
console.log('EXPLICIT_TIMEZONE_CALENDAR_AND_PAYLOAD_RESTORATION_OK');
