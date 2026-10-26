# V134 — revisões atuais compartilhadas pelos cenários

Unifica o caminho das revisões de custos usadas na tela e na aritmética condicional dos cenários aprendidos. O monitor não depende mais de uma cópia anterior do contexto de custos do aprendizado para produzir essa aritmética. A leitura estreita da API de revisão reutiliza a mesma ligação.

## Entrega

- O estimador existente continua validando conta, instituição, plano de preços, instrumento, moeda, operação, valor exato, validade, conflitos e substituições de revisões. Nada é extrapolado de outro valor, conta, moeda ou tarifa histórica.
- Cada rota aplicável conserva sua revisão, fonte, validade e seis componentes. Componentes conhecidos formam um subtotal identificado; um componente desconhecido impede um total completo. Um custo zero só aparece quando explicitamente documentado na revisão completa.
- Rotas diferentes continuam como alternativas sem seleção. Revisões conflitantes na mesma rota continuam bloqueadas. Combinações de rotas entre pernas do cenário são enumeradas pelo cálculo existente, com seu limite já existente de 256 combinações, sem somar alternativas entre si.
- Uma única leitura atual das revisões alimenta os detalhes e o cálculo condicional de retorno de pesquisa menos custos de compra. Essa ligação reconstrói valores e escopo e não usa o contexto antigo como fallback. Fontes alteradas durante a leitura fazem o produtor existente retirar os resultados.
- O comparador de caixa existente é reutilizado somente se houver um modelo de caixa explícito, atual e compatível. Ausência de remuneração informada não é convertida em retorno zero. Custos de manutenção e tributos não cobertos não são inventados.
- A UI acrescenta botões nos custos revisados por cenário para abrir rota, subtotal, componentes e fontes. A validade também é verificada no frontend ao renderizar. Não altera o layout dos indicadores, os filtros, o intraday ou o gráfico patrimonial.
- O diagnóstico existente passa a imprimir `CUSTOS_DOS_CENARIOS`, com contagem dos cenários e das variantes condicionais e os digests da leitura atual.

## Limites preservados

Uma revisão é uma declaração de custo, não validação independente do retorno previsto. Todos os bloqueios de publicação econômica, risco, dimensionamento e comparação permanecem. Não escolhe rota, muda alocação, redimensiona valores, cria recomendação, executa negociação ou treinamento. Sem novas requisições de mercado ou gravações de histórico. Modelos, pesos, limites, saldos, orçamentos, ledger e revisões salvas não são alterados.

O caso sem pernas de compra permanece explicitamente sem modelo de custos de manutenção; não recebe um custo total de manutenção zero.

## Verificação

Passaram 348 testes Python, incluindo integração de custos, estimador e armazenamento reais com fontes sintéticas, valores exatos, custos parciais, zero explícito, múltiplas rotas/pernas, validade, conflitos, não reaproveitamento de contexto antigo, comparação condicional com caixa e regressões do monitor, aprendizado e regras globais. Passaram os testes JavaScript/DOM de componentes, validade, clique e retorno, revisão de custos, oportunidades por moeda/conta, Todas separadas, intraday e gráfico patrimonial. O instalador passou nos testes de reaplicação, recusa de divergência e preservação de sentinelas de modelos e ledger.

Não houve coleta real de mercado nem teste visual no Mac. A ausência de revisões completas no ambiente do usuário continuará aparecendo como pendência, sem fabricar custos para preencher a tela.

## Aplicação

Instale com `--reiniciar` e atualize a página. A leitura dos custos já armazenados não exige um novo ciclo. Use o diagnóstico:

```bash
"$HOME/anaconda3/bin/python" -I -B "/Applications/Bridge_Companion/porquinho_v33_web_foundation-2/tools/diagnose_global_action_metrics_a24.py"
```
