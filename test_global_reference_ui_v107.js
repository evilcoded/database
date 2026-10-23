const assert=require('assert');const esc=v=>String(v).replaceAll('<','&lt;');const a24UiMoney=(v,c)=>v+' '+c;let r21375bDetailPosition=p=>'<div><small>VALOR ATUAL</small></div>';
/* V107: surface the same scoped reference valuation in existing account details. */
const v107OriginalDetailPosition=r21375bDetailPosition;
r21375bDetailPosition=function(position){
 const html=v107OriginalDetailPosition(position).replace('<small>VALOR ATUAL</small>','<small>VALOR DE REFERÊNCIA</small>');
 if(position.current_value===null||position.current_value===undefined)return html;
 const pnl=position.reference_pnl,at=position.market_quote_at;
 const detail='<small>Referência · '+esc(position.market_price_source||'Fonte não informada')+(at?' · '+esc(new Date(at).toLocaleString('pt-PT')):' · Data indisponível')+'</small>'+(pnl===null||pnl===undefined?'':'<small>Ganho/perda não realizado: '+esc(a24UiMoney(pnl,position.currency))+'</small>')+'<small>Preço de referência; não é cotação de execução.</small>';
 return html.replace(/<\/div>$/,'<div style="grid-column:1/-1;display:grid;gap:4px">'+detail+'</div></div>');
};
const p={current_value:120,reference_pnl:'20',currency:'BRL',market_price_source:'<source>',market_quote_at:'2026-10-23T10:00:00+00:00'};const html=r21375bDetailPosition(p);assert(html.includes('VALOR DE REFERÊNCIA'));assert(html.includes('20 BRL'));assert(html.includes('&lt;source>'));assert(html.includes('não é cotação de execução'));assert(html.includes('grid-column:1/-1'));const missing=r21375bDetailPosition({current_value:null});assert(!missing.includes('Ganho/perda'));console.log('ACCOUNT_REFERENCE_VALUE_PNL_SOURCE_UI_OK');