# Passagem de pesquisa para ações candidatas — V85

Escopo deliberadamente restrito: anexa os componentes de pesquisa existentes às ações candidatas já construídas pelo sistema. Integração no observation bridge, usado pelo ciclo, e resumo action_research_handoff na API monitor-consolidation. Não substitui envelopes econômicos existentes e não altera decisões, pesos, treino, horizontes ou algoritmos do Brain.

Correspondência exata por instrumento, conta, moeda, impressão do contexto de orçamento e horizonte de cada componente. Mais de uma fonte coincidente é ambiguidade explícita; não se escolhe uma fonte arbitrária. Caixa sem modelo contrafactual permanece pendente. Nenhuma identidade é inferida por ticker.

Os componentes são transportados como research_readings, mantendo valores, proveniência e validation_status, sem se passarem pelo contrato components validado do comparador. A pesquisa não é, por si, validação específica de compra, venda ou manutenção. comparator_ready permanece false nesta passagem. Este patch não implementa ainda a validação econômica por ação, dimensionamento ou publicação final. Não resolve a ausência de conjuntos governados sozinho.

Validação: 106 testes de passagem, escopo econômico, montagem de componentes e pesquisa; instalação repetida e preservação de base divergente. O instalador valida todos os arquivos antes de substituir, faz backup e compila Python em memória. Modifica dois adaptadores e adiciona um módulo de transporte. Não modifica arquivos de dados nem modelos. Reiniciar somente o Porquinho após conclusão do ciclo.
