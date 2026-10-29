# V142 — BRAPI com um ativo por requisição

O provedor confirmou no ambiente do usuário `QUOTES_PER_REQUEST_EXCEEDED`:
o plano permite um ativo por chamada e recusou o lote de nove. A rota corrigida
no V141 R2 está correta; esta entrega adapta o consumo ao limite confirmado,
sem exigir troca de plano ou modificar regras de decisão.

## Comportamento

- Uma identidade BRAPI por requisição autenticada, pelo gateway existente.
- No máximo duas chamadas BRAPI por execução do coletor operacional. `max_jobs`
  pode reduzir esse número, nunca aumentá-lo.
- Referências atuais já obtidas são reutilizadas por dez minutos. Uma tentativa
  recente também é adiada por dez minutos, mesmo quando a resposta foi antiga,
  inválida ou falhou. Isso evita repetir consultas inúteis ao mesmo ativo.
- A fila ordena pela tentativa mais antiga e desempata pela identidade, sem
  classificar investimentos. Tentativas persistem antes da chamada HTTP e
  sobrevivem a reinícios; uma falha não prende o coletor aos primeiros ativos.
- Para nove ativos e respostas válidas, a população inicial é atendida em até
  cinco execuções normais: 2 + 2 + 2 + 2 + 1. Não há nove chamadas em uma execução.
  Se o intervalo entre execuções for grande, referências anteriores podem perder
  atualidade; esta entrega não promete cobertura simultânea nem altera o timer.
- HTTP 429 interrompe as chamadas restantes e mantém pausa de dez minutos entre
  execuções. HTTP 401/403 também interrompe e pausa para não repetir falha de
  autenticação em todos os ativos. Não há repetição imediata.
- O radar padrão passa a ler as referências do coletor, com identidade/moeda e
  registro de fonte compatíveis. Abrir o radar não dispara outra consulta BRAPI.
  O adaptador direto recusa listas com mais de um ativo antes de fazer rede.
  CoinGecko mantém seu transporte existente.

O limite mensal/hora do plano não foi fornecido. O teto de duas chamadas por
execução e a pausa por ativo reduzem o consumo, mas não certificam adequação a
uma quota mensal desconhecida. Outros coletores existentes, por exemplo o de
histórico diário, mantêm seus próprios limites e não foram alterados.

## Persistência e segurança dos dados

A única nova persistência é a agenda operacional
`data/brain/research_quote_observations_a24/brapi_request_schedule.json`.
Ela contém schema, hashes de bindings, horários de tentativa e pausa; não contém
token, preço, saldo, modelo ou sugestão. É escrita atomicamente sob o lock do
coletor. Arquivo inválido ou symlink impede novas chamadas, sem apagar dados.

O preço só é publicado após as validações existentes de identidade, moeda,
atualidade e contexto. Uma tentativa recente **não** transforma uma cotação
antiga em atual. O journal diário preserva a primeira observação válida, e as
referências intradiárias continuam separadas. Não há alteração financeira,
conversão cambial, treinamento ou ativação de modelo.

## Instalação e diagnóstico

Aplicar após V141 R2. O instalador valida todos os hashes antes da escrita,
recusa divergência/symlink, faz backup e permite reaplicação idempotente.
São quatro arquivos de código: coletor, adaptador de transporte, radar e CLI
de diagnóstico. Nenhum arquivo de UI, configuração financeira ou modelo.

Após reinício e ciclo normal, executar `tools/diagnose_decision_pipeline_a24.py --resumo` com o Python isolado do projeto. `COTACOES_NATIVAS` inclui agora:
`assets_per_request: 1`, `request_limit: 2`, `network_requests`, referências em
cache, atualizadas, adiadas e em pausa. `deferred_job_count` representa trabalho
pendente, não falha nem inexistência dos ativos.

Um preço antigo após fechamento pode resultar em `SOURCE_OBSERVATION_NOT_CURRENT`.
Ausência de `QUOTES_PER_REQUEST_EXCEEDED`/HTTP400 confirma só esta parte do
transporte. `COMMON_ACTION_INDEX_PROFILE_REQUIRED` continua uma pendência
separada da integração dos índices de decisão das ações.

## Verificação

143 testes passaram, incluindo o cenário de um ativo por requisição, os nove
ativos distribuídos entre execuções, cache, rotação com preços antigos/falhas,
pausa persistente para 429/401, preservação do journal diário, holdings verificados,
contexto alterado durante consulta e radar sem rede/escritas. O instalador foi
testado para backup, idempotência, recusa de divergências e preservação de
sentinelas de dados e modelos. O teste de rede usa um provedor simulado que
recusa qualquer URL com múltiplos ativos; não houve acesso autenticado ao plano
do usuário neste ambiente.
