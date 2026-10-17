# A24 — Base comum e grupos das candidatas (V26)

Consolidação F3/F4. Reutiliza capital_relative_utility para converter projeções
brutas de pesquisa à referência de capital do orçamento, mantendo retorno, risco,
custos e utilidade como dimensões distintas. Não seleciona política ou ordem.

## Base comum de pesquisa

Cada grupo de comparação mantém conta, moeda, orçamento, plano, capital de
referência, data da previsão e horizonte iguais. Não agrega moedas, usa custo de
aquisição como capital investível ou compara montantes de orçamentos diferentes.
Mesmo quando a porcentagem é uma unidade comum, o capital e os demais contextos
continuam explícitos. Isso não substitui a base tipada e validada do comparador
governado; as restrições originais continuam preservadas.

Reconstrói o resultado de aprendizado V24 a partir dos experimentos exatos que
ele referencia. Os hashes precisam coincidir e o conteúdo da política precisa
ser reproduzido. As frações do cenário V25 devem corresponder à distribuição
original, inclusive cash. Não redistribui fontes bloqueadas ou escolhe outro
modelo/venue quando um vínculo não existe.

Calcula a contribuição das previsões das fontes selecionadas na hipótese de
cash com retorno nominal de preço zero, conforme o método de pesquisa V24. O
conversor original fornece a variação bruta sobre o capital de referência.
Esse número não é previsão validada do retorno líquido da conta. Não inclui
juros do cash, custos de negociação, impostos ou custos de manutenção desconhecidos.
Não arredonda ordens para casas decimais presumidas de uma moeda: não gera ordens.

O RMS de perdas observado no treino e os resultados posteriores são preservados
como observações retrospectivas. Não são passados como um modelo validado de risco
futuro. O conversor recebe risk_measure=None. Uma taxa histórica executada, mesmo
registrada corretamente, não é inferida como tarifa futura.

Custos totais permanecem UNKNOWN e retorno líquido/utility_score permanecem None.
Não há venue e notional de ordem selecionados, nem evidência completa desses
custos para o cenário. Mesmo uma candidata só de cash não ganha custo total zero:
suas pernas de negociação podem ser não aplicáveis, mas juros/custos de manutenção
ainda precisam de modelo adequado. Sem parcela de cash, não se exige um modelo
de juros de cash inexistente naquela distribuição; os outros custos continuam
pendentes. O patch explicita essas lacunas em vez de fabricar parâmetros.

## Grupos de distribuição e comportamento observado

O primeiro agrupamento reúne as mesmas frações por instrumento/provedor/moeda e
cash na data atual. Frações como 2/2 e 1/1 são iguais matematicamente. O agrupamento
não afirma igualdade entre as previsões numéricas: modelos diferentes podem gerar
a mesma distribuição com magnitudes previstas diferentes.

O segundo agrupamento também considera as distribuições em todos os períodos de
treino e avaliação selecionados, com a mesma versão de pesquisa. Portanto duas
candidatas iguais hoje, mas diferentes nos períodos avaliados, continuam separadas.
Isso descreve o comportamento observado, não prova equivalência dos algoritmos
em dados ainda não vistos ou independência estatística entre grupos.

Nenhuma candidata ou versão é apagada. A contagem de grupos não vira votação,
probabilidade de acerto, força de evidência ou regra de desempate. Não há ranking,
vencedora, política de utilidade aprendida/validada ou publicação canônica.

## Integração e preservação

A leitura utiliza a mesma captura de fontes que o V25. Alterações financeiras,
de experimentos, histórico ou versões durante a projeção continuam verificadas.
Falha na nova base econômica aparece no diagnóstico sem inventar um fallback.
A UI mostra somente contagens e limites semânticos dos grupos dentro da seção
existente, preservando abertura e cadência. Nenhuma tag canônica é substituída.

Não grava arquivo novo de pesquisa, não treina, não altera o método/namespace V24,
memória SQLite, conversas, autoconhecimento, modelos, snapshots, previsões, resultados
maturados, posições ou transações. Não faz requisições de rede ou operações
financeiras. Os dados internos de capital/conta não são exportados no resumo.

O modo manual continua exigindo uma decisão adequada e confirmação de execução;
o modo automático permanece desabilitado. Ainda faltam custos atuais aplicáveis,
liquidez/eligibilidade, retorno e risco validados, utilidade, comparação de ações,
sizing, validação prospectiva e produtor canônico independente.

## Instalação, ativação e validação

Instalador com baseline, backup e regressão em cópia temporária. Ativador V26
reinicia somente o Porquinho identificado, preserva Bridge e recusa ciclos ativos
ou enfileirados. Sem SIGKILL, segundo servidor, refresh forçado ou endpoint financeiro.
Se houver adiamento, repetir apenas o ativador indicado quando o ciclo terminar.
Ativação observada não certifica resultado econômico ou carregamento do navegador.

952 testes Python e 100 verificações JavaScript em pandas 2.2.3 e 3.0.3, sem skips.
Os 21 novos testes cobrem fonte exata, reconstrução de resultado, frações,
capital/conta/moeda/plano/horizonte, reutilização do conversor, cash sem custo zero
presumido, risco observado distinto de risco futuro, previsões distintas com a
mesma distribuição, trajetórias históricas diferentes, ausência de votação/
ranking/autoridade, privacidade e preservação dos insumos.

33 testes simulados do ativador. Instalador testado em aplicação e repetição,
recusando baseline divergente e preservando dados/CSV/configuração. Todas as
fixtures são sintéticas; esses testes não validam políticas reais de mercado.
