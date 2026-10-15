# A24 — revisão explícita de vínculos, caso a caso

Esta entrega cria o mecanismo de revisão e conecta vínculos revisados à aquisição diária existente. Não cria vínculos reais nem encerra a A24. Requer os patches globais V2 e de reconciliação já instalados; verifica os hashes coletados no preflight local.

## Revisão e fonte de autoridade

A nova ferramenta tools/market_provider_bindings_a24.py consulta identidades exatas dos arquivos existentes data/universal_instrument_catalog.json e data/instruments/manual_instruments.json. A existência no catálogo valida apenas a referência da identidade: não comprova posse, correção econômica, associação a provedor ou cotação. IDs com qualquer número de componentes são preservados literalmente, inclusive os IDs de quatro e cinco componentes encontrados localmente.

Cada linha revista exige instrument_id, provider, provider_id, quote_currency, identity_source_ref, confirmed_by, confirmed_at e effective_from. Não há inferência por ticker, holdings, formato do ID, moeda de conta ou sufixo _eur. O vínculo é uma declaração local de pesquisa, não atestado independente; não muda os resolvedores antigos nem seus contratos de três componentes para fingir compatibilidade ou autoridade.

O primeiro passo é escolher um instrumento da ficha local e conferir separadamente a identidade do instrumento e a referência no provedor. A ficha contém campos em branco e não é válida para aplicação. Não é necessário preencher todos os instrumentos: linhas ainda não revisadas devem ser removidas do documento destinado à aplicação. A geração de fichas futuras preserva as linhas já registradas.

Para cada caso, a aplicação exige o digest do documento revisado e o digest do registry anterior. A ferramenta recusa remoção/regravação de vínculos anteriores, duplicatas, conflitos da mesma chave provider/provider_id com identidades diferentes, moedas inválidas e confirmação sem timezone. Novos vínculos exigem confirmação no dia UTC atual e effective_from não anterior ao dia atual; a validação para leitura de vínculos antigos continua funcionando. Não permite retroagir a confirmação para construir prova histórica.

O registry data/instruments/market_provider_bindings_a24.json só é criado pelo subcomando apply explicitamente invocado depois da revisão. Tem lock exclusivo, escrita atômica, permissão 0600 e backup na ampliação. Não é um novo ledger financeiro, cadastro de contas, modelo ou fonte de autoridade canônica. O patch não altera modelos ou dados para simular registros resolvidos.

## Aquisição

fetch_daily conserva o contexto da requisição efetiva e consulta o registry. Aplica a identidade e a referência somente quando provider/provider_id/quote_currency correspondem exatamente ao vínculo revisado e a observação é da data effective_from ou posterior. Provider compara sem distinção de maiúsculas; provider_id e moeda são estritos. Conflito entre identidade recebida e revista é recusado. Registry ausente continua NO_APPLICABLE_EXPLICIT_BINDING, sem inventar associação; registry inválido gera falha explícita. Contextos de pesquisa auxiliares recebem a identidade de cada linha, mantendo suas restrições de autoridade.

A gravação do coletor continua somente para datas/ativos novos. Linhas já existentes não recebem metadados retroativos, não são substituídas por preços recém-consultados e não passam a ser prova prospectiva. O teste de integração executa aquisição simulada e merge reais, preserva a linha anterior e verifica repetição byte a byte sem novas datas.

O contrato dos vínculos é global e não fixa moeda-base nem lista de países. O adaptador ativo continua sendo o CoinGecko já existente: sua chamada legada pede EUR e só pode usar vínculo explicitamente correspondente a esse pedido. A função diária também aceita outra quote_currency explícita. Este patch não adiciona provedores de outras classes nem habilita automaticamente coleta multimoeda na tabela legada, cujos consumidores ainda têm limitações por símbolo/data. Vínculos de outros provedores ficam disponíveis como declarações, sem provocar chamadas a provedores não implementados. A moeda de cotação não preenche a moeda da conta.

Nenhuma confirmação local certifica modelo, retorno esperado ou sizing. Tudo continua RESEARCH_ONLY, SOURCE_UNATTESTED, sem treinamento solicitado, FX, promoção ou execução financeira.

## Instalação e ficha

O instalador executa 261 testes offline em cópia temporária, confere hashes e cria backup .porquinho_a24_bindings_backup_*. Modifica tools/fetch_history.py e o namespace de um teste de aquisição; adiciona o contrato, a CLI e 28 testes. Não reinicia serviços, aciona coleta, grava registry ou altera dados/modelos/memória/histórico. Prefere o Python da .venv, com NumPy/pandas/scikit-learn já usados pelo projeto.

Após aplicar o código, consulta status e cria exclusivamente uma ficha fora do projeto, em Downloads/PORQUINHO_A24_REVISAO_VINCULOS_*.json. A ficha usa as identidades locais e não é incluída neste pacote público. Falha na preparação da ficha é reportada separadamente, sem apagar a aplicação do patch. Reexecução idempotente não recria ficha automaticamente.

Comandos disponíveis, executados na raiz do projeto com .venv/bin/python -B tools/market_provider_bindings_a24.py:

- status: somente leitura, contagem de identidades e vínculos.
- template --output CAMINHO_FORA_DO_PROJETO [--instrument-id ID_EXATO]: ficha com campos vazios; preserva arquivo de destino já existente.
- validate --file FICHA: somente leitura; devolve review_digest e current_registry_digest.
- apply --file FICHA --review-digest DIGEST_REVISTO --expected-registry-digest DIGEST_ANTERIOR: grava somente o documento explicitamente revisado. Será usado depois da revisão caso a caso, não pelo instalador.

A ativação no processo vem depois da revisão. O ativador V4 verifica hashes anteriores e não deve ser usado como prova de ativação deste novo patch; a ativação seguinte precisará destes novos hashes.

## Verificado no cloud

261 testes aprovados em pandas 2.2.3 e 3.0.3. Incluem 28 casos novos: ciclo de revisão/aplicação, conflito de identidade, múltiplas cotações para o mesmo instrumento, ausência explícita, idempotência, backup, preservação de formatos, recusa de confirmação retroativa, fichas e aquisição/merge em diretório temporário. Compatibilidade corrigida para preservar None como objeto nas colunas opcionais do pandas 3.

O instalador passou aplicação e repetição com 261 testes por execução, recusou fonte divergente antes de gravar, preservou todos os arquivos de dados da fixture, não criou registry e gerou ficha externa com provedor vazio. O código real do Mac não foi executado pelo assistente; a evidência local será a saída do instalador.
