# A24 V48 — Provisões documentais de tarifas no comparador

Requer V47. Primeiras fontes: N26/Alemanha e Revolut/Lituânia, plano Standard, moeda EUR e identidades de cripto explicitamente cobertas no catálogo de dados. O motor não contém branches por banco, país, moeda, ativo ou percentual. Novas instituições/fontes podem ser descritas no mesmo catálogo, após revisão; isso não é um buscador automático universal da internet.

## O que passa a aparecer

Um painel compacto no cartão de realocação mostra tarifas de referência para venda e compra. Valores e custos abre popup com URL oficial, hash da fonte consultada, jurisdição da tabela, data de consulta, prazo de nova revisão, variantes e componentes pendentes. Sem menus expansíveis novos. Controles, planos salvos, filtros, P/L, gráficos e fluxos manuais anteriores permanecem.

As parcelas usam o mesmo capital de referência, separadamente, para comparação. A compra não foi dimensionada com o produto líquido da venda; portanto não há rota autofinanciada, custo total completo ou valor recomendado para mover. Não some as duas parcelas como se fossem uma cotação final de uma ordem. Nenhum cenário documental é inserido nas evidências revisadas de custos completos e nenhum bloqueio de execução/seleção é removido por essas provisões.

## Fontes e condições

- N26: https://n26.com/en-de/crypto . Bitcoin1.5%; demais moedas2.5%; baixa liquidez3.5%. A página informa arredondamento das tarifas para cima ao centavo e exceções possíveis. O dado separa a identidade Bitcoin e apresenta categorias normal/baixa liquidez como alternativas condicionais para as outras identidades cobertas, sem escolher categoria automaticamente. Não prova disponibilidade do ativo no serviço.
- Revolut: https://www.revolut.com/en-LT/legal/exchangingcryptocurrenciespersonalfees/ . Tabela lituana RDAEL Standard/Plus: maior entre1.49% e mínimo por faixa EUR. A tabela contém as faixas0–2,2–5,5–25,25–100,100–150,150–200 e regra acima200. O ponto exato200 é mantido pendente por ambiguidade textual. Regra de dispensa de comissão cripto para fiat/stablecoin é descrita separadamente para identidades explicitamente cobertas; não dispensa uso justo/spread/impostos.

Uso justo Standard pode incluir1% sobre o excesso de€1.000, conforme utilização e entidade. A política inclui exceção para sucursal portuguesa; ela NÃO foi presumida para a conta lituana. Consumo mensal, aplicação da entidade, spread, slippage, impostos, outros custos e elegibilidade permanecem pendentes. Percentuais típicos de spread não foram tratados como limites garantidos nem como spread real da ordem.

As fontes foram consultadas com HTTP200 e têm seus hashes no catálogo. Conteúdo HTML não é executado nem distribuído como código. Os fatos numéricos e as condições estão em `config/research_tariff_sources_a24.json`, separados da lógica genérica. A lista inicial de identidades é dado de cobertura revisada, não whitelist do universo do sistema: identidade não coberta fica sem tarifa, sem inferência por ticker.

## Correspondência e atualização

A política exige instituição/jurisdição de cadastro, plano e moeda correspondentes e classe/identidade de provedor explícitas. Alemanha e Lituânia foram declaradas nesta revisão; o motor não usa o país para inventar moeda ou condição tributária. O nome do plano é comparado sem distinguir maiúsculas/minúsculas. Plano ausente, outra moeda, identidade desconhecida, provedor ambíguo ou políticas concorrentes impedem seleção arbitrária.

O prazo de sete dias no catálogo é uma janela local para REVER a fonte, não uma alegação de vencimento do contrato bancário. Ao vencer, as estimativas deixam de ser usadas. Este patch não automatiza atualização ou extração de novas taxas: mudanças nas tabelas exigem revisão/versionamento do catálogo. Sem acesso de rede no runtime do novo módulo. Falha na fonte nova não oculta as leituras existentes do Brain.

## Preservação e ativação

Dez arquivos de código/configuração/testes,186 baselines, validação temporária, backup/rollback, repetição segura. Catálogo novo adicionado sem sobrescrever arquivo divergente. Não modifica registro de contas, planos cadastrados, posições, cash, ledger, snapshots, modelos, memória, aprendizado ou histórico. Nenhuma tarifa histórica é reclassificada como tarifa atual.

O ativadorV48 usa hashes atuais, inclusive o app.js corrigidoV47. Reinicia somente Porquinho identificado e preserva Bridge; recusa jobs ativos, não enviaSIGKILL ou inicia segundo servidor. Se necessário, repetir apenas `~/Downloads/PORQUINHO_A24_ATIVAR_CONSOLIDACAO_V48.command`. Nenhum refresh manual, treino ou operação financeira solicitado; rotinas normais continuam após reinício. Depois:Cmd+Shift+R.

Diagnóstico localV43 reutilizado: inclui somente contagens de estados das provisões, sem valores monetários. O console imprime ZIP_PARA_COMPARTILHAR. Nenhum envio automático.

## Verificação

1233testesPython+266verificaçõesJS no staging do instalador;38testes simulados do ativador.22novos testes de contexto: tarifas publicadas, faixas/mínimos, arredondamento, coincidência de conta/plano/moeda/classe/provedor, datas, ambiguidades, exceção stablecoin, conservação dos resultados existentes, leitura do registro/catálogo real em fixture isolado e mudanças durante leitura. Cinco testes adicionais de arredondamento genérico; cinco testesJS de painel parcial, fonte, pendências, escape e links. Chromiumdesktop/mobile390 com provisões geradas pelo módulo Python: cartões únicos, popup/Voltar, cenários anteriores conservados, sem overflow/erroJS. Instalador aplicado/repetido, baseline divergente recusada e sentinelas preservadas. Tudo sintético; resultado nas contas reais precisa ser confirmado após ativação. F3/F4 não são encerrados por essas provisões.
