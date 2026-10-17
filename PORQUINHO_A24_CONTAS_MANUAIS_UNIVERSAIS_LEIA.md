# A24 — contas universais no modo manual

Premissa confirmada: no Porquinho manual, qualquer conta pode registrar compras/vendas de qualquer instrumento com identidade explícita, respeitando a moeda cadastrada nessa conta. Não há lista de classes de ativos permitidas por banco. O cadastro de corretora ou plano bancário não é necessário para esta compatibilidade administrativa.

## Implementação

Cada alternativa recebe um contexto explícito de compatibilidade da moeda da conta, sem restrição de classe por instituição. O bloqueio genérico INSTRUMENT_VENUE_ELIGIBILITY_REQUIRED deixa de ser imposto às alternativas manuais. O leitor das candidatas reaproveita esse contexto e separa LIQUIDITY_EVIDENCE_REQUIRED do antigo bloqueio combinado de liquidez/corretora; liquidez não é presumida nem removida como requisito econômico.

A moeda declarada na conta é a fonte da regra. País/localidade não criam uma lista fixa BRL/EUR/USD nem reatribuem moedas existentes; o mesmo contrato aceita outras moedas cadastradas. As posições/cash cuja moeda difere da conta continuam recusados. Realoque mantém origem e destino distintos na mesma conta e moeda, sem transferência bancária ou FX implícito.

Saldo, orçamento, intenção do plano, classes escolhidas no plano, identidade explícita, disponibilidade das fontes e demais controles financeiros continuam. A universalidade da conta não significa que toda hipótese esteja adequada ao plano ou que sua recomendação já tenha evidência econômica suficiente.

Compatibilidade manual não comprova capacidade de API ou compra real no banco. A execução automática mantém integração, elegibilidade real, mandato e autorização próprios; execution_enabled não é alterado. Custos futuros não são presumidos, e nenhum modelo/retorno/risco é certificado. Este patch não cria ordem, transação, recomendação canônica ou saldo.

## Preservação e ativação

Somente código é alterado, após backup e regressões em cópia temporária. Não altera posições, transações, moedas, snapshots, memória SQLite, modelos ou histórico; não muda o método/namespace das políticas aprendidas nem os registros prospectivos V29. A UI mostra a regra manual; o resumo informa quantas alternativas são compatíveis na moeda da conta, separadamente da capacidade automática.

Após instalação, tenta ativação controlada V30 somente do Porquinho. Preserva Bridge, sem SIGKILL, segundo servidor, refresh manual ou endpoint financeiro. Se houver ciclo ativo/em fila, repetir somente o ativador indicado em Downloads após o ciclo. O relatório completo permanece local, com saída compacta no Terminal. Ativação e contagens reais ainda precisam ser observadas no Mac.

## Validação

1.019 testes Python e 106 verificações JavaScript em pandas 2.2.3 e 3.0.3; 37 testes simulados do ativador. Inclui compatibilidade universal manual, moeda incompatível recusada, ausência de restrição por país/classe de banco, realocação com duas pernas, preservação dos controles econômicos e ausência de concessão de API. Instalador aplicado e repetido em cópia temporária, recusando baseline divergente e preservando dados/CSV/configuração, com backup único.

A24 continua na consolidação F3/F4. Custos e demais evidências econômicas/canônicas ainda precisam ser concluídos; este patch resolve a regra de compatibilidade manual, não certifica resultados de investimento.

SHA-256 do instalador: `956dce6836efdc0b325c83154450f487dc800435e04bbd93c385709fa62a4e45`.
