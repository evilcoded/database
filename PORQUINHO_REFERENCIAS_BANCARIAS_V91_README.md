# Produtor de referências documentais bancárias — V91

Fonte recebida do site público do banco: https://nubank.com.br/sobre-investimentos/taxas-e-precos, resposta HTTP 200 coletada em 2026-10-22T21:15:42.809889+00:00. Bytes conferidos com SHA256 826eeb9f1b5095cdb21ed5638eaf404157f66c2542611d6d698d614095fb2d37. A tabela publica corretagem zero para renda fixa e variável e serviço zero para ações/BDRs; distingue mesa de operações, custos B3 e taxas de fundos. Não autoriza zerar todos os custos.

Implementa um produtor genérico que lê config/official_bank_component_policies_a24.json e cruza as pernas das ações existentes com instituição, país, moeda, classe explícita do catálogo, lado e canal declarado pelo usuário. A política inicial documenta somente a corretagem bancária zero para renda variável na rota de aplicativo declarada nesta sessão. Não contém tickers, valores de carteira ou IDs de conta. O nome do banco e a condição publicada estão no arquivo de dados; não há ramificação por banco na lógica.

A revisão da fonte é prevista para sete dias após a coleta. É uma política de atualização documental, não uma garantia de validade da tarifa, maturação do Brain ou espera para investir. Expiração, ambiguidade e falta de classe/canal correspondente impedem a aplicação da referência. A declaração de canal registra a escolha de execução manual nos aplicativos dos bancos brasileiros, sem inferir integração ou capacidade de negociação do banco.

Saída: official_bank_cost_references no bridge e resumo na API monitor-consolidation. Cada referência é DOCUMENTED_REFERENCE_NOT_PRETRADE_QUOTE, total_cost continua null e os outros componentes permanecem desconhecidos. Os registros não são inseridos como custos completos revisados, nem recebem validação de modelo. Taxas de manutenção/custódia zero publicadas não são transformadas em custo total de manutenção de investimentos zero.

Este patch configura uma referência parcial de custo. Ainda não produz o rendimento do saldo, custos completos, comparação validada ou recomendações finais. Não altera previsões, parâmetros, aprendizado ou histórico financeiro.

196 testes passaram, com bancos sintéticos, valores zero/não zero, incompatibilidade de classe, canal e país/moeda, expiração, ambiguidade, leitura sem escrita e regressões. Instalador testado em repetição e preservação de bases divergentes. Adiciona um módulo e um arquivo de configuração, modifica dois adaptadores. Backup antes da substituição; nenhum arquivo em brain/ é substituído. Reiniciar somente o Porquinho após terminar o ciclo.
