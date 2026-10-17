# A24 V37 — painéis de patrimônio, meta e experiência universal

Reorganiza a interface a partir dos painéis solicitados, preservando identidade visual, rotas administrativas, Brain, modelos, memória, aprendizado, snapshots e histórico. Não altera o algoritmo de decisão ou executa operações financeiras.

## Distribuição

- Visão geral: Patrimônio Total com informações de origem e minigráfico, Meta do Porquinho semanal, Estado do Sistema, Evolução do Patrimônio, ações pendentes do Brain, Alocação de Ativos, Desempenho por Ativo e Insights factuais.
- Carteira: Performance da Carteira vs Benchmark, posições e alocação. Seleção explícita de benchmark/fonte/moeda e períodos 7D/1M/3M/6M/1A/Tudo.
- Cockpit Brain: Próximo alvo de maturação em destaque, com horizontes futuros, maturados e vencidos ainda pendentes; demais diagnósticos anteriores preservados.
- Contas e Bancos: painel de cash registrado por conta no topo; controles administrativos originais mantidos abaixo.
- Oportunidades: Top Oportunidades em destaque, com avaliações e ações já recebidas do motor; comparações de realocação abaixo.
- Transações: Últimas transações verificadas no topo, filtros de moeda/conta e histórico completo anterior preservado.
- Mercado Global: Mercado Visão Geral em destaque; histórico diário, intraday e variações/fontes abaixo.

Cartões compactos, áreas e linhas em verde, alocação colorida, botões de períodos/seleção, indicadores e informações em popups. Não copia números ilustrativos da imagem. Não transforma referências de pesquisa em avaliação financeira de uma posição.

## Patrimônio e benchmark

Lê snapshots armazenados; usa o último arquivo nomeado por dia, até 366 dias, com limites de leitura e hash de origem. Nunca calcula posições passadas com quantidades atuais nem usa a tabela portfolio_daily hidratada como prova de evolução observada. Moedas globais explícitas são mantidas separadas. Snapshots compatíveis com o contrato legado de cash EUR e somas do produtor são mostrados como referência legada EUR, não como histórico financeiramente atestado de cada instrumento. Snapshots sem contexto ou totais consistentes são omitidos, sem modificação do arquivo original. Referência legada sem conta não é atribuída a uma conta filtrada.

Patrimônio atual usa posições com contexto exato quando completo; na falta, mostra o último registro compatível com origem/data visíveis. Ausência não vira zero. Cash e posições nos subindicadores mantêm o mesmo contexto temporal do total exibido.

Benchmark compara percentuais ancorados na mesma primeira data e somente em datas comuns, na mesma moeda. A curva de patrimônio inclui depósitos, retiradas e transações. Não é retorno ajustado a fluxos, alpha ou certificação; horários das amostras diárias não são uma marcação intraday sincronizada. A UI informa essa limitação. Cotações por instrumento/fonte não são associadas a posições por ticker. Dados insuficientes geram mensagem explícita.

## Meta semanal

Reutiliza contratos e APIs de meta semanal já existentes, vinculados a plano e orçamento ativos. Exibe capital de referência, objetivo monetário/percentual e estado de rascunho registrado. Botão Ver/definir meta semanal permite calcular objetivo e, após ação explícita, registrar o rascunho pelo endpoint existente. Não substitui metas já registradas. Não exige informar limites de alocação ao Brain, não cria quota, autoridade ou ordem e não garante retorno.

Progresso semanal permanece explicitamente não reconciliado quando não há janela/desempenho verificados; não trata depósitos ou crescimento do patrimônio como lucro semanal. Sem plano elegível, direciona às contas e planos existentes. Este patch não cria planos, orçamentos, treino ou operações para preencher o cartão.

## Fontes e preservação

Maturação lê estados/datas armazenados nos episódios, sem recalcular outcomes ou inventar vencimentos. Maturação não bloqueia sinais atuais nem aprova modelo. Transações usam projeção do ledger verificado; execução não é inferida de sinais/ordens. Painéis adicionais são lidos apenas na projeção financeira já usada pela UI; diagnóstico agregado padrão não exporta objetivos, preços ou transações individuais. Relatório do ativador contém apenas contagens/estado dos novos painéis.

Únicas mutações novas possíveis pela UI: registro explícito de rascunho de objetivo no contrato de planejamento existente. Instalador e leitores não modificam dados, metas, modelos, memória, snapshots ou históricos. Realocações sem custos/sizing continuam sem instrução ou valor final. Intraday mantém a referência e cadência legada já identificadas, não cria dados de um minuto.

## Verificação

1.107 testes Python e 187 verificações JavaScript nos ambientes pandas2/3; 38 simulações do ativador, inclusive redação dos novos campos privados. Chromium sintético desktop/mobile: composição dos painéis, patrimônio observado, períodos/moeda, benchmark, maturação, destaques, transações/contas com controles originais, popups e fluxo explícito de preview/draft da meta. Duas chamadas POST simuladas somente de planejamento, zero POST financeiro; consulta inicial compartilhada e atualização explícita após salvar. Sem erros JavaScript ou overflow horizontal. Fixture isolada não equivale ao Mac real.

Instalação e repetição em cópia temporária, divergência de baseline recusada, backup único e sentinelas de dados/CSV/config preservadas. Ativador V37 verifica hashes, preserva Bridge e não usa SIGKILL/segundo servidor/refresh financeiro. Ciclo ocupado: repetir somente o ativador indicado. Depois de ativar: Command+Shift+R.

Ativação anterior V36 confirmada por relatório local. V37 depende da execução local e conferência das fontes realmente presentes. F3/F4 não são encerrados nem modelos certificados por uma mudança de UI. O pacote público contém somente código, fixtures e logs sintéticos.

SHA-256 do instalador: `b1d82b3c22df8fd11f041e8f2a4a5ec46cd8148aeddb2f2b3727264097ab260f`.
