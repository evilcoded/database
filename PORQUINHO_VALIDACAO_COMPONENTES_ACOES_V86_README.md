# Validação dos componentes das ações — V86

Conecta action_research_handoff ao validador component já existente em economic_component_set_producer_a24, preservando exatamente seus critérios, unidades, escopo e requisitos de proveniência. Não altera algoritmos, pesos, horizontes, arquivos de modelos ou dados.

Cada alternativa com research_readings é avaliada nos cinco contratos existentes: forward_return, transaction_cost, counterfactual_return, relative_utility, risk_measure. Falhas recebem a razão do próprio validador; entradas ausentes não viram zero e nenhum validation_status é reescrito. Resultado disponível no bridge e no campo action_component_validation de /api/research/monitor-consolidation, com contagens e razões. A API expõe somente o resumo, sem os valores dos componentes.

A validação de componentes não valida automaticamente o conjunto completo de alternativas, os custos de uma operação específica, dimensionamento ou publicação. Este patch não escolhe um plano nem produz recomendações finais. Ele conecta e executa a etapa de validação de componentes que faltava após o handoff V85. Com os dados atuais, componentes de pesquisa não validados continuarão reprovados; o patch não supre os modelos ainda ausentes.

113 testes de componentes, handoff, montagem econômica e comparação passaram. Instalador verificado em repetição e base divergente, com backup e checagem integral antes da substituição. Reinicie somente o Porquinho após conclusão do ciclo. Não cria novas regras quantitativas nem um bloqueio por maturação de 30 dias.
