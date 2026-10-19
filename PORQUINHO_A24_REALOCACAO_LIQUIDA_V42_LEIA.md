# A24 V42 — Realocação líquida e valores parciais de cenário

Requer V41 instalado. SHA256: `e3b57a1e0f624ab3990d5353781a9f5d9891af9227f3a1242579d9795970fb34`.

Amplia o comparador existente para valores de venda parciais oriundos de cotações de custos revisadas. Não introduz coeficiente manual de risco, tamanho arbitrário ou novo pedido de informações sobre transações já registradas.

## Cálculo

C=capital financeiro exato de referência da origem; A=valor de venda cotado (0<A<=C); Fs=custos de venda; B=valor de compra cotado; Fb=custos de compra. Só aceita B+Fb=A-Fs, sem cash adicional, mesma conta/moeda e instrumentos distintos. O restante C-A permanece na origem no cenário. Não escala tarifas de uma operação para outra e não reaproveita uma taxa realizada como tarifa futura. Sem cobertura completa dos componentes de custos não produz cenário líquido.

Por modelo, a diferença após custos de entrada é B*(1+rd/100)-A*(1+rs/100). A parte não vendida permanece nos dois contrafactuais e se cancela na diferença. O limite de custos antecipados que anula vantagem positiva na posição inteira de referência é C*(rd-rs)/(100+rd), condicionado a rd>rs e rd>-100. Não é a simples diferença bruta C*(rd-rs)/100, porque o capital usado para pagar custos deixa de render no destino. Não é uma cotação, política aprovada ou garantia de retorno. Sem vantagem positiva, limite0.

Cada cenário conserva evidências/rotas, venda, compra, custos, saldo de referência restante e resultados por modelo. Cotações parciais não removem a pendência de custos da posição inteira. São possibilidades enumeradas, nunca escolha automática de venue, campeão de modelo, recomendação, ordem ou reserva. requested_amount/quantity permanecem None; sizing_created/execution_authorized permanecem false. Restrições de liquidez, lotes, manutenção e validação econômica não são certificadas por essa aritmética.

## Interface e evidência real

Em Oportunidades, abaixo da realocação existente, aparece Realocação · custos e valores de cenário. Detalhes em popup com Voltar, sem menus expansíveis novos. Preserva filtros de instrumento, conta e moeda, sem equivalência por ticker, FX ou transferência bancária. Não altera P/L, intraday, contas ou planos da V41.

No último relatório real, não havia cenários com custos futuros completos. Instalar este patch não cria cotações nem tarifas: pode continuar mostrando zero cenários cotados e nenhum valor final a mover. Quando houver capital financeiro exato e modelos compatíveis, já mostra o custo de equilíbrio derivado. O próximo fechamento da F4 ainda exige fontes atuais de custos/liquidez e decisão/dimensionamento final com publicação correspondente. Não espera a conclusão de todos os ciclos30/60/90dias para exibir leituras atuais; também não certifica pesquisas prematuramente.

## Preservação e instalação

Dados, modelos, memória, histórico, journals e snapshots não fazem parte do patch. Alterados: comparador de projeção somente leitura, template e camada de apresentação/testes. Não coleta dados, não treina e não chama endpoint financeiro. Lógica normal de aprendizado já configurada no aplicativo permanece funcionando. Validação em fontes temporárias,170 baselines, backup e aplicação atômica. Não exige/reescreve o helper local run_monitor_ui_regressions.py.

Ativador V42 recusa trabalhos ativos; reinicia somente Porquinho8765 e preserva Bridge8787. Se estiver ocupado, repita apenas `~/Downloads/PORQUINHO_A24_ATIVAR_CONSOLIDACAO_V42.command` após o ciclo normal. Cmd+Shift+R após ativação. Relatório de ativação exporta contagens, não valores/rotas individuais.

## Verificação

1142 testes Python +239 verificações JavaScript;38 testes simulados do ativador. Casos: valor parcial, restante preservado, compra financiada exatamente, efeito de custos sobre capital investido, taxas revertendo vantagem, moedas/contas incompatíveis, custos desconhecidos, nenhuma escala de tarifa, nenhuma seleção/ordem, compatibilidade e preservação dos registros. Chromium com cenário Python sintético100→98 e100 restante, diferença0.90, popup/Voltar e viewport390 sem overflow ou erros. Instalador aplicado/repetido com backup único, baseline divergente recusada, sentinelas de dados/modelos/histórico e helper local intactos. Não é validação dos modelos ou das operações reais do Mac; conferir relatório local após instalar.
