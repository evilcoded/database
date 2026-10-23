# V117 — estimativa do contrafactual específico da ação

Implementa um produtor aritmético de referência de manutenção, reutilizando as previsões já existentes. Não treina nem seleciona outro modelo, não muda pesos, regras de compra/venda, critérios de ativação ou horizontes de aprendizado.

## Cálculo

- KEEP: usa a previsão da posição de origem como referência de manutenção; a diferença bruta de manter em relação a si mesmo é zero. Isso não significa risco zero ou retorno zero.
- REALLOCATE: usa a previsão da posição de origem como contrafactual. Calcula retorno bruto previsto do destino menos retorno bruto previsto da origem, em fração de retorno. Não usa a média dos retornos históricos como previsão de manutenção. A diferença não é retorno líquido, ganho em dinheiro, utilidade ou quantia recomendada.
- SELL/REDUCE: estima somente o retorno de manter a origem. Não inventa rendimento do caixa, preço de venda, fração a reduzir ou custos para completar o resultado da ação.
- DEPLOY_CASH/INCREASE/NO_ALLOCATION: exige o modelo explícito de preservar o caixa; saldo sem informação de rendimento não vira rendimento zero. INCREASE não usa o retorno do ativo comprado como se fosse o retorno do dinheiro ainda disponível.

Exige identidade financeira exata, conta, moeda, horizonte/unidade e fingerprint do contexto. Não resolve aliases de pesquisa como identidades financeiras. Fontes duplicadas são recusadas. Requer proveniência do provedor e instrumento, hashes dos experimentos/fontes e datas coerentes. Reutiliza o limite de frescor já existente no produtor de componentes (três dias), sem estabelecer nova maturação. A diferença origem/destino só é calculada quando data de origem da previsão e amostragem coincidem.

O estimador respeita o horizonte que recebe; não treina novos horizontes e não converte observações em dias corridos. Os testes 30/60/90/120 verificam essa parametrização, não comprovam que já existam modelos operacionais para todos esses horizontes.

## Integração e preservação

O handoff passa a transportar o contrafactual derivado da ação como componente de pesquisa, sempre NOT_VALIDATED_FOR_COMPARATOR. A referência anterior é preservada separadamente; ela não é apagada do pacote de origem. Quando não existe contrafactual adequado, não se mantém a média histórica como previsão de caixa ou manutenção. Um componente já aceito pelo validador existente e explicitamente ligado à mesma ação/capital é preservado, sem sobrescrita pela nova estimativa.

O pacote de componentes recebe a data da observação de origem da previsão para a verificação temporal. Isso pode criar novas versões de pacotes derivados no próximo ciclo normal; pacotes imutáveis anteriores e modelos/experimentos originais são preservados. O handoff não grava observações diárias nem transforma reutilizações por ação em amostras independentes de aprendizado.

O diagnóstico da V116 passa a mostrar `source_production.counterfactual_estimation`: referências estimadas, diferenças brutas e motivos de indisponibilidade. Contagens referem-se a ações examinadas, não a compras recomendadas nem a observações independentes.

Esta entrega não certifica os modelos que falharam na avaliação e não completa custos, utilidade, risco ou dimensionamento faltantes. Não assegura recomendações imediatas. Nenhum conjunto de pesquisa é promovido por alteração de flags.

## Validação e instalação

232 testes Python passaram, incluindo 22 novos testes do estimador e regressões de componentes, risco, handoff, ações, fonte econômica, comparação e publicação. Testes verificam diferenças positivas/negativas, zero matemático do KEEP, preservação do caixa desconhecido, origem ausente, aliases não resolvidos, escopos/provedores/horizontes incompatíveis, duplicatas, datas futuras/expiradas/incoerentes, amostragem diferente, unidades e números inválidos, preservação de componentes validados e ausência de promoção.

Quatro arquivos de código, sem alteração de parâmetros, modelos salvos, carteira ou histórico. Instalador com hashes, backup, preflight e recusa de divergência. Instalação/repetição/recusa de divergência e preservação de sentinelas de modelo e ledger testadas em árvore sintética. Não executado nos bancos ou Mac do usuário.

`--reiniciar` reutiliza o reinício verificado existente. Após um ciclo normal, o diagnóstico manual já instalado exibe os novos resultados sem exigir nova coleta ou treinamento manual.
