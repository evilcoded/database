# Restauração de histórico brasileiro V78

Recebe caminho local e SHA256 esperado como argumentos; nenhum dado de mercado ou hash específico do usuário está embutido no código. Valida schema equity-historical/1.0, séries, datas, unicidade diária e consistência/positividade OHLC. Preserva bytes exatos da origem. Cria arquivo de recuperação em data/recovered_market_sources_a24/{sha}/ohlcv.json, manifesto de origem USER_SUPPLIED_RECOVERED_COPY e restaura data/equities/historical/daily/ohlcv.json somente se ausente. Um destino idêntico é preservado; destino diferente nunca é sobrescrito. Publicação de arquivo por hard-link de temporário no mesmo diretório para não sobrescrever um destino criado concorrentemente.

Sem rede, treinamento, reprocessamento de resultados ou alteração de pesos. Restaura dados de mercado e cria arquivos de rastreio; não modifica posições, caixa, contas ou dados financeiros. Nenhum arquivo do usuário é publicado no GitHub.

Depois da restauração, inspeciona pacotes históricos BRAPI selados já disponíveis e compara dias comuns de fechamento bruto por alegação de namespace do provedor. Usa apenas metadados explícitos para encontrar candidatos, registra coincidências e divergências, sem juntar preços, inferir moeda ou promover identidade histórica. AjustedClose é preservado no arquivo original e não é usado nessa comparação de fechamento bruto. Coincidência numérica não atesta identidade, moeda ou ajuste corporativo. Preserva qualquer divergência para revisão.

Relatório em Downloads contém contagens, intervalos de datas, evidências de origem e resultados de comparação; não contém os pontos de preço nem credenciais. Histórico recuperado permanece com suas datas antigas, não é apresentado como atualizado. A UI BRL e a validação das recomendações continuam como trabalho pendente após a conexão de fontes compatíveis.

Validação: sintaxe shell/Python, validação de arquivo recuperado, restauração exata, idempotência e preservação de destino divergente; comparação contra um pacote selado sintético com 30 dias comuns e uma divergência identificada, sem união automática. O script não precisa de reinício de serviços e não inicia ciclos.
