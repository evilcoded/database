# A24 V49 — financiamento de hipóteses após comissões

Continua a consolidação das provisões documentais da V48. Em cada conta/moeda/instrumento exatos, calcula quanto da venda de referência fica disponível para a compra depois das comissões documentadas das duas operações. Faixas e mínimos são pesquisados separadamente; categorias condicionais continuam como hipóteses distintas.

A hipótese padrão usa o capital da posição arredondado para baixo à precisão explicitamente cadastrada da moeda. Outros valores de venda só entram se já estiverem nos cenários de custos revisados existentes. Não há percentual fixo de alocação, escolha de valor ou alteração de orçamento. A parcela não vendida e o saldo residual são preservados na identidade matemática. A precisão da moeda não comprova lote negociável do banco.

Os cartões mostram a existência das hipóteses; **Valores e custos** abre a composição de venda, comissão de venda, compra, comissão de compra, saldo e parcela preservada, com Voltar/Fechar. As estimativas por modelo descontam apenas essas comissões e avaliam o saldo residual pelo valor nominal. Não representam lucro líquido certificado. Spread, impostos, eventual uso justo e demais custos pendentes permanecem desconhecidos; custo total e valor selecionado continuam indisponíveis. Não há ordem ou recomendação final.

O motor é genérico: as políticas bancárias e suas fontes permanecem em dados da V48. Este patch não renova sua janela de revisão nem adiciona outra fonte de tarifas. Falta de moeda/precisão ou incompatibilidade de contexto não cria valores por padrão.

## Instalação e ativação

Execute o instalador com o projeto parado ou em funcionamento. Primeiro ele verifica hashes, valida uma cópia temporária e faz backup dos fontes alterados. Nenhum snapshot, modelo, memória, aprendizado, transação ou saldo é migrado ou reescrito. Repetição não gera outro backup. Divergência de baseline interrompe a instalação.

Depois o ativador protegido pode reiniciar somente o Porquinho identificado na porta 8765; Bridge 8787 preservado. Trabalho ativo/em fila bloqueia a ativação. Nesse caso repita apenas `PORQUINHO_A24_ATIVAR_CONSOLIDACAO_V49.command`, salvo em Downloads. Não há SIGKILL, servidor duplicado, refresh manual, treino solicitado ou operação financeira. Atualize o navegador após ativação (Command+Shift+R).

O diagnóstico ZIP exporta somente identificadores/contextos e contagens de estados/hipóteses, sem valores monetários dos cenários. Contagens reais e ativação devem ser confirmadas pela saída local; testes sintéticos não certificam a execução no Mac.

## Validação

1262 testes Python e 269 verificações JavaScript. Incluem faixas não monotônicas, mínimos, arredondamento documental, limites ambíguos, moedas de precisão variável, financiamento sem aporte, preservação de parcela não vendida/saldo, isolamento de conta/moeda/identidade, arquivos locais inalterados, leitura estável e diagnóstico sem valores privados. Mais 38 testes do ativador. Chromium desktop/mobile 390 px: cartões, popup/Voltar e ausência de overflow horizontal ou erros JavaScript. Instalador exercitado com aplicação/repetição, backup único e baseline divergente recusado.
