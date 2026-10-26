# V129 — Revisão de custos na UI e referência de pesquisa limitada ao caixa

## Entrega integrada

Adiciona **Revisar custos** aos valores exatos dos cenários existentes. O formulário identifica a conta, instrumento, moeda e valor no servidor; o navegador não escolhe outro valor ou cria uma compra. Usa o armazenamento existente de `account_cost_evidence_a24` e a sessão local já utilizada pelo Porquinho.

Os seis componentes começam como desconhecidos: corretagem/comissão, bolsa, spread, slippage, tributos e outros custos. Zero precisa ser informado explicitamente; não aplicável requer declaração de evidência. A referência da fonte, local da consulta, data observada, prazo de uso da revisão e confirmação de cobertura são explícitos. Nenhuma tarifa global é inferida de uma prévia. Datas exigem fuso; valores são enviados como decimais textuais, sem conversão intermediária para ponto flutuante.

Uma revisão pode permanecer parcial. Custos revisados continuam sendo declarações, sem atestação independente ou validação econômica. O formulário não compra, registra posição, concede autoridade ou ativa recomendação.

## Atualização de evidências

Atualizações explícitas da mesma conta/instrumento/moeda/rota/operação/valor/plano de preços podem substituir a revisão anterior sem sobrescrevê-la. As referências antigas ficam nos arquivos imutáveis. As relações exigem identidade exata, cronologia estrita e referências existentes; não se presume uma escolha entre rotas distintas. A revisão antiga não volta a valer quando a sucessora expira.

A gravação verifica a versão das revisões sob o bloqueio existente, além de revalidar o cadastro da conta. Formulários obsoletos e tentativas concorrentes são recusados. A ausência de plano de preços também é registrada nas novas revisões, permitindo invalidá-las se esse contexto mudar depois.

## Caixa e orçamento

O orçamento registrado continua sendo intenção de planejamento; nenhuma alteração de orçamento, plano, caixa, ledger ou modelo é aplicada.

Quando há exatamente um orçamento ativo, um plano associado, pesquisa habilitada e caixa positivo inferior à intenção, os cenários podem usar esse caixa como **referência de pesquisa**. A intenção original é exibida separadamente. Isso destrava a análise e a revisão dos custos para uma referência suportada pelo caixa, sem tratar o valor como ordem ou novo dimensionamento de execução.

O estado `ACTIVE_BUDGETS_EXCEED_CURRENT_CASH` continua presente, o teto dos rascunhos financeiros continua indisponível e a divergência continua na lista de pendências. Não há rateio automático entre múltiplos orçamentos nem eleição de plano. A regra usa fatos do contexto, sem nomes de bancos, provedores, ativos ou moedas.

A referência passa pelo vínculo dos cenários, base econômica e avaliação aritmética existentes. Cada leitura valida novamente conta, moeda, plano, intenção original e caixa. Mudanças de caixa ou plano retiram a conciliação anterior. Não há conversão cambial ou mudança de pesos aprendidos.

## UI preservada

O formulário tem estilos limitados ao seu próprio identificador, com campos completos e disposição responsiva. O cache do JavaScript é atualizado. Não muda portlets de patrimônio, ganho/perda, evolução ou intraday; esses renderizadores foram verificados com os testes existentes.

## Testes

- Fluxo HTTP real com Flask e sessão local: campos exatos, confirmação, origem, prazo, contexto obsoleto, concorrência, zero explícito, componentes desconhecidos, substituição com preservação do histórico e ausência de escritas financeiras.
- Encadeamento da referência de caixa até associação, base econômica, transporte e avaliação dos cenários, preservando os fatos originais e o bloqueio dos rascunhos financeiros.
- Execução do formulário JavaScript real com respostas sintéticas: fuso, precisão decimal, zero, desconhecidos, sessão e somente chamadas para revisão de custos.
- Regressões de aprendizado, calendário, custos, ações, contas e acompanhamento prospectivo.
- Instalador: hashes exatos, backup, repetição, divergência e preservação de sentinelas de modelos/ledger.

Uma asserção anterior ao V111 que esperava bloquear também as observações quando o orçamento excede o caixa foi excluída da seleção de regressão. O arquivo de demanda de pesquisa é byte a byte igual ao V111 publicado; seus testes de substituição foram executados. O V129 não muda essa regra antiga.

## Aplicação e uso

Aplicar com `--reiniciar`, aguardar o reinício e atualizar a página. Em **Custos e fontes → Custos revisados por cenário**, abrir **Revisar custos** no valor desejado. Preencher somente informações documentadas; manter desconhecido o que não estiver comprovado. Não é necessário efetuar compra para usar este fluxo.

A instalação não registra revisões automaticamente. Somente o botão de confirmação grava a declaração em seu armazenamento separado. Recomendações finais continuam dependentes dos demais componentes e validações.
