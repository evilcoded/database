# A24 — acompanhamento prospectivo automático das políticas

Continuação da consolidação F3/F4. Registra hipóteses atuais das políticas aprendidas em um journal próprio e acompanha preços futuros sem depender de COMPRA, transação manual ou preenchimento do usuário.

## Registro e maturação

- No ciclo normal, utiliza as políticas atuais reconstruídas e verificadas pelo produtor existente; mantém todas as candidatas daquele registro. Uma primeira captura por moeda e dia UTC, no máximo uma nova captura e um resultado por ciclo. Não substitui a primeira captura quando outros algoritmos chegam no mesmo dia.
- Grava a data atual, a versão/snapshot/digests da política, fontes explícitas e frações exatas. Confere novamente os contextos financiados, vínculos e arquivos antes de gravar. Não atribui emissão antiga ao novo journal.
- Inicia a avaliação no primeiro dia UTC posterior ao registro em que todas as fontes possuem observações válidas. Usa somente o journal diário de cotações já existente, com identidade/provedor/provider_id/moeda/evidência de identidade explícitos; não usa o histórico de 365 dias como observação prospectiva.
- Mede uma trajetória hipotética de parcelas iniciais fixas por 30 intervalos entre 31 observações comuns. Datas podem ter lacunas; não equivale a 30 dias corridos, aos ciclos canônicos de 30/60/90 dias ou ao erro da previsão original.
- Calcula resultado bruto de preço e referência de parcelas iguais em todas as fontes da mesma moeda e mesmas datas UTC. Cash tem somente retorno nominal de preço zero, sem presumir juros ou custos zero. Não renormaliza quando faltam fontes. Não comprova preços simultâneos/executáveis na corretora.
- Grava resultados imutáveis e reconstitui os resultados para leitura. Corrupção, fontes alteradas, duplicatas, dados futuros ou divergências ficam indisponíveis e preservados; não são substituídos silenciosamente.

Journal próprio: `data/brain/prospective_allocation_policy_a24`. Não altera o journal diário de cotações, modelos, memória SQLite, conversas, snapshots anteriores, transações, posições, emissões ou ciclos canônicos. Não muda o método/namespace das políticas aprendidas; os processos de aprendizagem anteriormente configurados continuam.

## Limites e interface

É evidência local de pesquisa, sem atestado independente. Registros diários/candidatas podem se sobrepor e não são amostras independentes. Não modela tarifas futuras, juros de conta, elegibilidade, liquidez, risco ou utilidade econômica. Não treina, promove modelos, valida políticas, publica recomendações canônicas, gera ordens ou habilita execução automática.

A mesma UI mostra registros, hipóteses, resultados persistidos e progresso das observações. O resumo não exporta valores financeiros. GET/inspeção permanecem somente leitura. Nenhum novo timer, endpoint ou requisição de rede é adicionado pelo adaptador.

O instalador aplica somente código, após regressões em cópia temporária e backup. Não cria registros prospectivos durante a instalação. Após ativação controlada V29, o ciclo normal poderá criar novos registros; isso precisa ser observado no Mac. Se houver ciclo ativo/em fila, repetir somente o ativador indicado em Downloads após o ciclo terminar.

O Terminal mantém saída compacta; relatório completo continua em Downloads. Ativação preserva o Bridge, sem SIGKILL, segundo servidor, refresh manual ou endpoint financeiro.

## Validação

1.012 testes Python e 105 verificações JavaScript em pandas 2.2.3 e 3.0.3, sem skips; 36 testes novos de protocolo/persistência, incluindo registro e maturação completos com experimentos e fontes sintéticos verificados. 36 testes simulados do ativador. Aplicação e repetição do instalador em cópia temporária, baseline divergente recusado, backup único e sentinelas/CSV/config preservados.

Resultados futuros ainda dependem de observações futuras; estes testes não comprovam desempenho ou captura real no Mac. A24 permanece em consolidação, com custos aplicáveis e demais requisitos econômicos/canônicos pendentes.

SHA-256 do instalador: `9dee5aaeeafe9531aa88b616c9c4b504b17a4494c1dea114ca18c6f2c24dd2ec`.
