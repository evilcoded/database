# A24 — patch 1: capital por conta/moeda → demanda de pesquisa

Primeira implementação do fluxo definido pelo usuário: instituições → contas → capital por moeda → acompanhamento. A prioridade passou a ser a implementação; não requer concluir previamente a exploração de instrumentos. Não encerra a A24.

## Comportamento implementado

Reutiliza o modelo de leitura canônico existente, o cadastro de instituições/contas e os stores de Planning Budget e Investment Plan. Não cria outro ledger, cadastro de saldos, modelo de preços ou fonte de autoridade financeira. A leitura não cria arquivos de dados.

Identifica contextos com cash canônico positivo por account_id/currency. A moeda vem do cash e precisa coincidir com o cadastro da conta; a localidade vem da instituição. Não deduz moeda ou elegibilidade pelo país. BRL/EUR/USD não são whitelist: o contrato aceita códigos explícitos ASCII alfabéticos em maiúsculas de até 16 caracteres, incluindo moedas fiat e códigos de pesquisa como XAU/USDT. O cadastro atual tem uma denominação explícita por conta; uma denominação adicional não cadastrada permanece pendente, sem conversão implícita.

Cash positivo ativa demanda de observação, independentemente da existência de posições nessa moeda. Cash sem orçamento não é apresentado como capital investível: o contexto registra CASH_DETECTED_INVESTMENT_BUDGET_REQUIRED e investment_budget_amount=null. Somente orçamentos ACTIVE seguros e compatíveis fornecem o montante de intenção de investimento; a soma precisa caber no cash atual. Não inventa reservas ou disponibilidade bancária livre a partir de saldo Pluggy observacional. Saldo somente observacional, sem origem canônica aprovada, não é promovido.

Planos ativos compatíveis delimitam classes para a pesquisa; múltiplos planos ativos para o mesmo orçamento, autoridade inesperada, moeda/conta conflitante ou orçamento superior ao saldo bloqueiam o contexto. Sem plano, a demanda é de observação exploratória; não comprova elegibilidade de compra. O contexto inclui planos/estratégias/horizontes declarados e orçamentos por ID. Alterações de saldo, estratégia, horizonte ou distribuição dos orçamentos invalidam seu fingerprint.

Gera demandas estáveis por conta + instrumento existente + moeda de observação. A identidade do instrumento é preservada, inclusive IDs com quatro/cinco componentes. A moeda original do candidato não vira moeda-base da pesquisa. Um instrumento já observado em EUR pode ter demanda em BRL por causa do capital da conta, sem exigir posição BRL anterior.

Consome somente candidatos já selecionados pelo bridge do Brain. Não inventa universo global, não transforma referência de catálogo em descoberta e não renomeia os IDs legados da carteira. As limitações atuais de descoberta e vínculos continuam explícitas.

O resultado é levado ao ciclo shadow em intelligence.funded_currency_research. O endpoint GET /api/research/funding-contexts expõe a mesma projeção; POST não é permitido. Não há painel novo nesta etapa. Fontes ausentes ou inválidas retornam UNAVAILABLE sem fallback de saldos observacionais; o restante da observação do Brain continua separado dessa indisponibilidade.

## Limite deste primeiro patch

Esta etapa projeta e disponibiliza demandas de pesquisa. Não coleta cotações novas, executa FX, agenda treinamento, amadurece modelos automaticamente ou cria recomendações/ordens. A ligação destas demandas à aquisição e à maturação multimoeda é o próximo patch; não deve ser confundida com capacidade já entregue.

Vínculos explícitos existentes são apresentados somente como candidatos para revisão da fonte, sem atestado independente. Na ausência deles, a demanda registra EXPLICIT_PROVIDER_QUOTE_BINDING_REQUIRED. Não há associação por ticker.

Manual é o único modo efetivo. O contexto mantém conta, moeda, orçamentos, política de delegação ausente e exigências de revalidação de capital/elegibilidade/sizing/idempotência. Esses campos são um contrato para integração futura, não um executor implementado. execution_authorized e automatic_execution_authorized permanecem false, inclusive em conta CONNECTED_EXECUTE. Capacidade de negociar ETH no Brasil, transferência para corretora e delegação dependerão de validações próprias; país ou saldo não concedem essas capacidades.

Não reutiliza uma previsão EUR como evidência BRL validada. Não toca registros, aprendizado, memória ou modelos anteriores e não autoriza publicação canônica.

## Instalador

Verifica baseline exato dos patches anteriores e fontes de leitura/planning. Altera universal_observation_bridge.py e webapp/server.py; adiciona funded_currency_research_a24.py e 35 testes novos. Valida 296 testes offline em cópia temporária antes de gravar, cria .porquinho_a24_funding_backup_* e confere hashes finais. Reexecução idempotente. Prefere o Python da .venv; usa Flask/NumPy/pandas/scikit-learn já usados pela aplicação, sem instalar dependências no Mac.

Não reinicia serviços ou solicita compra, venda, movimentação, coleta de mercado ou treinamento. A ativação no processo em execução permanece separada; o ativador anterior não possui estes novos hashes.

Após aplicação, um subprocesso -I -B, com escrita/rede/processos bloqueados por audit hook, lê as fontes reais e imprime apenas contagens e moedas reconhecidas, motivos de pendência e número de demandas. Não exporta saldos nem IDs de contas. Não prova ativação do processo da UI. Falhas nessa leitura são reportadas separadamente da instalação.

## Verificação

296 testes offline aprovados com pandas 2.2.3 e 3.0.3. Incluem 35 casos novos: capital BRL sem posições BRL, outras moedas sem whitelist, país independente da moeda, precisão Decimal, separação de contas/moedas, orçamento sobrealocado, ausência de orçamento, autoridade, políticas de planos, fingerprints, wiring no bridge e rota Flask real GET-only com fontes simuladas.

Instalador aplicado e repetido em raiz temporária: 296 testes em cada execução; baseline divergente recusado antes de gravar; arquivo sentinela de dados preservado. Não houve execução financeira.

Mais 17 testes existentes de Planning Budget/runtime/Investment Plan passaram com pytest no cloud. A suíte antiga test_canonical_runtime_read_model_g14.py teve três falhas por ausência dos arquivos privados de abertura/cutover no pacote de fontes; esses casos não integram a regressão offline, e não foram alterados ou desabilitados. A leitura real do cash no Mac continua sendo evidência local necessária; nenhuma fixture de capital real foi fabricada no cloud.
