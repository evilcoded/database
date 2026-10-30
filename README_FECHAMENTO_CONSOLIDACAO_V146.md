# V146 — fechamento da integração das sugestões globais

Consolida COMPRA, VENDA, MANTENHA, REALIZAR e REALOCAR numa projeção comum, da decisão à interface e ao acompanhamento prospectivo. As regras, limites de compra/venda, fórmula comum V143, modelos e dados financeiros permanecem preservados. Não é um redesenho do dashboard nem uma certificação de desempenho financeiro.

## Entrega

- `suggestion_consolidation_a24` produz um contrato explícito por conta/moeda/identidade. Sinal, referência bruta disponível, valor pendente, revisão de convergência e entrada ausente são estados diferentes. ACOMPANHE continua separado de MANTENHA.
- COMPRA preserva a alocação original dentro do caixa, orçamento e limites de posição; ausência de avaliação mantém o sinal sem fabricar um valor. Não cria quantidade de compra sem uma regra de execução.
- VENDA preserva a saída integral configurada. A explicação distingue risco estrutural de tese fraca confirmada em dois dias completos, sem criar stop-loss percentual.
- REALIZAR preserva os critérios de convergência e a fração original em unidades. Um único sinal de deterioração continua em revisão, sem valor de saída inventado. O contador da interface deixa de somá-lo a VENDA.
- REALOCAR agrupa somente saídas com valor e quantidade positivos e entradas com referência financiada pelo caixa atual, uma vez por movimento. Não antecipa receitas das vendas, não mistura moedas nem declara vantagem líquida comprovada. Seus detalhes mostram ações e critérios de cada perna. Não introduz uma nova regra de seleção econômica entre pares.
- Interface consome o contrato comum. Sugestões vencidas não reaparecem pelo fallback de posição. Preserva os botões Global/EUR/BRL, gráficos, intraday e proteção V144.
- Acompanhamento guarda quantidade, fração e critérios da decisão e exige que o horário da cotação-base corresponda ao dos indicadores. A população é lida sob o bloqueio do escritor.
- Novos snapshots completos são armazenados separadamente mesmo quando já existe uma emissão diária anterior à atualização. Não reescrevem a emissão original nem aumentam artificialmente a contagem de amostras independentes. Realocações possuem captura selada do agrupamento e de suas pernas.
- Resumo de acompanhamento separa ações, perfis, snapshots e agrupamentos, mantendo os horizontes de 30/60/90/120 dias de calendário. Nenhum resultado pendente é promovido a modelo validado.

## Critério de fechamento e limites

O fechamento é da integração dos cinco tipos de sugestão: cálculo, apresentação e registro. Não é necessário aguardar que todos ocorram no mercado real. A validação instalada percorre cenários de controle EUR/CoinGecko, BRL/CoinGecko e BRL/brapi, com limiares de controle declarados e sem ler ou modificar a configuração financeira real.

Históricos/cotações não entregues pelo provedor continuam pendentes. Horizontes ainda não amadurecidos continuam pendentes. O aprendizado legado e a captura prospectiva são preservados; este patch não treina, ativa, recalibra ou certifica modelos. As referências são brutas para revisão manual, não valores líquidos de ordens. Custos ou disponibilidade no banco não são inventados nem exigem novos formulários para mostrar os sinais existentes.

## Validação

185 testes Python de decisão, dimensionamento, índices comuns, associação às posições, captura, maturação dos quatro horizontes, análise de ações, histórico, proteção e conhecimento passaram. Um teste AST antigo procura uma atribuição removida no servidor e foi excluído da seleção; testes de integração exercitam os ganchos atuais. O relatório `VALIDACAO_FECHAMENTO_V146.json` contém somente cenários sintéticos e o resultado da seleção.

DOM: contrato real produzido pelo Python passou pelos cliques de COMPRA, VENDA, MANTENHA, REALIZAR e REALOCAR, quantidades/frações, filtros Global/EUR/BRL e expiração. Também passaram os testes anteriores de ações, critérios V145, proteção e botões de moeda. Nenhum POST de execução foi feito. Não houve inspeção visual por navegador real nem consulta ao mercado.

Instalador: onze arquivos, hashes da base V145, compilação, backup, verificação dos payloads, recusa de divergência antes de escrita e reaplicação idempotente. Durante a instalação, executa os cenários de controle e sincroniza apenas o conhecimento descritivo. Teste com sentinelas confirmou preservação de ledger, configuração, modelos e memória legada.

## Operação

Aplicar `PORQUINHO_FECHAMENTO_CONSOLIDACAO_V146.command --reiniciar`. O reinício usa o mecanismo existente de espera por ciclo ativo. As mensagens de sucesso são `CINCO_FLUXOS_VALIDADOS` e `PATCH_FECHAMENTO_CONSOLIDACAO_V146_OK`.

Validação de controle, sem servidor, rede ou ciclo:

```bash
"$HOME/anaconda3/bin/python" -I -B "/Applications/Bridge_Companion/porquinho_v33_web_foundation-2/tools/validate_suggestion_consolidation_a24.py"
```

Diagnóstico compacto opcional do estado real, somente leitura:

```bash
"$HOME/anaconda3/bin/python" -I -B "/Applications/Bridge_Companion/porquinho_v33_web_foundation-2/tools/diagnose_decision_pipeline_a24.py" --fechamento
```

A próxima etapa de produto é o ajuste dos portlets e gráficos de decisão do dashboard. Não depende de forçar ações reais nem de criar mais revisões de custos.
