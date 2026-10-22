# Contexto de cotação V73

Adiciona diagnóstico de idade e sessão declarada pelo provedor à aquisição BRAPI. Sem calendário verificado no projeto, a sessão permanece UNKNOWN quando a fonte não informa marketState. Não infere abertura/fechamento pelo horário, dia da semana, país ou ticker. Estado declarado não equivale a calendário independente. Atraso contratado permanece desconhecido, sem assumir que a quota ou plano garante preço em tempo real.

Preserva as regras do diário: 30 minutos, mesmo dia UTC e tolerância de relógio de 30 segundos. Cotações antigas não são publicadas como observações novas, mesmo fora da sessão. Não altera modelos, aprendizado, critérios de recomendação ou a base histórica. Não implementa calendário, fechamento diário ou backfill.

Resultado da última tentativa disponível em results/brapi_research_diagnostic_a24.json, substituído atomicamente, com rota, moeda, status, data/idade e contexto da fonte. É diagnóstico operacional, não série de mercado ou entrada de modelo. Não exporta token nem contextos privados de contas. Novos ciclos gravam esse diagnóstico; o instalador só altera código, com backup e verificação de base. Não há mudança de interface neste patch.

46 testes de contexto de fonte, aquisição BRAPI e regressões CoinGecko, com rede simulada. Instalador e idempotência verificados. Reiniciar Porquinho após ciclos concluídos e ler o diagnóstico depois de uma tentativa BRAPI. A captura pode continuar recusada enquanto o provedor retornar dados antigos: o patch torna a causa visível, sem fabricar atualidade.
