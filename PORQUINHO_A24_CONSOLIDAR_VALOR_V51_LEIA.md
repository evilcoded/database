# A24 V51 — orçamento total da compra na realocação

Consolida os cenários da V49/V50 em fluxos de caixa explícitos, sem selecionar um investimento:

- Venda de referência menos comissão da venda = líquido provisionado.
- Parcela para o ativo + comissão da compra = débito total provisionado da compra.
- Débito total da compra + saldo residual = líquido provisionado da venda.
- Parcela vendida + restante da posição = capital de referência original.

A comissão da compra já integra seu débito total e não deve ser somada novamente. O teto do orçamento é arredondado para baixo à precisão cadastrada da moeda. A precisão de referência não certifica a regra de arredondamento do banco: se o cenário não fechar nessa precisão, a UI mantém a necessidade de conferir/recalcular a cotação.

O cartão destaca o teto provisionado por capital de cenário. Quando categorias de compra diferentes conduzem ao mesmo teto, ele aparece uma vez. Se a categoria da venda alterar o teto, continua como intervalo; se houver vários capitais de cenário, nenhum é escolhido automaticamente. Os detalhes passam a ter oito campos, distinguindo líquido da venda, débito total da compra e parcela do ativo.

A classificação de SOL no contexto N26 / Alemanha / Standard / EUR usa a explicação de tarifas revisada do aplicativo: 2,5% para compra e venda. A confirmação está em dados de política, com origem declarada e sem atestado independente. Não se estende a outros bancos, países, planos, ativos ou moedas. A fonte pública e seu prazo local de revisão permanecem os anteriores; não há renovação automática. Nenhuma captura ou valor financeiro privado faz parte da entrega pública.

## Limite da consolidação

Este patch consolida **o orçamento provisionado do cenário**, não a fração da posição que o Brain deve escolher vender. `selected_amount` e `recommended_amount` continuam nulos. O valor da venda usa referência de pesquisa e provisão documental de comissão; seu líquido efetivo depende da cotação bancária. Spread, quantidade recebida, desempenho líquido, lotes e condições de execução não são certificados por um teto calculado. Não há cotação permanente derivada de uma captura, recomendação final ou ordem.

A seleção autônoma do valor pelo Brain e a ligação a cotações bancárias atuais continuam necessárias para concluir o valor recomendado. Ciclos históricos continuam servindo ao aprendizado; este patch não altera critérios ou acrescenta limiares de alocação.

## Instalação e ativação

Verifica hashes e valida em uma cópia temporária antes de aplicar os fontes. Faz backup único dos arquivos alterados; repetir não gera outro backup. Divergência interrompe a instalação. Não modifica saldos, posições, transações, modelos, memória, aprendizado ou snapshots/históricos anteriores. Nenhuma confirmação financeira privada é publicada ou importada pelo instalador.

O ativador protegido pode reiniciar somente o Porquinho identificado na porta 8765, preservando o Bridge 8787. Trabalho ativo/em fila bloqueia a ativação; depois repita apenas `PORQUINHO_A24_ATIVAR_CONSOLIDACAO_V51.command` salvo em Downloads. Não usa SIGKILL, servidor duplicado, refresh manual, treino solicitado ou operação financeira. Após ativar: Command+Shift+R no navegador.

O diagnóstico adiciona contagens dos novos estados, sem exportar valores monetários. A saída local deve confirmar ativação e resultados reais; testes sintéticos não comprovam cotações bancárias ou tamanho recomendado.

## Verificação

1306 testes Python, 281 verificações JavaScript e 38 testes do ativador. Incluem conservação de caixa, comissão incluída sem dupla contagem, capitais distintos sem seleção, faixas condicionais de venda, precisão variável, arredondamento bancário pendente, preservação de dados, classificação tarifária no contexto exato e diagnóstico sem valores privados. Chromium desktop/mobile 390px: teto provisionado, oito campos, modelos/cobertura/fontes e popups/Voltar, sem overflow horizontal ou erros JavaScript. Instalador exercitado com aplicação/repetição, backup único, baseline divergente recusado e sentinelas financeiros/modelos/histórico/runner local preservados.
