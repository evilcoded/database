# A24 — Brain produtor de políticas candidatas de distribuição (V24)

Continuidade da consolidação F3/F4. Este patch implementa aprendizagem automática
de parâmetros de uma família de políticas de alocação, usando previsões e rótulos
já calculados pelo laboratório global existente. Não pede percentuais manuais.
Não declara autonomia financeira concluída nem valida políticas para operação.

## Método e limites

A hipótese explícita é distribuir parcelas iguais entre as k fontes com maiores
previsões brutas positivas. O número k é aprendido comparando os resultados
realizados anteriores, para cada algoritmo já processado e cada moeda separada.
O espaço pesquisado contém k de 1 ao número de fontes disponíveis. Uma parcela é
1/k; fontes com previsão não positiva deixam sua parcela em cash nominal, sem
renormalizar os outros pesos. Portanto o limite de concentração da hipótese é
aprendido pelo k selecionado, e não fornecido como percentual pelo usuário.
Essa família é uma hipótese do pesquisador, não um otimizador universal de todas
as carteiras possíveis, um modelo completo de tolerância a risco ou recomendação.

O produtor reutiliza folds, previsões e identidades dos experimentos globais
existentes, cujas populações são verificadas pelo validador já utilizado no
laboratório. Não ajusta novamente estimadores, altera seus parâmetros ou promove
um novo campeão ao laboratório antigo. Exige a mesma população realizada entre
algoritmos, seção transversal completa em cada origem, uma fonte por instrumento,
moeda explícita e o horizonte original de 30 observações. Fontes duplicadas,
períodos desiguais, mistura de moedas ou dados ausentes não são preenchidos por
suposição. Outros calendários só serão utilizáveis quando cumprirem esse contrato.

O protocolo de pesquisa separa a primeira e a segunda metade cronológica das
origens. O treino da política exclui qualquer rótulo cujo alvo alcance o início
da avaliação. Em cada lado, a seleção começa na primeira origem e só inclui uma
próxima origem posterior ao alvo anterior. Assim os períodos selecionados não se
sobrepõem. Exige ao menos dois períodos de cada lado para calcular as estatísticas;
isso é um mínimo estrutural, não uma afirmação de suficiência estatística.

A seleção usa apenas a média de retornos brutos e o RMS dos retornos negativos
nos períodos de treino. Mantém todas as candidatas não dominadas nessa comparação,
sem inventar coeficiente de aversão a risco ou escolher uma vencedora única.
Os resultados dos períodos posteriores são calculados depois dessa seleção e não
escolhem parâmetros. Não são aproveitados para reescolher k ou algoritmo.

A referência é a distribuição igual entre todas as fontes da população comum.
Políticas e referência são comparadas sem custos, juros de cash ou simulação de
turnover. Cash tem retorno nominal de preço zero por definição dessa experiência;
isso não afirma ausência de juros, taxas ou risco em uma conta real. Retornos
brutos descritivos não comprovam utilidade econômica líquida nem desempenho futuro.

As proporções atuais de pesquisa usam as previsões mais recentes, por identidade,
provedor e moeda. Não são valores monetários de uma conta e não aplicam regras de
plano, local de negociação, liquidez ou elegibilidade do broker. Não são vinculadas
às posições por ticker e não geram ordens. A definição e unidade das métricas
continuam separadas dos ciclos canônicos de 30/60/90 dias.

## Histórico, memória e execução

As versões de pesquisa são imutáveis, com integridade local e referências aos
experimentos/fontes exatos, em `data/brain/learned_allocation_policy_a24/versions`.
Uma mudança do conjunto de experimentos, dos dados ou do código gera outra versão;
as anteriores ficam preservadas. O resumo mostra apenas o conjunto atual, não o
total de toda a história. Hash local não é atestado independente de disponibilidade
histórica das fontes.

O produtor roda no ciclo normal já existente, após o laboratório global, e grava
no máximo uma versão por ciclo, com lock e revalidação de vínculos/funding antes
de escrever. A leitura do painel reconstrói o cálculo, sem ajuste de modelos,
rede ou gravação. Não há novo timer ou refresh manual. Se os experimentos forem
insuficientes, registra o estado correspondente sem fabricar candidatas.

O instalador só modifica código, com backup e regressões em cópia temporária.
Não treina ou roda o produtor. Após ativação, o ciclo normal poderá produzir as
versões separadas. Mantém intactos memória SQLite, conversas, autoconhecimento,
modelos, snapshots, forecasts, resultados maturados e histórico financeiro.

O novo produtor usa evidência numérica dos experimentos globais. Não utiliza o
conteúdo textual/heterogêneo de `data/memory.sqlite3` como dataset supervisionado,
não copia parâmetros antigos sem identidade e não interpreta flags `passed` como
validação econômica. O Brain original continua com sua memória e rotinas de
aprendizagem; este patch acrescenta a pesquisa de políticas, sem substituir aquele
núcleo ou declarar que toda a integração da memória foi concluída.

O V23 de políticas manuais permanece opcional. O V24 não grava nesse registro,
não exige que ele seja preenchido e não converte as candidatas em
VALIDATED_LEARNING_POLICY. Os campos de validação, comparação, publicação e
execução permanecem falsos. A preparação ainda depende de custos pré-negociação,
liquidez, elegibilidade da conta, comparação de ações, utilidade, dimensionamento,
validação prospectiva e produtor canônico independente.

## Painel e ativação

A seção existente de alternativas econômicas mostra por moeda o número de
candidatas retidas e os períodos de ajuste/avaliação separados. Não exibe uma
distribuição recomendada, não substitui badges e não remove a informação de
ausência de decisão canônica. Mantém o estado de abertura das seções e a cadência.

O ativador V24 conserva as guardas existentes: somente Porquinho, Bridge
preservado, sem SIGKILL, segundo servidor ou endpoints financeiros. Se ocupado,
repetir apenas o ativador indicado após o ciclo normal. Sucesso de ativação confirma
código/endpoint observados; não comprova criação de candidatas em todas as moedas,
carregamento do navegador ou validação de política. Recarregar a página depois.

## Validação

906 testes Python e 96 verificações JavaScript, sem skips, em pandas 2.2.3 e
3.0.3. Os 28 testes novos cobrem aprendizagem que muda com os dados de treino,
ausência de influência dos resultados posteriores na seleção, purga, períodos
não sobrepostos, moedas/identidades, população comum entre modelos, falta de dados,
frações e cash, autoridade, persistência imutável, mudança de funding, corrupção,
remoção de vínculo e lock. Todos os dados de teste são sintéticos.

33 testes simulados do ativador. Instalador aplicado e repetido em cópia temporária,
com um backup, recusa de baseline divergente e preservação de dados/CSV/config.
Não foi executado no Mac do usuário durante o desenvolvimento e não certifica
resultados de mercado ou capacidade de evitar perdas.
