# Referências de componentes B3 à vista — V94

Fonte correta recebida: https://www.b3.com.br/pt_br/produtos-e-servicos/tarifas/listados-a-vista-e-derivativos/renda-variavel/tarifas-de-acoes-e-fundos-de-investimento/a-vista/ . Resposta capturada em 2026-10-22T22:07:04.673041+00:00, SHA256 e9a0cf8a6880bb433180c9ced9d22191447c8ab1daa12bd23d556b7c3e83ee6a, bytes verificados. Não usa as tarifas de HFT/derivativos obtidas no V92.

Adiciona produtor genérico e configuração revisável de tarifas. O código cruza mercado, moeda e classe explícitos no catálogo, sem extrair identidade de ticker. Os dados de configuração especificam B3/BRL, ações e fundos listados e as condições publicadas. Não escolhe ativos, banco ou faixa de ADTV para o investidor.

Hipóteses implementadas: operações regulares não day trade, faixa mensal de ADTV de 0 a R$3milhões inclusive. Negociação 0,00500%, CCP 0,02240%, TTA 0,0026%: total 0,0300% por lado. Em leilões de abertura/fechamento, negociação 0,00700%: total da hipótese 0,0320%. Condições ficam explícitas e não verificadas para a conta; não são perfis assumidos. Faixa superior exige regra de alocação mensal; o ajuste 225 não é somado por ordem. Day trade e programas de incentivo não são modelados por estas hipóteses.

Exemplo de cálculo, não proposta de compra: numa referência de R$5.000, a hipótese regular equivale a R$0,25+R$1,12+R$0,13=R$1,50 por lado, e a de leilão equivale a R$1,60. Valores não arredondados: o rateio/arredondamento efetivo do banco não é presumido. As taxas de formação da tarifa já estão incluídas; não se adiciona PIS/COFINS/ISS novamente. IR sobre ganho do investidor, spread, slippage e outros custos permanecem separados.

Integração no ciclo: official_exchange_fee_references no bridge; resumo homônimo em monitor-consolidation. Para casos de caixa, capital_ceiling serve somente como base hipotética comum das alternativas mutuamente exclusivas, nunca como ordem ou sugestão de alocação. Para posições sem valor atual explícito, calcula somente taxas condicionais, sem converter custo histórico em preço de mercado. total_cost permanece null; não cria custos completos revisados, comparação validada, recomendações ou execução.

Inclui dependências documentais do V91 caso ainda não instaladas. Aceita somente os hashes conhecidos dos adaptadores após V89 ou V91; alterações locais ou configurações divergentes são preservadas por cancelamento. Configura rechecagem de fontes em sete dias, não validade garantida do preço ou maturação do aprendizado. Não substitui arquivos de brain/, não altera modelos/histórico financeiro nem os critérios do comparador.

223 testes passaram: cálculo e componentes por lado, leilão separado, falta de notional, identidade/moeda/mercado, não duplicação de tributos, recusa do ajuste mensal por ordem e regressões de risco/decisão. Instalador testado antes/depois de V91, repetição e divergência. Backup antes de substituir. Reinicie somente o Porquinho após o término do ciclo.
