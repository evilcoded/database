# V131 — indicadores operacionais na moeda nativa

O coletor suplementa os contextos CoinGecko em moedas adicionais à moeda explicitamente usada pelo produtor original. Não copia índices EUR para BRL. Retornos de 7/30 dias, referência BTC, volume e capitalização relativos e distância da máxima vêm da solicitação explícita na moeda do contexto.

A fórmula pura foi extraída do motor original para `operational_score_a24.py`; o produtor original delega ao mesmo cálculo, preservando seus parâmetros e sua calibração existente. O novo caminho usa os pesos originais de base, sem aplicar a calibração aprendida em outra moeda. O critério monetário de capitalização usa o valor informado pelo provedor na unidade de referência original: não há conversão de preço da posição nem cópia de pontuação.

O ciclo normal coleta e registra capturas imutáveis em `data/observability/global_operational_metrics_a24`. Leituras exigem identidade, moeda, vínculos, fontes recentes, fórmula e reconstrução dos índices compatíveis. Uma captura recente pode ser reutilizada sem atualizar artificialmente sua data. Dados ausentes ou inválidos deixam a leitura indisponível. A confirmação de tese fraca usa os dois dias UTC anteriores já concluídos no mesmo contexto, sem reutilizar confirmações de outra moeda.

O caminho original na moeda de referência permanece preservado. Este patch não amplia sua seleção original de ativos. Perfis operacionais brapi e renda fixa permanecem pendentes; indicadores de criptomoedas não são atribuídos a essas classes. As regras globais compartilham o mecanismo existente, enquanto cada adaptador precisa fornecer entradas semanticamente compatíveis.

Não altera modelos, pesos salvos, limites de decisão, ledger, saldo ou orçamento. Não executa treinamento nem negociação. As leituras operacionais não equivalem à publicação de recomendações completas com dimensionamento e custos validados; os bloqueios existentes continuam aplicados.

## Aplicação

Execute o instalador com `--reiniciar`, atualize a página e execute um ciclo normal pela interface. Depois:

```bash
"$HOME/anaconda3/bin/python" -I -B "/Applications/Bridge_Companion/porquinho_v33_web_foundation-2/tools/diagnose_global_action_metrics_a24.py"
```

O diagnóstico apenas consulta o servidor local. Não inicia ciclo, coleta ou treinamento.

## Verificação

209 testes Python passaram, incluindo 2.000 comparações numéricas do cálculo original, casos com calibração, moedas adicionais, unidade explícita de capitalização, falhas de provedor, dados incompletos, confirmações diárias, integração por posição e reutilização sem mudança de data. Passaram as verificações JavaScript de painel, gráfico patrimonial, intraday e fluxo DOM completo de revisão de custos. O instalador foi verificado para reaplicação, recusa de divergência e preservação de sentinelas de modelos e ledger.

Verificações feitas em ambiente de desenvolvimento com fontes sintéticas, sem coleta real CoinGecko nem teste visual no Mac.
