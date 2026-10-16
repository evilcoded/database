# A24 — Compatibilidade explícita da visão de pesquisa

Problema: posições e fontes revisadas podem usar identificadores diferentes, impedindo a correspondência exata no diagnóstico.

O mecanismo é genérico: lê correspondências direcionais expressamente fornecidas pelo usuário, mantém a identidade original da posição e usa a identidade de pesquisa apenas para consultar fontes já confirmadas na mesma moeda. Não procura por ticker, não altera o ledger, snapshots, modelos, registros de previsões ou cadastros existentes. Não mescla séries históricas e não habilita recomendações canônicas ou execução.

As correspondências reais não fazem parte deste pacote. O comando local recebe `PORQUINHO_REVIEWED_IDENTITY_PAIRS` como JSON de pares completos e grava exclusivamente `data/instruments/research_identity_links_a24.json`, com escopo CURRENT_RESEARCH_VIEW_ONLY. Requer posições atuais com contexto explícito e fontes de destino já confirmadas na moeda da posição. Arquivo existente diferente é preservado e recusado. Repetição idêntica é idempotente.

Contas com estado CANONICAL_ACCOUNT_ID_AS_PROJECTED só são aceitas na visão de diagnóstico se seu ID constar uma única vez no cadastro atual e a moeda for idêntica. Sem coincidência exata, continuam pendentes. Posições de quantidade decimal zero são excluídas do acompanhamento ativo e contabilizadas separadamente.

Antes de instalar, valida hashes das fontes e executa 464 testes Python e 18 verificações JavaScript em cópia temporária sem dados. Backup das fontes modificadas, aplicação atômica por arquivo e rollback em erro. Requer Node e o ambiente Python já existente. Testado com pandas 2.2.3 e 3.0.3. Os testes usam fixtures sintéticas.

O ativador V8 preserva o Bridge, recusa ciclo ativo/enfileirado e nunca envia SIGKILL ou cria um segundo servidor. Verifica hashes, processo, novo snapshot e revisão do endpoint. A comprovação da atualização do diagnóstico independe de um novo resultado do laboratório; a evidência do leitor e a certificação dos modelos permanecem separadas. 33 testes simulados do ativador passaram; ativação real depende da execução no Mac.

Marco atual: consolidação F3 → F4. Compatibilidade de pesquisa não resolve a produção de comparação econômica, sizing e publicação canônica da F4. Nenhuma garantia de desempenho financeiro.
