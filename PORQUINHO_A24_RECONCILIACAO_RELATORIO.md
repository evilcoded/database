# A24 — reconciliação global de resultados de pesquisa

Aplica-se após PORQUINHO_A24_IDENTIDADE_GLOBAL_V2.command, com hashes exatos. Não encerra a A24 nem autoriza publicação canônica.

## Resultado

O reconciliador P35F aceita histórico com colunas neutras, sem exigir price_eur. Para previsões com origem explícita, seleciona estritamente instrument_id + provider + provider_id + quote_currency. Apenas o nome do provedor é comparado sem distinção de maiúsculas; identificador e moeda mantêm comparação estrita. Não usa ticker para resolver identidade e não aplica FX.

A previsão deve declarar EXPLICIT_QUOTE_NEUTRAL_VALUES_SOURCE_UNATTESTED. O preço realizado vem exclusivamente de price com origem/cotação explícitas. Não há substituição por price_eur, outra origem, outra moeda ou observação inicial aproximada. Identidade ausente, vínculo conflitante, unidade não verificada ou data de emissão inválida permanecem bloqueados. Uma referência local não se torna atestado independente.

O alvo continua sendo a 30ª observação diária posterior à observação de previsão. Não corresponde aos ciclos canônicos de 30/60/90 dias. As datas são filtradas por as_of; não há exigência de negociação em todos os dias do calendário. Duplicatas não desaparecem do relógio de observações: invalidam o ponto. Preços inválidos entre início e término bloqueiam o resultado. Nenhuma posição, quantidade ou moeda de conta é inferida.

Antes da maturação, retorno parcial e diferença em relação ao alvo permanecem diagnósticos provisórios. Na maturação, o resultado permanece RESEARCH_OUTCOME_OBSERVED_UNATTESTED, RESEARCH_ONLY e NOT_VALIDATED. issued_before_outcome e independent_archive_verified continuam falsos; não há certificação de modelo, retorno esperado ou sizing, promoção automática ou execução financeira.

O caminho legado de pesquisa permanece separado. Linhas com origem explícita não alimentam uma junção legada por símbolo. Isso pode deixar registros antigos sem correspondência; o patch não cria vínculos retroativos para contornar essa ausência.

## Instalador

Modifica p35f_outcome_reconciliation.py e a expectativa do teste de integração global; adiciona global_outcome_index_a24.py e 27 testes de reconciliação. Valida 233 testes em cópia temporária antes de gravar, cria backup .porquinho_a24_reconciliation_backup_* e confere hashes finais. Reexecução idempotente. Não instala dependências e não inicia ou reinicia serviços.

Após a aplicação, um subprocesso -I -B inspeciona os arquivos locais somente em leitura e imprime contagens agregadas. Um audit hook bloqueia escrita, processos e conexões. Compara hashes do CSV e journal antes e depois: se o aplicativo modificar as fontes durante a leitura, as contagens são descartadas e o resumo solicita nova leitura. Nada individual é exportado. O resumo não comprova ativação do código na UI nem validade econômica. Falhas de leitura são explicitadas; dados ausentes não são fabricados.

A aplicação dos arquivos não recarrega automaticamente o processo em execução. Não reutilizar o ativador anterior como prova da ativação deste patch, pois ele não verifica estes novos hashes.

## Verificações no cloud

- 233 testes aprovados em pandas 2.2.3 e 3.0.3; 27 novos casos de reconciliação, com resultados positivos, maturação parcial, separação de moedas/provedores/identidades, conflitos, preços inválidos e duplicatas.
- Instalador aplicado e repetido: 233 testes em cada execução; baseline divergente recusada antes de gravar; arquivo sentinela de dados preservado.
- Verificador de resumo executado contra journal/CSV sintéticos temporários: uma previsão global madura identificada corretamente; tentativa deliberada de escrita bloqueada; dados preservados.

Nenhum serviço, dado real, modelo real, treinamento ou operação financeira foi executado nos testes. A validação no Mac só será estabelecida pela saída local.
