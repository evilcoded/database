# A24 — patch 2: aquisição de pesquisa por moeda financiada

Consome as demandas do patch de capital por conta/moeda. Mantém casos sem vínculo explícito como pendentes. Não cria ou confirma vínculos reais, não resolve instrumentos por ticker e não concede autoridade financeira.

## Implementado

Novo research_quote_acquisition_a24.py, chamado no ciclo normal após a composição shadow. Usa somente demandas atuais de observação com contexto íntegro e execução desabilitada. Lê novamente o registry explícito: source_candidates recebido numa demanda não é prova de vínculo. Confere vigência, identidade/provedor/provider_id/moeda, política de classes e ausência de ambiguidade de fonte. Mais de uma fonte aplicável exige escolha explícita.

Revalida os fingerprints dos contextos contra o cash/planning atuais antes das chamadas e novamente antes de gravar; confere que o registry não mudou. Não gasta o saldo ou o orçamento: são contexto da demanda de pesquisa, não autorização de compra.

O primeiro adaptador é CoinGecko. Usa GET /simple/supported_vs_currencies e GET /simple/price com IDs e moedas explícitos, last_updated_at, capitalização e volume 24h quando disponíveis. Outras moedas não são whitelist; precisam ser suportadas pela fonte e pelo vínculo. Uma moeda ausente/indisponível fica pendente, sem converter EUR/USD silenciosamente. Não usa o país do banco como moeda, provedor ou canal de negociação. Provedores ainda não implementados ficam PROVIDER_ADAPTER_NOT_IMPLEMENTED.

Reutiliza o resolvedor seguro de credenciais já usado pelo Provider do Porquinho, sem exportar valores. Restringe HTTPS aos hosts oficiais api.coingecko.com/pro-api.coingecko.com, mantém TLS, bloqueia redirecionamentos, limita resposta a 2 MiB e usa timeouts de seis segundos por chamada. Falhas HTTP aparecem por código, incluindo 403/429, sem corpo ou credenciais nos relatórios. Há limite de 50 pares por ciclo, no máximo 100 mediante configuração interna, com rotação e demanda restante explícita. Antes da chamada de preços e da gravação, há verificações de orçamento de tempo; timeouts HTTP continuam sujeitos às características de leitura da biblioteca de rede.

Sem vínculo elegível: zero chamadas, sem carregar credenciais e sem criar arquivos de observação. As 127 demandas reais do último relatório estavam nesse estado. A instalação deste código não muda esse fato: a coleta real depende da revisão dos vínculos e da ativação do código.

## Dados de pesquisa

As novas observações vão exclusivamente para data/brain/research_quote_observations_a24/YYYY-MM-DD.jsonl, com partições UTC e cadeia hash local por dia. Não mistura novas moedas na chave legada data+ativo de market_daily.csv. Planejamento e escrita consultam apenas a partição do dia; a leitura histórica pode percorrer partições sem mudar o formato das identidades.

Chave: identidade literal + provedor + provider_id + moeda + dia. Duas contas podem compartilhar uma observação de mercado; IDs de contas, saldos e orçamentos não são gravados no journal. A primeira captura válida do dia é imutável e não representa fechamento de mercado. Reexecução no mesmo dia não repete a chamada de preços para pares já capturados. Dias novos adicionam arquivos, preservando o histórico. Escritores usam lock exclusivo, append e fsync; corrupção/linha parcial é detectada e não é reparada ou sobrescrita automaticamente.

Exige preço positivo finito e timestamp do provedor no dia UTC corrente, com no máximo 30 minutos de idade e tolerância futura de 30 segundos. Campos auxiliares ausentes continuam null. volume_24h é volume móvel informado pelo provedor, não soma do dia civil. O fingerprint da resposta é do JSON decodificado normalizado, não atestado de arquivo externo independente.

Mantém source_availability_attested=false, independent_archive_verified=false, provider_internal_fx_verified=false, FX do Porquinho=false e autoridade RESEARCH_ONLY/NOT_VALIDATED. Uma cotação agregada do provedor em BRL não comprova negociação numa corretora brasileira ou preço executável. Nenhuma observação promove modelos, decisões ou sizing.

Este patch grava novas observações quando houver vínculos aplicáveis. Ainda não liga o novo journal ao treino/maturação do laboratório, nem altera previsões EUR antigas: essa integração é a etapa seguinte. A ausência de dados novos enquanto os vínculos estão pendentes não será apresentada como erro de modelo ou ciclo concluído.

## Runtime e instalação

O resultado agregado fica em universal_shadow.funded_currency_acquisition na resposta do ciclo normal. GET /api/research/acquisition-plan mostra somente o plano agregado e não coleta; POST não é permitido. Não cria serviço, worker ou agendamento paralelo. Não adiciona painel de interface nesta etapa.

O instalador modifica webapp/server.py e adiciona o adaptador e 33 testes. Executa 329 testes em cópia temporária antes de gravar, exige os hashes do patch de capital e cria backup .porquinho_a24_acquisition_backup_*. Não coleta dados, lê credenciais, reinicia serviços, treina modelos, cria ordens ou muda políticas de delegação. Preserva dados/modelos/memória/histórico existentes. Reexecução idempotente.

Após aplicar, o subprocesso de diagnóstico fica em leitura com escrita/rede/processos bloqueados por audit hook. Imprime contagens de trabalhos elegíveis e motivos de pendência. Não ativa o runtime nem solicita cotações. A ativação posterior precisará dos novos hashes; o ativador antigo não deve ser usado como prova de carregamento deste código.

## Verificado

329 testes aprovados em pandas 2.2.3 e 3.0.3. Incluem 33 casos novos: aquisição BRL/EUR separada com fonte simulada, partições de dias distintos, idempotência, compartilhamento de cotação entre contas, fonte ambígua, vínculo futuro, mudanças de capital/vínculo durante o HTTP, adulteração do contexto, preços inválidos/stale, ausência explícita, privacidade, corrupção, recusa de hosts/redirecionamentos, semântica de volume, integração no refresh e rota GET-only. HTTP real do provedor e resolvedor de credenciais do Mac não foram executados pelo assistente.

Instalador aplicado e repetido em raiz temporária: 329 testes por execução; fonte divergente recusada antes de gravar; dados sentinela preservados. Nenhum dado real ou operação financeira foi usado nos testes. A verificação com observações reais dependerá de vínculo revisado, acesso local ao provedor e ativação planejada.
