V112 — coleta restrita do motor original

Exporta apenas parâmetros numéricos conhecidos de action_rules, max_positions, position_sizing.max_position_pct e discovery_top_n; flags trained/calibration_usable e os cinco pesos kpi_weights; métricas numéricas e ações reconhecidas dos scores salvos; hashes de três arquivos de código. Não exporta config.json, seu hash, credenciais, contas ou modelos completos. Scores salvos não são reavaliados ou certificados.

Não importa código do aplicativo, não acessa rede, não inicia ciclos, não reinicia serviços e não modifica parâmetros, modelos, carteira ou histórico. Cria um ZIP privado em Downloads. Esta coleta não ativa recomendações.

Três testes sintéticos verificam a lista restrita de campos, ausência de credenciais, preservação dos arquivos, dados ausentes, links simbólicos e tipos inválidos. Sintaxe Bash verificada.
