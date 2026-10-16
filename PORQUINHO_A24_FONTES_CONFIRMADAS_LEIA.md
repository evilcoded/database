# A24 — verificar cotações e cadastrar correspondências confirmadas

Comando genérico que recebe um JSON privado de correspondências confirmadas pelo usuário e seu SHA256. Não contém uma lista fixa de ativos ou moedas. O arquivo de confirmação é criado localmente em Downloads; não deve ser publicado no repositório.

O comando confere hashes das ferramentas já instaladas, formato e integridade da confirmação, identidades e pares exatos presentes na demanda financiada atual. Não associa símbolos, não altera IDs, não substitui fontes já cadastradas. Usa o adaptador CoinGecko existente, com TLS, endpoint oficial restrito, sem redirects e com a configuração segura de credenciais do projeto. Outros provedores são recusados explicitamente, sem fallback para CoinGecko.

Faz dois GETs para novas correspondências: supported_vs_currencies e simple/price com os IDs exatos e as moedas solicitadas. Todos os pares novos precisam estar disponíveis, ter preço numérico finito positivo e timestamp recente (até 30 minutos, tolerância de 30 segundos de adiantamento). Não utiliza FX local, conversão por moeda de conta ou cotação substituta. O serviço pode agregar/converter preços internamente; isso não é atestado, e disponibilidade de uma cotação não comprova mercado de execução numa corretora.

Se qualquer cotação nova faltar, ficar obsoleta ou falhar, nenhum dos novos vínculos do lote é aplicado. Depois da consulta revalida a fila e o digest do registro. Usa o importador anterior com trava, backup e gravação atômica para acrescentar apenas os vínculos confirmados. O responsável é registrado como operador local que executou a confirmação, com horário UTC da execução e vigência sem retroagir. A referência contém hashes da confirmação e da resposta JSON normalizada e horário da consulta. Esses hashes não constituem arquivo independente de preços; o relatório exporta apenas IDs, moedas, timestamps e disponibilidade, sem valores de cotação.

Reexecução com os mesmos vínculos já presentes retorna CONFIRMED_BINDINGS_ALREADY_PRESENT, sem nova consulta ou duplicação. Vínculo existente em conflito não é alterado. Uma falha no estágio de registro exige conferir o relatório/estado antes de concluir que houve gravação; o comando não afirma genericamente que toda falha significa zero gravações.

A aplicação cria/atualiza somente o registro explícito de vínculos e seu backup/lock. Não altera dados históricos, snapshots, previsões antigas, moedas legadas, identidades de posições, modelos ou maturações. O comando não solicita refresh, treinamento, compras, vendas ou reinício. O coletor já ativo pode consumir os vínculos nos próximos ciclos normais, respeitando os limites e a amostragem de pesquisa existentes. Os novos journals ainda não são treinamento automático do laboratório.

## Confirmação privada

Formato:

```json
{"schema":"porquinho.confirmed-source-pairs-a24/1.0","confirmed":true,"provider":"CoinGecko","instruments":[{"instrument_id":"ID_EXATO_CONFIRMADO","provider_id":"id-exato-confirmado","quote_currencies":["MOEDA_CONFIRMADA"]}]}
```

Execute o `.command` passando o caminho desse arquivo e o SHA256. Utilize apenas o arquivo correspondente aos casos que efetivamente confirmou. Não forneça chaves em chat: o comando reutiliza o resolvedor seguro já existente.

## Verificação

20 testes com fornecedor simulado: aplicação de duas moedas, moeda arbitrária, lote incompleto recusado, idade/timestamp de preço, número inválido, ID diferente, falta de confirmação/demanda, fonte em conflito, preservação e backup, mudança de fila, erro HTTP, repetição sem nova consulta, ausência de gravações de snapshots/observações e execução completa do ponto de entrada com relatório privado sem valores financeiros. Os testes não comprovam acesso real ao CoinGecko nem aprovação financeira. Essa comprovação de disponibilidade só pode ocorrer na execução local.
