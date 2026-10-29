# V141 R2 — correção do contrato HTTP da BRAPI

O ciclo real do V141 registrou `PROVIDER_HTTP_404` para os nove ativos e nenhuma
cotação atual. O coletor e o radar reutilizavam um separador incorreto: ponto e
vírgula. Agora ambos usam o mesmo construtor de URL, com vírgulas e cada código
escapado individualmente, preservando o gateway existente de credenciais.

Contrato externo conferido no SDK oficial, revisão fixa:
https://github.com/brapi-dev/brapi-python/blob/4ffd1c37684abb3910a3c70c3cd33f682a226c40/src/brapi/resources/quote.py#L125

A documentação de `quote.retrieve` declara `PETR4,VALE3` no caminho
`/api/quote/{tickers}`. Não houve consulta autenticada à BRAPI neste ambiente:
o acesso direto a brapi.dev foi recusado pelo proxy. Portanto o teste local
comprova o formato e as proteções, mas a resposta real dependerá do próximo
ciclo normal no Mac. Não repetir consultas em caso de 429 ou relaxar validade
para produzir uma cotação aparentemente atual.

## Instalação

Aplicar após V141, usando o Python e o reinício verificado já existentes.
O instalador modifica somente:

- `market_data/global_quote_transport_a24.py`
- `universal_portfolio/brapi_research_acquisition_a24.py`

Pré-valida hashes, recusa divergências e symlinks, faz backup e aceita reaplicação.
Não modifica a UI V140, configuração, limites, ledger, modelos ou histórico.
Mantém limite de requisições, cache de dez minutos, separação entre primeira
observação diária e referências intradiárias, identidade e moeda exatas,
atualidade do timestamp do provedor e revalidação de contexto antes da gravação.

Depois do ciclo normal, executar o diagnóstico existente com `--resumo`.
Uma cotação fora da janela de atualidade continuará indisponível, inclusive após
fechamento da bolsa; horário da coleta não substitui horário do preço.

## Integração global: resultado da revisão

Esta revisão de rota **não resolve** `COMMON_ACTION_INDEX_PROFILE_REQUIRED`.
O problema remanescente é de significado dos índices, não de encaminhamento HTTP.

O produtor atual de ações entrega escore de evidências em [-1,1] e cobertura
independente em [0,1]. O mecanismo original global recebe índices separados de
entrada, risco, assimetria, reversão e potencial, com regras comuns configuradas.
Transformar o escore por `(score+1)*50` não produz esses cinco índices. Cobertura
não é potencial, nem probabilidade. Despachar ações para os limites antigos de
`equities.decision` também criaria uma segunda política de decisão, contrariando
a exigência de limites globais.

Além da escala, o cálculo original usa retorno de 7/30 dias, giro monetário sobre
capitalização, drawdown desde máxima histórica, retorno relativo ao BTC, regime
por dominância BTC e uma referência monetária explícita para faixa de tamanho.
As fontes BRAPI disponíveis têm volume em quantidade de ações e máxima de 52
semanas. Não são, respectivamente, giro monetário e máxima histórica. Histórico
atual de 62 observações tem 14/15 indicadores técnicos; a SMA200 pendente não é
um novo bloqueio de compra imposto por esta entrega.

A consolidação continua exigindo entradas de significado comum e uma versão
explícita do perfil de índices. Não se deve preencher ausência com zero, copiar
métricas EUR para BRL, selecionar BTC como benchmark de ações implicitamente,
ativar um modelo experimental ou anunciar recomendações de ações concluídas.
O registro prospectivo de 19 leituras e seus horizontes continua independente.

## Verificação

Testes do coletor, cache, contexto, holdings, agendamento e radar passaram.
O teste novo verifica uma URL literal do contrato externo, reproduz 404 com o
separador antigo e executa o coletor com os nove ativos no formato correto.
O teste anterior foi corrigido: seu servidor simulado repetia o mesmo erro de
separador da implementação. O instalador foi verificado quanto a reaplicação,
divergência antes de qualquer escrita e preservação de dados/modelos sentinela.
