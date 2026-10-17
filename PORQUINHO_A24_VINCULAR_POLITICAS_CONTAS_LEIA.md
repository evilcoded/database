# A24 — Candidatas aprendidas no contexto das contas (V25)

Continuidade F3/F4. Liga as candidatas produzidas pelo Brain no V24 às contas,
moedas, orçamentos e planos existentes. É uma projeção de pesquisa somente leitura,
não uma recomendação, ordem, autorização financeira ou novo modelo preditivo.

## Comportamento

Cada cenário pertence a uma conta, moeda, orçamento e plano explícitos. O orçamento
de referência é a parcela daquele orçamento ativo, não o cash total da conta nem
o total de todos os planos. Sua soma é conferida contra o teto já projetado pelo
mecanismo atual e contra o cash canônico. Sem orçamento ou plano compatível, o
contexto fica pendente; não se cria saldo ou intenção de investimento.

Cada orçamento exige um único plano ativo correspondente na projeção atual. As
classes permitidas são conferidas separadamente por plano. A união das classes
de vários planos, usada para observação, não autoriza aplicar o capital de um
plano em uma classe permitida somente por outro.

Os pesos da candidata são associados por instrumento, provedor, ID do provedor e
moeda da cotação às solicitações existentes. Em seguida são ligados à alternativa
exata DEPLOY_CASH ou INCREASE da mesma conta, moeda e horizonte. Duplicidade ou
ausência da alternativa não resulta em escolha automática. O contexto de funding
da alternativa deve coincidir com o contexto atual.

Todas as restrições anteriores são preservadas: custos pré-negociação, identidade
financeira, elegibilidade, retorno/risco validados, comparação, utilidade e sizing.
Vínculo de pesquisa não se torna equivalência financeira entre posição e fonte.
Se uma perna estiver fora das classes permitidas ou tiver conflito de identidade,
seu peso não é redistribuído às outras. O cenário completo continua marcado com
suas pendências, sem ser promovido para recomendação.

Os cenários descrevem cash incremental do orçamento, não os pesos-alvo de toda a
carteira. Não comparam peso de pesquisa com custo de aquisição para inferir venda,
não vendem posições ausentes da candidata e não criam realocações ou transferências.
Posições reais e suas identidades permanecem intactas.

As parcelas são transportadas como frações exatas da família aprendida (1/k),
incluindo as parcelas de cash. Não há arredondamento monetário por padrão global
de moeda. budget_reference_capital é apenas referência do orçamento; scenario_amount
e requested_amount continuam ausentes (None). Não é capacidade de sizing validada,
reserva de saldo ou montante de ordem. Candidatas concorrentes compartilham a
identificação de recurso e não devem ser somadas como compromissos de capital.

## Integridade e preservação

O V25 reutiliza a leitura validada dos resultados do V24 e conserva o mesmo resumo
de aprendizagem. Não modifica o código científico ou o namespace de versões do
produtor V24. Não reinicia sua pesquisa por causa de uma alteração na UI.

Confere versões das fontes financeiras antes/depois, hashes dos arquivos de
experimentos, histórico de preços e pesquisa, além de mudanças nas pastas que
podem receber novos experimentos durante a projeção. Alterações deixam a leitura
indisponível para nova tentativa; não produzem contexto financeiro desatualizado.

O novo adaptador não grava arquivos. Não altera SQLite de memória/conversas,
autoconhecimento, modelos, resultados maturados, snapshots, previsões ou ledger.
O ciclo de aprendizado existente permanece em funcionamento. Não faz rede,
ajusta estimadores, cria política manual, inventa limites ou concede autoridade.

## UI e ativação

A seção atual de alternativas econômicas mostra contagens de cenários, contextos
de orçamento/plano e correspondências de fontes/alternativas sem conflito de
identidade. Não exporta os valores de orçamento, contas, instrumentos ou IDs das
candidatas no resumo do diagnóstico. Uma correspondência de fonte não certifica
elegibilidade do broker ou aprovação econômica. As restrições ainda pendentes
aparecem como contagens por motivo.

Nenhuma tag canônica é fabricada, removida ou substituída pela projeção. As novas
informações usam a mesma seção e preservam o estado de abertura e a cadência de
atualização existentes. O modo automático continua desabilitado.

O instalador aplica código com baseline, backup e regressões em cópia temporária.
O ativador V25 reinicia somente o Porquinho identificado, preserva o Bridge e
recusa ciclo ativo/enfileirado. Sem SIGKILL, segundo servidor ou refresh forçado.
Se houver adiamento, repetir apenas o ativador indicado quando o ciclo terminar.
Sucesso de ativação não comprova validade das políticas ou elegibilidade econômica.

## Validação

931 testes Python e 98 verificações JavaScript, sem skips, em pandas 2.2.3 e
3.0.3. Os 25 novos testes cobrem conta/moeda/orçamento/plano, partição de capital,
classes, provedor exato, identidade de pesquisa distinta, horizonte, duplicidade,
zero cash, preservação de blockers, valores de ordem ausentes, privacidade,
leitura sem escrita, mudanças concorrentes e manutenção do resumo original com
fontes verificadas reais em fixture. Todos os dados de testes são sintéticos.

33 testes simulados do ativador. O instalador é validado em aplicação e repetição,
recusa baseline divergente e preserva sentinelas de dados, configuração e CSV.
O patch não conclui A24: custos futuros, liquidez, elegibilidade, política de
utilidade, comparação econômica, sizing, validação prospectiva e publicação
canônica continuam necessários antes de usar as candidatas como decisões.
