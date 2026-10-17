# A24 — consolidação da cobertura do histórico

Mantém a consolidação F3/F4 e distingue a cobertura de taxas nas alternativas econômicas completas da cobertura nas distribuições selecionadas para aplicar cash. O zero numa seleção não comprova perda de transações. Não altera nem alarga os critérios de correspondência.

## Mudanças

- Reaproveita a evidência econômica existente, sem novo cadastro, coleta, treinamento ou alteração das transações.
- Confere evento/hash/conta/moeda/lado/identidade e a população de transações realizadas antes de afirmar o reaproveitamento nas alternativas completas. Entrada indisponível ou divergente permanece desconhecida, não zero.
- Reconcilia cada transação histórica uma única vez nas distribuições atuais, distinguindo instrumento ausente, outra conta, outra moeda e outro lado da operação. Não usa ticker ou aliases como identidade financeira.
- Mostra na mesma UI a cobertura das alternativas e a cobertura dos cenários de cash. Resumo sem identificadores financeiros ou valores.
- Relatório completo da ativação continua salvo em Downloads; Terminal exibe resumo compacto com status, invariantes, problemas e cobertura. A inspeção prévia também é compacta e elimina uma composição redundante do ciclo.

Nenhuma taxa histórica é transformada em tarifa futura. Não cria retorno líquido, comparação aprovada, política validada, sizing, ordem ou recomendação canônica. Não reescreve snapshots, memória, aprendizagem, modelos, transações, posições ou maturações. Método e versões das políticas aprendidas continuam preservados.

## Validação e ativação

976 testes Python e 102 verificações JavaScript, em pandas 2.2.3 e 3.0.3, sem skips. 35 testes simulados de ativação, incluindo a preservação dos erros/invariantes no resumo e do conteúdo do relatório completo. Instalador aplicado e repetido em cópia temporária; baseline divergente recusado; backup único e dados/CSV/configuração preservados.

A ativação V28 tenta reiniciar somente o Porquinho, preserva Bridge e recusa ciclo ativo/em fila. Sem SIGKILL, servidor duplicado, refresh manual ou endpoint financeiro. Quando adiada, repetir apenas o ativador indicado em Downloads após o ciclo. Ativação e motivos reais V28 ainda precisam ser observados no Mac.

SHA-256 do instalador: `e187224cc92875fd7a835b4177adced7e2d6c2d2cb8e3a596673a73f4a3995e3`.
