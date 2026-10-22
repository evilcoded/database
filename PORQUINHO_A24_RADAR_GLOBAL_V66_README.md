# Radar global V66

Substitui o uso de `radar_seed` no radar HTTP (`MarketDataService.radar_snapshot`) e na pesquisa local (`AssetResolver`) pelos catálogos globais existentes. A lista legada não é apagada: outros módulos históricos e diagnósticos ainda podem usá-la.

O radar lista todo instrumento registrado, inclusive sem fonte. Rotas de cotação exigem o registro explícito já existente, com provedor, ID e moeda. Não associa símbolos automaticamente. Conflitos ficam pendentes. As consultas CoinGecko usam a moeda da rota, sem EUR fixo; o adaptador BRAPI usa o ID explícito e exige moeda na resposta. Outros provedores exigem adaptador; nenhum preço é inventado. Novos instrumentos não exigem alteração da lista no código.

Não descobre automaticamente todo o mercado, não cria vínculos B3 ausentes e não publica sugestões finais. Não altera seleção global, modelos, histórico, pesos, orçamento, posições ou regras do Brain. Não muda o coletor operacional legado de `porquinho.py`, nem produtores históricos de renda fixa e ações. Não certifica disponibilidade do ativo em um banco.

Mudança de contrato: `/api/market-data/radar` retorna uma linha por instrumento/rota de moeda (podem existir várias moedas/provedores para o mesmo instrumento). Linhas sem vínculo têm preço e moeda de cotação desconhecidos. Preços são referências com data, nunca preços executáveis. Não reutiliza nem grava o cache antigo indexado apenas pelo símbolo. Falhas de rede mantêm os instrumentos e as pendências, sem substituir por preço antigo de outra rota.

Instalador verifica hashes antes das alterações, cria backup, é idempotente e não inicia serviços. Reiniciar somente o Porquinho após concluir ciclos em andamento. Testes: 62 verificações de radar, transporte, vínculos explícitos e leitura global; rede dos provedores simulada, sem validação ao vivo do BRAPI nesta entrega.
