# A24 — origem global: preflight de aquisição e vínculos

Leitura local sem importar a aplicação, sem rede, sem reinício, coleta, treinamento, atribuição de identidade ou escrita no projeto. Imprime apenas JSON agregado; não exporta registros individuais, identidades, saldos, credenciais ou conteúdo das fontes. Um audit hook bloqueia escrita, processos e conexões durante a inspeção.

Inspeciona os arquivos existentes: data/universal_instrument_catalog.json, data/instruments/manual_instruments.json, data/unified_br_equity_market_latest.json e results/latest.json. Relata campos explícitos e declarações de provider_binding_attested, mantendo essa declaração distinta de comprovação independente. Uma declaração não é aceita automaticamente como vínculo autorizado. Detecta conflitos por provider/provider_id e contabiliza formatos de instrument_id sem alterá-los. currency não é tratada como quote_currency. O escopo é limitado aos caminhos inspecionados; ausência nesses caminhos não prova ausência em todo o projeto.

Também lê brain/reports/history_fetch.json e o cabeçalho/contagens de market_daily.csv. A inferência do intervalo de seis horas só é apresentada quando o hash de webapp/server.py confere com o código já inspecionado. Coleta hashes de oito fontes relevantes para conferir continuidade. Arquivos JSON limitados a 32 MiB; caminhos com symlink são recusados e alterações durante a leitura são sinalizadas.

Constatações no código conhecido: o servidor restringe a coleta histórica pelo mtime do relatório a seis horas; o merge diário preserva datas/ativos existentes; main do coletor usa a chamada legada sem identidade global. Logo, CSV inalterado após um novo snapshot não demonstra por si só falha da aquisição. A identidade global precisa vir de fonte explícita; não pode ser criada a partir de ticker, moeda, holdings ou metadados legados.

Objetivo: orientar a próxima ligação de aquisição usando a origem real disponível no Mac. Não concede atestado, não cria registry, não refaz histórico e não libera publicação canônica.

Verificados: 11 testes de contagem, metadados aninhados, preservação de formatos, conflitos entre fontes, privacidade, symlinks, recusa de escrita e execução do .command; smoke de leitura das fontes cloud; sintaxe Bash. O JSON produzido pelo usuário estabelecerá a situação dos dados locais.
