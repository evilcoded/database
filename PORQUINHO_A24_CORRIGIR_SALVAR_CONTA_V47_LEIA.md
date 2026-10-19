# A24 V47 — Preservar a tela atual depois de salvar conta/instituição

Requer V46. Correção de interface, sem alteração de API/backend/dados.

## Causa e correção

Salvar conta ou instituição chamava diretamente `v38240Accounts`, que monta a grade antiga. A navegação normal chama o fluxo `v38130Accounts`, composto pela etapa inicial e pelo renderizador atual `v38279r4Render`. A gravação do plano funcionava, mas a composição final da tela não era executada após o PUT.

Os quatro callbacks existentes de criação/edição de conta/instituição agora aguardam o fluxo completo. O endpoint, payload, campos e autoridades do salvamento não mudam. Não há nova operação financeira, nem repetição do POST/PUT para recarregar a interface. A leitura posterior usa os mesmos read models já existentes na tela normal.

A validação V46 testou gravação/edição e modal isolado; não capturou a recomposição integral após salvar. V47 acrescenta testes da chamada composta e exercício no Chromium com o salvamento e os renderizadores reais de produção, com provedores sintéticos. Não contém correção de valores financeiros ou novo layout bancário.

## Uso

Instale e recarregue com Cmd+Shift+R. Abra Contas e Bancos e teste editar/salvar novamente. Não é necessário cadastrar os planos outra vez.

O instalador altera somente `static/app.js` e o teste JavaScript correspondente, com baseline, validação temporária, backup/rollback e repetição segura. Nenhum serviço é iniciado/reiniciado; nenhum ativador é executado ou criado. O servidor existente serve o JavaScript atualizado ao recarregar o navegador. Dados e planos já salvos, instituições, contas, snapshots, modelos, memória e histórico não são regravados pelo instalador.

## Verificação

1206 testes Python e261 verificações JavaScript aprovados. Quatro novos cenáriosJS: retorno à tela composta após salvar conta, criação/edição de instituição e espera da conclusão do renderizador atual. Chromium desktop/mobile390: salvar pela função real, executar a composição real dos renderizadores, remover grade antiga, preservar plano e controles atuais, reabrir a edição e ausência de overflow/erroJS. Instalador aplicado/repetido com baseline divergente recusada e sentinelas incluindo registro com plano previamente salvo, dados/modelos/histórico/runner local preservadas. Testes sintéticos; confirmação visual final depende do navegador real após atualização.
