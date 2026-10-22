# Pesquisa BRAPI V72

Adiciona BRAPI ao planejador e coletor existente de pesquisa financiada por planos. Consome apenas vínculos explícitos únicos por instrumento/moeda, com plano e contexto atuais. Não descobre ativos, não modifica vínculos, moedas ou orçamento e não altera modelos, scores, features ou regras de análise. O caminho CoinGecko mantém o transporte e as verificações existentes.

BRAPI: uma rota por chamada do coletor, com rotação entre rotas pendentes (sem ranquear investimentos), sem repetição automática diante de HTTP 429. Grava no mesmo diário encadeado e imutável, com deduplicação por instrumento/provedor/moeda/dia UTC. Exige símbolo e moeda correspondentes, preço válido e timestamp atual. Preserva o limite original de 30 minutos, mesmo dia UTC e tolerância de 30 segundos para relógio adiantado. Não converte uma referência antiga do radar em observação nova. Valores ausentes de capitalização e volume permanecem desconhecidos.

Revalida contexto financeiro e digest dos vínculos antes da consulta e antes da gravação. Fontes com múltiplas rotas continuam exigindo seleção explícita. Classes fora dos planos ativos continuam excluídas; o patch não amplia a autorização dos planos. Registra resultados por provedor e totais no retorno do coletor. O monitor deve receber isso pelo ciclo existente; não há ciclo adicional criado pelo patch.

Não recupera histórico, reprocessa modelos, muda aprendizados, impõe espera de 30 dias, cria recomendação ou executa ordens. Habilitar a captura não garante uma sugestão imediata nem comprova que todos os produtores posteriores já cobrem cada classe brasileira. Respostas atrasadas/fora do horário de mercado podem ser recusadas para pesquisa mesmo quando válidas como referência de radar.

Validação: 69 testes de pesquisa BRAPI, regressões CoinGecko e vínculos explícitos, com rede simulada. Instalador compilado, backup e idempotência verificados. Requer reinício do Porquinho depois de concluir ciclos em andamento. Dados financeiros e modelos preservados; novos ciclos poderão acrescentar observações de pesquisa válidas ao diário existente.
