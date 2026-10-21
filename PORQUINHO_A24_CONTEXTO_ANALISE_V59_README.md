V59 — Transporte do contexto da análise existente

O produtor legado já decide COMPRE/VENDA/REALIZE/MANTENHA/ACOMPANHE no ciclo corrente. A moeda da requisição de mercado não acompanhava o score. Este ajuste registra os parâmetros da requisição em novas gravações do cache e transporta moeda, fonte, instante e frescor para scores e suas cópias experimentais.

Não altera os parâmetros das requisições atuais, pontuação, critérios, limiares, seleção, treinamento, pesos, ações, cálculo de valores ou maturação. Não promove sinais experimentais. Não preenche moeda pelo nome de campo ou pelo ticker. Cache antigo sem contexto de requisição continua sem moeda explícita até uma resposta nova com contexto registrado. A chamada legada atual permanece EUR; este patch não implementa a análise de caixa BRL nem o planejamento semanal autônomo.

Verificação: 250 comparações diferenciais das ações e valores experimentais; comparação estrutural das demais funções e da lógica do ciclo descontando apenas metadados; transporte de moeda explícita, recusa de contexto ausente/divergente e preservação das linhas de entrada. Testes isolados, sem consultar provedores reais ou treinar modelos.

Instalador aceita apenas a versão de origem verificada ou o resultado idêntico. Faz backup, não inicia serviços e não modifica arquivos de aprendizado, dados financeiros ou configuração. O cache recebe metadados durante o uso normal após reinício e nova consulta. Requer reinício seguro do Porquinho; não interromper ciclos em andamento.
