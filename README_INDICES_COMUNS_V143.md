# V143 — perfil comum de índices de decisão

A escolha explícita foi criar um cálculo comum para ações e cripto, mantendo os
limites configurados de compra e venda. O perfil `COMMON_NATIVE_PRICE_INDEX_V1`
alimenta agora os planos operacionais globais, para todas as identidades e moedas
com fontes explícitas. Não converte o escore antigo de ações [-1,1] em uma suposta
probabilidade, nem aplica uma política separada para BRAPI.

É uma **nova heurística descritiva, ainda sem validação estatística de desempenho**.
O uso de limites iguais não comprova que a distribuição dos novos índices seja
igual à dos antigos. A fórmula e o comportamento mudam tanto para cripto quanto
para ações, conforme a escolha do usuário. Não há compra garantida, precisão
prometida, ativação de modelo treinado experimental ou execução de ordem.

## Dados e significado comum

O cálculo recebe somente histórico diário verificado de preços e uma referência
atual, ambos na moeda explicitamente reportada pelo provedor. A mesma função
recebe as séries de ações BRL, cripto BRL e cripto EUR. Trocar o provedor ou
multiplicar todos os preços por uma constante não altera os índices.

Não usa dominância de BTC, referência relativa a um ativo específico, capitalização
absoluta, volume em quantidade de ações como se fosse giro monetário, fundamentos
sem data ou máxima de 52 semanas como se fosse máxima histórica. A retirada dessas
entradas é uma alteração do modelo de índices, não uma afirmação de que elas são
economicamente irrelevantes. Liquidez e elegibilidade no banco continuam assuntos
separados; os índices não provam que um ativo pode ser negociado numa conta.

Horizontes de 7, 20, 30 e 60 são em **dias corridos**. O preço de referência de um
horizonte é a última observação anterior ao instante alvo, com tolerância máxima
de sete dias. Isso permite fechamentos/feriados sem preencher candles fictícios.
Exige pelo menos 20 observações completas, uma âncora de 60 dias e pelo menos 20
observações nessa janela. Não exige SMA200. As lacunas entre observações dessa
janela e a distância do último preço diário não podem superar sete dias.

A cotação atual deve passar pelas proteções existentes: moeda, identidade,
binding, tempo do provedor e idade máxima de 30 minutos. Histórico não substitui
preço atual. Preços antigos após fechamento continuam indisponíveis para decisões
atuais, mesmo que o histórico permita calcular indicadores descritivos.

## Fórmula versionada e auditável

`C(x)` limita a [0,100]. `r7` e `r30` são retornos percentuais desde as respectivas
âncoras até a cotação atual. As médias usam as observações completas das janelas
nominais de 20/60 dias; a janela longa inclui a âncora de 60 dias.

- `momentum = C(50 + 2.2*r7 + 0.7*r30)`
- `regime = C(50 + 1000*(media20/media60 - 1))`
- `consistencia`: percentual de movimentos positivos na janela longa; movimentos
  exatamente nulos contam como metade. Não é probabilidade prevista de alta.
- `vol`: desvio padrão populacional dos log-retornos divididos pela raiz do
  intervalo em dias, multiplicado por `sqrt(365)*100`.
- `drawdown`: queda percentual da cotação atual em relação ao maior preço da
  janela longa, incluindo a própria cotação. Não é queda desde máxima histórica.
- `reversao = C(30 + 3*max(r7-12,0) + 1.2*max(r30-35,0))`
- `entrada = C(72 + min(10,max(-10,-0.7*r7)) - 2*max(r7-8,0) - max(r7-18,0))`;
  se `r7 < -12` e `r30 < -15`, subtrai oito e limita novamente.
- `risco = C(25 + 0.9*abs(r7) + 0.35*max(drawdown-25,0) + 0.15*vol)`
- `assimetria = C(55 + 0.35*(100-risco) + 0.15*max(75-momentum,0))`
- `oportunidade = C(0.35*momentum + 0.20*consistencia + 0.20*(100-reversao) + 0.25*regime)`
- `potencial = C(0.30*oportunidade + 0.22*entrada + 0.18*assimetria + 0.12*regime + 0.18*(100-risco))`

Os índices são arredondados para uma casa decimal. `promising_pct` permanece o
nome de compatibilidade do campo de potencial; seu contrato declara índice de
0 a 100 e `probability_estimate: false`. Entrada, reversão, assimetria e a mistura
final retomam a estrutura do cálculo original; os componentes de regime,
oportunidade e risco foram explicitamente generalizados. Isso não é um modelo
calibrado de retorno, probabilidade ou perda futura.

## Sugestões, contas e aprendizado

Os limites são lidos do `config.json` existente. As funções compartilhadas de
COMPRE, VENDA, MANTENHA e REALIZE não foram alteradas. O dimensionamento bruto,
limites de posição e combinação operacional de saídas/entradas para realocação
continuam usando os mecanismos existentes por conta/moeda, sem FX ou antecipar
receitas de vendas. Custos desconhecidos não viram zero. Não são ordens ao banco.

Não há fallback silencioso para métricas antigas de cripto quando faltam entradas
do perfil comum. O snapshot original de cripto e o escore descritivo antigo de
ações permanecem preservados como fontes/linha anterior de comparação; **os planos
globais passam a consumir exclusivamente o novo perfil**. Status históricos com
`ORIGINAL` no nome mantêm compatibilidade dos contratos de regras e planos; isso
não significa que os novos índices sejam numericamente iguais aos antigos.

As confirmações de tese fraca usam somente capturas prospectivas deste perfil,
com mesma identidade, provedor, moeda e referência de binding. São necessários
os dois dias UTC completos anteriores; múltiplas leituras no mesmo dia não contam
como dois dias. O histórico retrospectivo de preços não fabrica decisões passadas.

Os resultados de 30/60/90/120 dias continuam sendo registrados pelo acompanhamento
existente. Novas emissões incluem o identificador do perfil na chave, preservando
a leitura e os IDs dos registros anteriores. Os 19 registros antigos não são
reescritos ou reaproveitados como validação do novo perfil. O aprendizado legado
permanece intacto; o perfil novo coleta evidência prospectiva e **não recebe uma
calibração automática validada por esta entrega**.

## Instalação e resultado esperado

Aplicar após V142. O instalador entrega sete módulos, incluindo o novo módulo
comum; pré-valida hashes, recusa divergências/symlinks, faz backup e é idempotente.
Não modifica UI, agendador, intervalo de ciclos, limites de compra/venda, ledger,
saldo, quantidade, configuração financeira ou arquivos de modelos treinados.

O coletor comum roda após a coleta de referências/histórico e antes da captura de
decisões, sem fazer chamadas de rede adicionais. Suas capturas ficam em
`data/observability/common_action_metrics_a24/captures`. Leituras da API/dashboard
não gravam essas capturas. A análise de ações agora informa se o novo perfil está
disponível, em vez de declarar sempre `COMMON_ACTION_INDEX_PROFILE_REQUIRED`.

Depois do ciclo normal concluir, `tools/diagnose_decision_pipeline_a24.py --resumo`
mostra `INDICES_GLOBAIS`, motivos concretos de entradas pendentes, contagens por
conta/moeda e cada sugestão com seu perfil. Fora do pregão, pode continuar havendo
zero índices de ações por falta de cotação atual. `COMPRE` só aparece quando os
novos valores satisfazem os limites reais da configuração; não é forçado pelo patch.

## Verificação e limites da evidência

Testes cobrem invariância de escala, a mesma trajetória reportada pelos dois
provedores, finais de semana, históricos incompletos/futuros/duplicados, preços
inválidos, limites dos índices em 300 trajetórias sintéticas, todos os tipos de
regra com mesma configuração, fluxo real de fonte selada → cotação → índice →
plano de COMPRA → acompanhamento, duas datas completas para confirmação de venda,
separação de IDs antigos/novos e leituras sem alteração de dados/modelos.

Foram conferidos também 78 bundles históricos do pacote já fornecido, nos três
contextos CoinGecko EUR, CoinGecko BRL e BRAPI BRL: todos foram aceitos pela fórmula
sem exceção. Esse ensaio verifica compatibilidade de entradas; **não é backtest,
validação preditiva ou reconstrução de decisões antigas**. Não se consultou o plano
BRAPI do usuário neste ambiente. Fixtures antigas de composição foram atualizadas
para fornecer explicitamente índices do novo perfil, e uma fixture legada recebeu
a prova de escopo EUR que o código anterior já exigia.
