# Dashboard global V118

Entrega integrada sobre V117: patrimônio e P/L por conta/moeda, observações patrimoniais dos ciclos normais, cartões compactos de posições e pesquisa, ações explícitas com origem, e apresentação dos cenários existentes do Brain no seu horizonte original.

- P/L desde o custo registrado; posições sem preço ficam fora do subtotal com cobertura parcial visível. Caixa/aportes não se tornam lucro.
- Histórico separado em `data/observability/global_dashboard_a24`, sem alimentar aprendizado. GET não grava; o ciclo normal registra após revalidar a carteira. Sem reconstrução retroativa. Variações exigem mesma quantidade/custo/população; cobertura diferente interrompe a curva.
- Uma política de ações compartilhada, extraída fielmente do mecanismo original. 500 casos verificam paridade. Provedor é proveniência de dados, nunca escolha de regra. Apenas métricas atuais, normalizadas e na moeda da posição permitem a leitura. Dados insuficientes continuam pendentes. Leitura por regra não é uma recomendação dimensionada.
- Sugestões completas publicadas pelo produtor existente têm prioridade visual. Não se criam recomendações para preencher cartões. Compra, venda, manutenção e realocação aparecem quando a fonte correspondente existe e está válida.
- Cenários aprendidos existentes podem ser exibidos sobre caixa de referência, com projeção bruta dos ativos e horizonte explícito. Isso não é ordem nem ganho líquido. **O modelo de 30 observações não produz uma meta semanal validada; nenhuma conversão para sete dias é feita.** Sem cenário atual conciliado, a meta continua em análise.
- Não altera modelos, pesos, aprendizagem, thresholds, catálogo ou ledger. Não registra compras novamente. Nenhuma negociação executada.

Instalação: executar `PORQUINHO_DASHBOARD_GLOBAL_V118.command --reiniciar`. Verifica todas as bases antes de escrever, faz backup, recusa divergências e aceita reaplicação idempotente. Após reiniciar, aguarde um ciclo normal concluído; o gráfico começa na primeira leitura observada e cresce a partir daí. A UI mantém os filtros persistidos.

Validação: 122 testes Python passaram (painéis, monitor, publicação manual, fonte econômica, contrafactual, regras globais, isolamento, histórico). Um teste legado de EUR já incompatível com a prova de escopo exigida pela base V108 foi excluído; essa exigência não foi relaxada. Teste JS verifica P/L parcial, isolamento de conta/moeda, ações e cartões. Sintaxe dos scripts verificada. Instalação/repetição/divergência e preservação de sentinelas de modelos/ledger verificadas. A captura visual em Chromium ficou indisponível neste ambiente; ainda é necessária conferência visual no aplicativo real.

Os testes usam apenas dados sintéticos. Execute com a raiz da aplicação como cwd e este diretório no PYTHONPATH; o teste JS aceita `PORQUINHO_PROJECT`.
