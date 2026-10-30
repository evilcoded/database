# V145 — consolidação e explicação das sugestões globais

O diagnóstico anterior confirmou índices comuns para 12 pares cripto/moeda e seis ações, com ETH sinalizado para revisão de proteção. Não havia COMPRA elegível naquele recorte. Esta entrega distingue falta de dados, critérios não atendidos e dimensionamento pendente; não cria uma compra para preencher a tela.

## Comportamento

- Cada sugestão transporta um `decision_path`: disponibilidade das entradas, comparações reais das regras, estágio de dimensionamento e motivos de pendência. Nenhuma regra ou valor é recalculado por essa explicação.
- `decision_pipeline` por conta/moeda separa leituras atuais, entradas pendentes, sinais de COMPRA, compras com valor bruto e compras aguardando dimensionamento. Critério de entrada não atendido continua sendo diferente de falta de dados.
- O detalhe do plano e de cada sugestão apresenta os critérios e pendências em pequenos controles clicáveis. Chaves dos controles incluem conta/moeda/identidade/critério, impedindo que os detalhes de um ativo substituam os de outro.
- Os motivos de histórico diário ou cotação exata ausente chegam ao plano sem substituir índices por zero ou por métricas legadas de outra moeda.
- A fila histórica existente prioriza séries ainda ausentes e depois a observação de origem mais antiga. Mantém uma consulta histórica por ciclo, os períodos de espera, a requisição individual BRAPI, os vínculos explícitos e o armazenamento selado. Não amplia o universo, permissões ou plano contratado do provedor.
- Diagnóstico `tools/diagnose_decision_pipeline_a24.py --resumo` inclui o funil e os critérios por sugestão.

## Limites e preservação

Não modifica limites configurados, fórmula dos índices V143, aprendizado/modelos legados, saldos, posições, lançamentos ou ordens. Preserva proteção V144, intraday, gráficos e filtros Global/EUR/BRL. A ausência de histórico ou de cotação continuará pendente quando o provedor não entregar dados válidos. Não atesta elegibilidade de negociação, custo líquido, rentabilidade ou precisão da heurística. Horizontes prospectivos não amadurecem com a aplicação do patch.

O instalador verifica sete arquivos contra a base anterior, exige o registro descritivo V144, faz backup, recusa divergências antes de escrever e sincroniza somente o conhecimento descritivo após aplicar. Reaplicação é idempotente. `--reiniciar` usa o reinício verificado existente, que pode aguardar o ciclo atual.

## Validação executada

159 testes Python de integração/regressão passaram: decisões/dimensionamento, índices comuns, associação às posições, captura prospectiva, análise de ações, históricos, proteção e conhecimento. Um teste antigo que procura uma atribuição com nome removido na AST do servidor foi excluído dessa seleção; os ganchos atuais são cobertos por testes de integração operacional. Testes DOM passaram para critérios clicáveis, COMPRA/VENDA/REALOCAR, proteção e botões de moeda. Instalação sintética confirmou os sete payloads, backup, reaplicação sem alterações, recusa de divergência e preservação dos sentinelas financeiros/modelos. Não houve consulta real ao mercado nem validação de desempenho financeiro.
