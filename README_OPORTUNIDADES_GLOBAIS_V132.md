# V132 — oportunidades globais e explicação das regras

Corrige a tela Oportunidades, que ainda consultava somente a lista do snapshot original, sem transportar os indicadores nativos adicionais do V131. A camada visual posterior também foi ligada ao novo conteúdo; ela não volta a substituir o painel pela lista antiga.

## Comportamento

- Reutiliza o planejador de pesquisa e seus vínculos explícitos, classes permitidas e impressões do contexto. Cada linha mantém conta, moeda, identidade, provedor e identificador da fonte. Não atribui uma referência sem moeda à conta selecionada.
- Reutiliza o mesmo avaliador de métricas e a mesma função de regras. Uma posição existente recebe a regra de acompanhamento; uma alternativa sem posição recebe a regra original de entrada. O P/L não é inventado para uma posição nem exigido para uma alternativa sem posição.
- Exibe até seis cartões compactos, contagem das ações no recorte e acesso às demais leituras. O filtro de moeda, conta e busca é aplicado antes das contagens. A lista expandida exibe até 200 linhas; acima disso, solicita reduzir o recorte. Não cria ranking.
- Cada cartão abre a fonte, a data e os critérios efetivamente comparados. Os detalhes das posições também passam a explicar risco estrutural, enfraquecimento de tese com confirmação diária, realização e manutenção. O P/L usado é desde a aquisição registrada, não desde o snapshot anterior. Não cria stop percentual de perda.
- P/L fora da janela atual, futuro ou anterior à alteração da posição não pode disparar realização de lucro. Risco estrutural atual e tese fraca confirmada continuam podendo produzir leitura de venda sem depender desse P/L.
- Disponibilidade no banco permanece informação independente. Um relato negativo ou ausência de confirmação não muda o índice de mercado e aparece como pendência. Uma leitura COMPRE não comprova elegibilidade, custos, liquidez, comparação econômica, valor de ordem ou recomendação dimensionada.
- Fontes ambíguas, moedas incompatíveis, indicadores incompletos ou vencidos permanecem pendentes. O frontend também retira a ação de uma leitura operacional vencida quando renderiza os dados.

Perfis operacionais de ações brapi e renda fixa continuam pendentes. Este patch não transforma indicadores de criptomoedas em indicadores dessas classes nem promove pesquisa para validação econômica.

## Preservação

Sem alterações no motor original, modelos, pesos salvos, limites, ledger, saldos e orçamento. Sem treinamento, novas coletas HTTP, gravação de histórico ou execução de negociação. Apenas projeções de leitura e UI, reutilizando os indicadores já disponíveis.

O instalador verifica os hashes da base V131 antes de escrever, faz backup, recusa divergências e permite reaplicação. Use `--reiniciar` para carregar o código atualizado.

## Verificação local

Passaram 226 testes Python e as verificações JavaScript/DOM. Testes sintéticos cobrem moedas e contas distintas, posição versus entrada, confirmação diária, perda de 18% sem stop inventado, realização, P/L desatualizado, referência anterior à compra, disponibilidade desconhecida/negativa, fontes ambíguas, vínculo alterado e ausência de gravações. A composição real dos painéis é exercitada. Testes JavaScript verificam filtros, contagens, escape de texto e validade; um teste DOM carrega todos os scripts do template, exercita o override visual real, clique no cartão, abertura do critério e retorno à lista. Também foram executadas as regressões de gráfico patrimonial, intraday e revisão de custos.

Não foi realizado teste visual no Mac nem coleta real de mercado neste ambiente.

## Após instalar

Atualize a página e abra Oportunidades. Se os indicadores existentes ainda estiverem atuais, não é necessário outro ciclo; caso estejam vencidos, execute um ciclo normal. Para conferir:

```bash
"$HOME/anaconda3/bin/python" -I -B "/Applications/Bridge_Companion/porquinho_v33_web_foundation-2/tools/diagnose_global_action_metrics_a24.py"
```

O diagnóstico passa a imprimir `OPORTUNIDADES_GLOBAIS` e os critérios das posições. Apenas consulta o servidor local.
