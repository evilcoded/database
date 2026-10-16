# Dupla conferência de moedas e maturação — somente leitura

A auditoria não instala fontes nem executa módulos da aplicação. Lê arquivos explicitamente enumerados: tabela de mercado, snapshot atual, prediction_lab, resultados de episódios, dois journals P35 e diretórios de resultados shadow e captura prospectiva. Não percorre todos os snapshots históricos e não certifica todo o Brain.

Confere declarações de `quote_currency` separadamente de `currency`, campos com `_eur`, contextos de identidade explicitamente Brasil/cripto e estados de maturação armazenados. As contagens JSON são de objetos, não de posições ou operações únicas. Não herda automaticamente a moeda de um objeto pai para campos filhos. Os códigos de moeda não se limitam a EUR/BRL/USD.

Nos resultados de episódios, cruza símbolo, data e preço legado de referência/maturação com a tabela preservada. Mais de uma linha símbolo/data é ambígua; não escolhe uma. Uma correspondência única relata apenas a declaração de moeda da linha. Isso não prova identidade canônica nem que o campo legado esteja nessa unidade. Uma moeda declarada em conflito entre as duas pontas é sinalizada. Sem moeda explícita, a unidade continua pendente, mesmo se o nome do campo termina em `_eur`.

Também verifica por AST o contrato EUR do código atual de aquisição, sem importá-lo nem consultar credenciais. Um contrato do código atual dá suporte à hipótese histórica EUR, mas não comprova por si só a origem de cada linha histórica. Os journals P35 lidos têm a cadeia local de hashes verificada, sem atestado independente.

Um processo filho com audit hook recusa gravações e rede. O processo pai salva somente o relatório agregado em Downloads, fora do projeto. Os arquivos lidos são novamente comparados por SHA256; se mudarem durante a leitura, o relatório exige repetir a inspeção. Limites de tamanho/população resultam em inspeção não concluída, não em confirmação parcial silenciosa.

22 testes offline e execução integral do `.command` com dados sintéticos: EUR declarado, campos legados sem moeda, conflito EUR/BRL, moeda de conta distinta de cotação, duplicados, contrato de código não atestado, identificação explícita Brasil, journal parcial, symlink e preservação dos arquivos. Nenhum dado real do Mac foi conferido por esses testes.

Não atribui moedas, não altera dados, não inicia ciclos, não treina, não reinicia serviços e não autoriza publicação canônica ou execução financeira. Compartilhe o JSON gerado para interpretar os dados reais antes de qualquer correção/migração adicional.

## V2 — diagnóstico e formatos de journal

O relatório anterior INSPECTION_NOT_COMPLETED/ValueError não permite concluir nada sobre as moedas. V2 informa código de erro sanitizado e fonte em falhas globais. Falhas de journal tornam o resultado parcial, mantendo as demais seções. A leitura aceita registros JSON seguidos por LF, CRLF ou pelo separador literal barra-n do escritor legado, via JSONDecoder incremental, sem substituição global de escapes. Toda cadeia continua sendo verificada; journal truncado, separador desconhecido ou hash inválido não são aceitos. A presença do formato legado não foi confirmada nos dados do usuário. A versão foi testada com o .command completo e preservação dos arquivos. Use o nome V2; o arquivo anterior não precisa ser apagado.

## V3 — diretório shadow com mais de 2.000 arquivos

A execução real V2 encontrou DIRECTORY_FILE_LIMIT em data/brain/shadow/outcomes. Isso não é corrupção nem resultado de moeda. V3 agrega cada arquivo individualmente, até 20.000 por diretório e dentro do orçamento total de leitura, sem carregar todos os objetos ao mesmo tempo. Se encontrar um limite ou arquivo inválido, mantém as seções anteriores e relata PARTIAL_INSPECTION_NOT_CERTIFIED com contagem lida e motivo. O limite não é interpretado como ausência de dados. Verificação do comando integral com 2.001 arquivos de outcome e preservação de todos os bytes de entrada aprovada. Nenhum snapshot é removido ou compactado pela auditoria.
