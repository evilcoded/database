# V115 — comparação e dimensionamento até a publicação manual

Liga a saída da comparação econômica e do dimensionamento existentes ao compositor `universal_recommendation_snapshot.compose_snapshot`, sem criar outro algoritmo de retorno, risco, utilidade ou valor a investir. A publicação é de sugestões para execução manual, com autoridade EVIDENCE_ONLY, nunca de ordens. O shadow e seu histórico continuam separados; não são renomeados como recomendações canônicas.

Seis arquivos de código: produtor manual, integração na composição do ciclo normal, transporte de metadados pelo assembler de componentes, cache/API no servidor, apresentação nos Insights e diagnóstico de leitura da API. Nenhum novo agendador, treinamento ou alteração de modelos/configuração/carteira/histórico.

## Funcionamento

Após as fases existentes de comparação e dimensionamento, o produtor confere novamente o mesmo conjunto e suas saídas com os avaliadores existentes. Somente aceita o envelope observado pelo transporte governado e vinculado ao hash de um arquivo permitido. Não aceita propostas de UI, ações legadas, quantias derivadas do orçamento ou componentes de pesquisa como substitutos dos componentes completos.

Uma movimentação requer correspondência única de alternativa, comparação, conta, moeda, origem, destino, ação e horizonte com o dimensionamento. Os avaliadores existentes mantêm as rejeições por modelos/políticas/capacidade. Modelos e saídas com datas futuras são rejeitados. NO_ALLOCATION com zero explícito é preservado.

O contrato de publicação requer `manual_publication` no conjunto, com `valid_until` em ISO com fuso e `policy_refs` não vazias. Esses metadados devem vir do produtor econômico com a política e validade efetivas; o patch não solicita ao usuário tolerâncias de risco, não inventa prazo de validade nem cria arquivos governados de exemplo. O assembler transporta esses campos, sem certificá-los. Não se deve adicionar flags de validação aos modelos de pesquisa para preencher esse contrato.

Conjuntos independentes da mesma conta/moeda não são somados nem recebem um vencedor arbitrário: para publicação precisam formar uma decisão conjunta que resolva a disputa pelo capital. Contas/moedas diferentes podem publicar separadamente, sem FX.

A API GET `/api/recommendations/manual` expõe o resultado do último ciclo normal no processo. Cada leitura retira sugestões vencidas ou cujo arquivo de origem mudou. Depois de reiniciar, informa que aguarda um ciclo normal; não treina/coleta mercado para responder ao GET. `/api/status` transporta a mesma publicação. Os Insights mostram a lista por moeda/conta/busca, valor, origem/destino e validade, com conteúdo escapado. A disponibilidade canônica anterior permanece distinta desta publicação manual.

## Limite atual confirmado na V114

Os dados auditados ainda não fornecem conjuntos econômicos completos validados. Portanto, este patch conecta o produtor e testa seu caminho positivo, mas não promete sugestões imediatas com os dados atuais. Ele não certifica pesquisas nem elimina as lacunas de custos, contrafactual, risco, utilidade e dimensionamento. Nenhum fixture sintético é instalado no aplicativo do usuário.

## Instalação e validação

Instalador com preflight de hashes, recusa de bases divergentes/links simbólicos, backup e substituição atômica por arquivo. Por padrão não inicia serviços. `--reiniciar` reutiliza o reinício verificado da V111: recusa encerrar o servidor se houver ciclo ativo ou se não conseguir confirmar processo/projeto/estado, e nunca usa SIGKILL.

119 testes Python passaram, incluindo 25 testes novos e regressões de comparação/assembler/dimensionamento. Caminhos positivos passaram em BRL e EUR e no ciclo completo; casos negativos incluem custos/validação/quantias ausentes, mistura de identidades, políticas rejeitadas, ambiguidade, capacidade excedida, validade vencida, datas futuras, mudança de fonte e disputa de capital. Testes da UI verificam filtros, validade e escape. Sintaxe Python/JS/Bash validada. Instalador testado em instalação sintética, repetição, recusa de divergência e preservação de sentinelas de modelo e ledger. Não houve teste no Mac/bancos reais.
