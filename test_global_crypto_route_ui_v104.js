const assert=require('assert');let values={},opened=[],closed=0,toasts=[],fallback=0;global.window={v38275AccountId:'account'};global.$=id=>values[id];global.toast=x=>toasts.push(x);global.closeModal=()=>closed++;global.esc=x=>String(x);global.v38275RouteForm=()=>fallback++;global.r21386ls19aOpenManualTrade=async id=>opened.push(id);

/* V104: route crypto to the SAME existing manual investment form, in every account currency. */
const v104OriginalPositionRouteForm=v38275RouteForm;
v38275RouteForm=function(){
 const select=$('v38275Instrument'),option=select?.options[select.selectedIndex],box=$('v38275RouteBox');
 if(option?.dataset.route!=='EXISTING_MANUAL_EXTERNAL_TRADE'||!box)return v104OriginalPositionRouteForm();
 box.innerHTML='<p>Cripto usa o mesmo registro manual de investimento existente. A moeda será obtida da conta selecionada.</p><p>Você pode abrir o formulário para conferir o cadastro. Revise e confirme somente uma compra já executada, com os dados efetivos. Abrir o formulário não cria posição, reserva de caixa ou ordem.</p><button type="button" id="v104OpenExistingTrade" class="primary">Abrir registro de investimento</button>';
 $('v104OpenExistingTrade').addEventListener('click',v104OpenExistingManualTrade);
};
async function v104OpenExistingManualTrade(){
 const accountId=window.v38275AccountId,instrumentId=$('v38275Instrument')?.value;
 if(!accountId||!instrumentId){toast('Selecione conta e instrumento.');return;}
 if(typeof r21386ls19aOpenManualTrade!=='function'){toast('O registro manual existente não está disponível nesta versão.');return;}
 closeModal();
 await r21386ls19aOpenManualTrade(accountId);
 const select=$('r21386ls19aInstrument');
 if(!select)return;
 const exact=Array.from(select.options).find(o=>o.value===instrumentId);
 if(!exact){select.selectedIndex=-1;const button=$('r21386ls30eReviewButton');if(button)button.disabled=true;toast('O instrumento não está no catálogo do registro manual existente. Nenhum substituto foi selecionado.');return;}
 select.value=instrumentId;
}

(async()=>{for(const currency of ['EUR','BRL']){values={v38275Instrument:{value:'exact-id',options:[{dataset:{route:'EXISTING_MANUAL_EXTERNAL_TRADE'}}],selectedIndex:0},r21386ls19aInstrument:{options:[{value:'other'},{value:'exact-id'}]},r21386ls30eReviewButton:{disabled:false}};await v104OpenExistingManualTrade();assert.equal(values.r21386ls19aInstrument.value,'exact-id');assert.equal(opened.at(-1),'account');}
values.r21386ls19aInstrument={options:[{value:'other'}]};await v104OpenExistingManualTrade();assert.equal(values.r21386ls19aInstrument.selectedIndex,-1);assert.equal(values.r21386ls30eReviewButton.disabled,true);assert.equal(closed,3);console.log('EXISTING_FORM_REUSE_EXACT_ID_OK');})();
