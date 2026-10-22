# Processar componentes já prontos no mesmo ciclo — V88

O produtor encerrava o loop após gravar o primeiro pacote. Mesmo com várias contas/séries elegíveis e com experimentos existentes, só um pacote avançava por ciclo. O V88 continua o loop para todos os pacotes elegíveis já calculados por prepare.

Preserva, por pacote, o lock do produtor, a checagem do registro de fontes, a revalidação do contexto de conta/orçamento, o hash da fonte e a reconstrução do experimento antes da escrita. Não altera algoritmos, pesos, horizontes, seleção de instrumentos, limites de validação ou chamadas aos laboratórios. Não adiciona requisições HTTP.

Os registros continuam imutáveis e identificados pelo conteúdo. Contabiliza eligible_packet_count, packets_already_current e packets_created. Em falha durante um lote, informa o erro e quantos pacotes foram realmente criados, preservando os já gravados; não há rollback de registros financeiros nem escrita financeira nesta etapa.

Não garante que existam vários pacotes elegíveis: se faltarem fontes ou experimentos, o bloqueio permanece. Não implementa a comparação econômica líquida nem a publicação final. Remove um atraso de processamento na etapa anterior. O limite de um experimento por ciclo nos laboratórios permanece inalterado.

147 testes passaram, incluindo contas distintas no mesmo ciclo, repetição sem alteração de bytes/mtime, perda de elegibilidade entre gravações, erro de escrita parcial e regressões de risco/decisão. Instalador testado em repetição e base divergente. Modifica somente universal_portfolio/research_economic_components_a24.py; não edita dados/modelos e não substitui arquivos de brain/. Backup e integridade antes da substituição. Reiniciar somente o Porquinho após terminar o ciclo.
