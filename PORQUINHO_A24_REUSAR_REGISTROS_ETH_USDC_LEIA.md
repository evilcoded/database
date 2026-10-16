# A24 — Reaproveitamento dos registros manuais existentes

Diagnóstico somente leitura para conferir as transações recentes de ETH e USDC como referência, sem recadastramento. Não instala código no aplicativo, não reinicia serviços, não treina modelos, não altera ledger, posições, snapshots, memória, histórico ou taxas. Grava somente o relatório externo em Downloads.

Lê a cadeia do ledger existente e o store durável de execução manual, além dos catálogos atuais para rotular o inventário. Identificadores originais permanecem intactos: símbolo não cria identidade ou associação. Mostra os últimos contextos por identidade/conta/moeda/lado; horários empatados ficam ambíguos. ETH/USDC são apenas os alvos desta investigação, não filtros fixos no motor global. Outros contextos recentes também aparecem para não perder registros cuja identidade não esteja rotulada no catálogo.

Reusa vínculos explícitos existentes: parent_external_id único, manual_external_transaction_id ou commit_plan_id únicos por operação, e identidade única de passo da sequência persistida. Confere quantidade/valor da operação, escopo e montante da taxa; taxas canônicas sem asset_id podem ser ligadas por um passo explícito, sem atribuir identidade retroativa. Não junta por símbolo, conta+horário ou coincidência de valores. Cada taxa é contada uma vez mesmo quando mais de um vínculo a confirma.

Confere presença/validade de conta, moeda, quantidade, preço, valor bruto, timestamp, fonte e proveniência. Verifica compatibilidade de quantidade × preço com o valor bruto na precisão de liquidação declarada. A falta de taxa anexada não implica taxa zero. Limites e estabilidade das fontes são verificados. Fonte alterada durante leitura exige repetir a inspeção depois do ciclo, sem reinício.

O relatório exporta identificadores de instrumento, moedas, contagens, estados e indicadores de presença. Não exporta montantes, quantidades, source_refs, comprovantes ou IDs de conta. O contexto de conta usa hash para distinguir registros. Integridade da cadeia é local, não atestado independente. Estado durável é informado como tal; a forma do registro e ligações ao ledger não certificam por si só toda a execução ou modelos.

Taxas realizadas são evidência de operações já executadas. Este diagnóstico não as transforma automaticamente em tarifa futura, não calcula taxa percentual futura e não autoriza comparação, decisão ou operação. Seu objetivo é verificar onde o fluxo manual já fornece os dados necessários antes de construir outro cadastro ou solicitar preenchimento.

Processo filho isolado (-I -B), com auditoria que recusa gravação, subprocessos e rede. Código de leitura e quatro dependências de fonte existentes têm hashes conferidos. Não invoca commits, recovery/finalizadores ou operadores de taxa. O processo externo grava exclusivamente o relatório em Downloads; recusa saída dentro do projeto. Nenhum arquivo de dados do usuário é publicado no repositório.

Validação: 20 testes com fixtures sintéticas, incluindo taxa sem identidade de ativo ligada pela sequência real do contrato existente, divergências de conta/moeda/montantes, ausência de vínculo, vínculos ambíguos, fontes corrompidas, symlinks e preservação. Comando completo executado duas vezes em projeto sintético, relatórios externos distintos, dados de origem idênticos. Não houve verificação dos eventos reais do Mac no cloud; o relatório local fornecerá essa evidência.

Continua no marco de consolidação Brain/decisão/UI F3 → F4. Não é uma nova fase nem um teste do mecanismo de compra e venda. A ficha de 36 custos não precisa ser preenchida para esta inspeção.
