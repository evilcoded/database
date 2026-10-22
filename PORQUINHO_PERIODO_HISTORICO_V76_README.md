# Período de histórico V76

Configura a requisição BRAPI para 3mo/1d, conforme o erro INVALID_RANGE e os limites informados pela API no diagnóstico do usuário. Não cria regra para plano gratuito, não solicita upgrade e não muda critérios do Brain.

O período é dado em config/market_history_requests_a24.json, schema porquinho.history-request-settings/1.0, providers.brapi.range e interval. Uma futura alteração de cobertura pode ser refletida nessa configuração, sem alterar métodos dos modelos. O adaptador valida parâmetros conhecidos, sem inferir permissões do plano. Se já existir configuração diferente, o instalador a preserva e cancela por divergência.

Pacotes com janelas diferentes têm identidades distintas. Três meses não é registrado como 365 dias: requested_days fica desconhecido e requested_range/request_parameters preservam a requisição efetiva. O seletor de fontes do laboratório passa a identificar a janela configurada; esse ajuste afeta a localização dos dados, não os cálculos, horizontes, mínimos de treinamento ou validação. IDs e pacotes CoinGecko anteriores permanecem iguais. As tentativas anteriores recusadas são preservadas sob suas identidades originais.

O intervalo diário, a semântica de fechamento e os campos de ajuste não verificado do V75 continuam. Nenhuma série histórica é confundida com capturas prospectivas. Histórico limitado pode ser insuficiente para alguns experimentos; o patch não reduz requisitos nem força sugestões. O processo normal pode criar novos experimentos isolados com fontes suficientes, sem substituir os modelos armazenados pelo instalador.

A auditoria tools/trace_brapi_history_v75.py agora inclui o período requisitado. Após instalar, reiniciar somente após concluir ciclos e executar a auditoria depois de um ciclo. 107 testes de configuração, identidade, seleção de fontes, adaptação BRAPI e regressões dos laboratórios e histórico CoinGecko, com fontes simuladas. Instalador e idempotência verificados. A aceitação da requisição 3mo será verificada no Mac.
