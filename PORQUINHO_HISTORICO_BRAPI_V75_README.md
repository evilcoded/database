# Histórico BRAPI V75

Adiciona ao coletor histórico existente uma rota por ciclo para BRAPI: /api/quote/{provider_id}?range=1y&interval=1d. Usa o vínculo explícito e exige resultado único com símbolo e moeda correspondentes. Histórico precisa conter historicalDataPrice, com datas e fechamentos positivos finitos. Recusa duplicidade diária, futuro e pontos fora da janela; exclui o dia UTC atual. Sem interpolação, FX ou retropreenchimento do diário prospectivo.

Os fechamentos BRAPI têm sampling e pricing_method específicos, com ajuste corporativo não verificado. A série_id também incorpora essa semântica, sem alterar IDs CoinGecko existentes. Capitalização e volume_24h permanecem desconhecidos: não converte volume diário em volume financeiro/24h. Não chama esses preços de retorno total, não presume ajuste por dividendos e não certifica disponibilidade histórica de forecasts.

Preserva o formato de pacote selado, validação por reconstrução, backup, contextos de financiamento, hashes de vínculos, limite de uma requisição histórica por ciclo e registro de tentativa com janela de seis horas. Mantém os pacotes anteriores intactos. Usa o laboratório existente sem alterar método, treinamento mínimo, horizonte ou critérios. Os ciclos normais poderão criar novos experimentos de pesquisa isolados com as novas fontes, conforme o comportamento já existente do laboratório; o instalador não executa treinamento nem altera modelos armazenados.

Não garante cobertura histórica do plano BRAPI. Dados ausentes ou recusados ficam registrados como fonte indisponível. Captura diária e histórico adquirido agora continuam separados. Não publica recomendações finais nem ordens automaticamente.

Inclui tools/trace_brapi_history_v75.py: leitura dos pacotes selados e metadados de experimentos armazenados, sem rede ou execução de modelos. Gera ZIP em Downloads. Campos de status do experimento são os armazenados; a auditoria não reexecuta a validação matemática do modelo.

102 testes de adaptação histórica BRAPI, regressões do histórico CoinGecko e laboratórios existentes, com fontes simuladas. Instalador e idempotência verificados. Validação ao vivo ocorrerá no Mac usando o acesso configurado; reiniciar após conclusão dos ciclos para carregar o patch.
