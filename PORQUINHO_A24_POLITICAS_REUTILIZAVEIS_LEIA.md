# A24 — Políticas reutilizáveis por conta e moeda (V23)

Consolidação F3/F4. Registro de políticas definidas pelo usuário para risco,
liquidez e concentração. Uma definição atende várias alternativas de sua conta,
moeda e horizonte, com vínculo opcional a plano manual ativo. Não há moeda-base,
lista fixa de moedas, conversão cambial ou associação por símbolo.

O instalador modifica apenas código, mantém backup e executa regressões em cópia
temporária. Não cadastra políticas, escolhe limites, altera planos/orçamentos ou
reescreve snapshots, ledger, memória, modelos e registros maturados. O ativador
V23 segue a guarda existente: somente Porquinho, preservando Bridge, sem SIGKILL,
segundo servidor, refresh manual ou operação financeira. Se estiver ocupado,
repetir apenas o ativador indicado após o ciclo normal.

## O que passa a funcionar

`data/account_action_policies_a24.json` é um novo registro criado somente quando
um usuário aplica uma política explicitamente revisada. Revisões são acrescentadas
sem remover versões anteriores, com hash encadeado, bloqueio de escrita, gravação
atômica e conferência do digest esperado. Repetir exatamente a última revisão é
idempotente; alterar uma revisão existente é recusado. Alterar escopo exige outro
ID, evitando mover silenciosamente políticas entre contas, moedas ou horizontes.

Cada política informa início e fim de validade e a data de registro é preservada.
Não é utilizada antes de ter sido registrada e não é aplicada retroativamente a
decisões ou histórico. A última revisão substitui a anterior para resolução atual:
uma revisão futura ou expirada não faz a anterior voltar a vigorar. Uma revisão
REVOKED desativa o uso sem apagar o histórico. A integridade local por hash não é
atestado independente.

O avaliador existente consome as políticas vigentes para as alternativas atuais.
Um plano opcional deve existir e estar ativo, ser manual e corresponder à conta e
moeda. Se deixar de satisfazer essas condições, sua política não é selecionada.
Não há prioridade implícita entre uma política geral e outra de plano: múltiplas
definições compatíveis deixam a dimensão indisponível por ambiguidade. Uma política
direta do contrato V22 que conflite com a reutilizável também é recusada.

Políticas não fabricam evidência, exposição contrafactual, retorno esperado ou
capacidade de liquidez. Os três avaliadores originais continuam exigindo métricas,
unidades, maturidade, calibração e proveniência compatíveis. Um limite cadastrado
sem evidência validada deixa o resultado desconhecido. Nem a política nem uma
aceitação de cenário produzem valor de ordem, reserva de cash, autorização de
execução ou publicação canônica.

O painel de alternativas mostra contagens de políticas vigentes, versões e
correspondências, preservando a abertura das seções. O resumo não exporta contas,
limites ou valores de cenário. Instalar/ativar não significa que limites foram
definidos ou modelos validados.

## Configuração local explícita

Neste patch a configuração é feita pela ferramenta local, sem novo formulário
na UI. Execute na raiz do projeto com seu Python do ambiente:

```bash
.venv/bin/python -I -B tools/configure_account_policies_a24.py status
.venv/bin/python -I -B tools/configure_account_policies_a24.py check /caminho/politica_revisada.json
```

`status` e `check` são somente leitura. `check` valida a próxima revisão contra
contas e planos atuais e retorna o digest esperado; não grava políticas.

Somente após revisar os limites e a definição completa, aplique com:

```bash
.venv/bin/python -I -B tools/configure_account_policies_a24.py apply /caminho/politica_revisada.json \
  --expected-digest DIGEST_RETORNADO_PELA_CONFERENCIA \
  --confirm CONFIRM_USER_POLICIES_RESEARCH_ONLY
```

Aplicar grava apenas o novo registro de configuração e seu arquivo de lock.
Não reinicia serviços. Após o V23 estar ativo, as leituras normais do monitor
passam a resolver as políticas configuradas, sem novo patch por conta ou ativo.

O arquivo de revisão contém exatamente: policy_id, revision (inteiro iniciado em
1), status (ACTIVE/REVOKED), dimension (risk/liquidity/concentration), account_id,
currency, plan_id (null ou ID real), horizon_unit (OBSERVATIONS/DAYS), horizon_value
(inteiro positivo), effective_from, effective_until e definition. Horários precisam
de fuso explícito. Os IDs e moeda são os existentes no registro de contas.

`definition` obedece ao contrato original da dimensão, com source=USER_DEFINED,
validated=true somente após revisão explícita do limite, proveniência e referências
exigidas pelo respectivo avaliador. Essa revisão se refere à política do usuário,
não à validação de um modelo. policy_id, conta, moeda e effective_from devem
coincidir com o envelope; policy_version (risco/liquidez) ou version (concentração)
deve ser a revisão representada como string. Risco declara também o horizonte
exato, como unidade e valor do envelope separados por dois-pontos. Nenhum campo
de política é preenchido automaticamente a partir da estratégia do plano.

Os contratos completos existentes são:

- universal_portfolio/universal_adaptive_risk_policy_authority.py
- universal_portfolio/universal_adaptive_liquidity_policy_authority.py
- universal_portfolio/universal_concentration_policy_authority.py

Não são entregues políticas prontas com números arbitrários. Faltam definir os
limites do usuário, fornecer evidências econômicas validadas, custos aplicáveis,
utilidade, sizing e integrar o produtor canônico independente. Este patch não
declara A24 concluída.

## Validação

878 testes Python e 94 verificações JavaScript em pandas 2.2.3 e 3.0.3, sem skips.
24 novos testes cobrem os três contratos reais, conta/moeda/plano/horizonte,
expiração e uso não retroativo, versões, revogação, idempotência, concorrência,
ambiguidade, conflito com V22, privacidade e preservação dos dados.
33 testes simulados do ativador. Fixtures sintéticas; não comprovam políticas
preenchidas no Mac nem validação financeira.
