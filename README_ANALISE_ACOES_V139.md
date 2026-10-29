# V139 — Cálculos de ações conectados às fontes verificadas

O diagnóstico do V138 confirmou 18 decisões registradas e acompanhamento prospectivo funcionando. As ações continuavam sem o perfil de índices exigido pelas regras globais; havia artefatos técnicos/fundamentalistas antigos, mas os artefatos de risco/regime e oportunidade não estavam sendo produzidos no ciclo normal.

## Entrega concreta

O ciclo normal passa a executar os cálculos já existentes em `equities.technical`, `equities.risk_regime` e `equities.opportunity`, consumindo os históricos BRAPI já adquiridos pelo coletor configurado. A aquisição de histórico existente foi antecipada para antes da pesquisa longa, junto às outras coletas, e seu resultado é reutilizado depois. A projeção de análises não faz chamadas de rede adicionais.

A seleção é feita por identidade canônica, classe explícita, moeda e vínculo confirmado do provedor. OHLCV é extraído de bundles selados e reconstruídos pelo validador existente. Histórico legado associado apenas por ticker não é reatribuído silenciosamente. Pontos incompletos do dia atual, fechamentos divergentes, OHLCV inválido, moedas incompatíveis e alterações de vínculo são recusados.

As novas análises ficam em um namespace separado, `data/observability/equity_analysis_pipeline_a24`, com capturas seladas, versão dos cálculos e referência aos históricos. A ponte de observação global pode consumir essas evidências por identidade exata. Os artefatos antigos não são reescritos. O leitor diferencia ausência de histórico, análise produzida e ausência de uma cotação atual compatível; a hora do cálculo não torna o histórico uma cotação atual.

Os cálculos técnicos, de risco e de oportunidade não foram alterados. A dependência de credenciais de `equities.historical` passou a ser carregada apenas quando há solicitação de credencial, permitindo usar seu normalizador puro sem iniciar dependências de aquisição. A função pública permanece disponível para os consumidores existentes.

## Limite importante: as recomendações globais de ações ainda não estão concluídas

Este patch **não produz `promising_pct`, `entry`, `risk`, `reversal_risk` e `asymmetry` para as ações** e não declara essa pendência resolvida. O escore especializado de oportunidade é evidência assinada entre −1 e +1; ele não é uma probabilidade nem o índice operacional global entre 0 e 100. Convertê-lo arbitrariamente mudaria o significado dos limites de decisão.

Fundamentos sem data permanecem evidência legada disponível, mas não entram como dados atuais na nova projeção. Sem uma referência comparável qualificada, o risco absoluto pode ser calculado, enquanto os indicadores relativos ficam indisponíveis. Não se escolhe um benchmark silenciosamente. Esses limites aparecem no resultado, em vez de serem preenchidos com zero ou com um indicador de outra moeda.

A próxima parte funcional é a compatibilidade dos indicadores de decisão. O fluxo de ações não deve ser considerado concluído antes dela. Os critérios de compra/venda/manutenção/realização, o dimensionamento do V137, os registros prospectivos já criados, os modelos e o dashboard foram preservados. Não foram criadas ordens, alterações financeiras, ativações de modelos ou recomendações a partir das evidências especializadas.

## Instalação e verificação

Aplicar `PORQUINHO_ANALISE_ACOES_V139.command --reiniciar` sobre V138. Seis arquivos de código, incluindo um módulo novo. O instalador verifica as bases antes de escrever, verifica as dependências de análise, cria backup, recusa divergências e pode ser reaplicado.

Após um ciclo normal, o diagnóstico resumido informa as análises efetivamente produzidas e as entradas que continuam pendentes:

```bash
"$HOME/anaconda3/bin/python" -I -B "/Applications/Bridge_Companion/porquinho_v33_web_foundation-2/tools/diagnose_decision_pipeline_a24.py" --resumo
```

O diagnóstico consulta apenas o servidor local; não inicia ciclo, coleta de mercado ou treinamento. A aquisição normal continua limitada e pode precisar de ciclos sucessivos para atender os trabalhos de histórico que já estavam na fila.

## Verificações de desenvolvimento

A suíte de regressão de 478 testes passou. Uma suíte complementar de 65 testes de análise e contratos de ações também passou, com sobreposição de 17 testes entre as duas. Após os últimos ajustes, os 41 testes diretamente afetados passaram novamente.

Incluem paridade com as funções existentes, captura selada, preservação de arquivos antigos e sentinelas financeiros/modelos, ausência de rede na projeção, identificação/moeda, dados sem data, falta de referência relativa, adulteração de fontes, alteração de vínculo, dados não finitos, expiração da análise e consumo pela ponte sem promover o escore a decisão. O teste de ordenação do V138 foi atualizado para incluir histórico e análise antes da captura.

Compilação Python e sintaxe shell passaram. Instalador testado em cópia da base: seis arquivos, reaplicação idempotente, recusa de divergência antes de escrever e preservação de sentinelas de configuração, ledger, modelos e aprendizado legado. Não houve coleta ao vivo, treinamento ou teste no Mac do usuário. A produção de análises na instalação depende dos históricos verificados efetivamente disponíveis.
