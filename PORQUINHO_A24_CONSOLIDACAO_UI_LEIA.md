# A24 — consolidação do acompanhamento e UI das posições

Entrega anexada ao fechamento atual F3 → F4. Não cria fase nova, não encerra as pendências de comparação/sizing/publicação e não emite decisões para retirar o aviso de indisponibilidade.

## Comportamento

A carteira recebe um painel com horário do último sinal do monitor, estado de agendamento, horário do snapshot, resultado do laboratório, presença do contrato do leitor global e quantidade de registros de pesquisa validados no dia UTC. Falha de agendamento é apresentada mesmo quando o heartbeat é recente. A hora do snapshot não é usada como se fosse a hora da cotação individual. Captura diária de pesquisa não é cotação atual de execução.

As linhas das posições mostram o motivo do estado de acompanhamento, sem alterar o badge canônico existente. A associação exige instrumento, conta e moeda explícitos e iguais. Não utiliza ticker, nome de conta, sufixo de ID ou inferência EUR para resolver identidades. Se a UI legada não fornecer os campos, informa que a ligação da posição ainda não está confirmada, em vez de aproveitar um sinal de outro ativo/conta/moeda.

A inspeção lê posições do read model canônico verificado, vínculos explícitos e o journal do dia UTC, cuja cadeia é validada pelo leitor existente. Não escolhe arbitrariamente entre fontes ou posições duplicadas. Registros do journal são contados separadamente dos vínculos: conta não tem correspondência automática só porque há uma cotação com o mesmo símbolo. Os formatos antigos e globais de IDs continuam distintos até uma migração de identidade explícita.

O frontend também deixa de mostrar textos legados como orientação de venda/compra quando não há publicação canônica correspondente. Se existir publicação verificada para o mesmo contexto, o texto usa a ação publicada, não uma ação legada conflitante. Alvo de 0% não é apresentado como ordem de venda, e alvo/risco não comprovam sizing. O patch não altera as telas/autoridades de registro manual de operações.

O backend continua informando o produtor canônico ausente enquanto o contrato prevê zero snapshots canônicos. Uma falha de integração não é relabelada como decisão do Brain de abster-se. A criação das recomendações reais continua no fechamento da F4 com evidência, comparação, sizing e produtor verificados. Não há garantia de evitar perdas financeiras.

## Leitura e preservação

Novo GET `/api/research/monitor-consolidation`, sem POST de atualização, treino ou operação financeira. O frontend consulta esse diagnóstico durante a renderização existente da carteira, no máximo uma vez por 30 segundos, com controle de chamada pendente; não cria um novo scheduler de coleta ou treinamento. O botão Verificar acompanhamento consulta somente esse GET.

A inspeção não escreve snapshots, ledger, modelos, aprendizagem, vínculos, forecasts ou journals. Cada falha de seção resulta em diagnóstico parcial com dados desconhecidos, não em contagem zero fabricada. Campos financeiros e valores de preços não são incluídos no novo diagnóstico. Posições fechadas com quantidade zero não criam ambiguidade para uma posição ativa no mesmo contexto.

## Instalação e ativação

O instalador exige os baselines verificados, executa 427 testes Python e 18 verificações JavaScript numa cópia temporária de fontes, cria backup e aplica as fontes atomicamente por arquivo, com rollback em falhas. Não migra dados históricos.

Depois faz uma inspeção local somente leitura e grava o ativador `PORQUINHO_A24_ATIVAR_CONSOLIDACAO_V6.command` em Downloads. Tenta a ativação controlada: somente SIGTERM para o listener canônico identificado do Porquinho, preservando Bridge, com rechecagem de fontes/PID/tarefas e trava de concorrência. Tarefa queued/running impede o reinício; não envia SIGKILL nem cria outro servidor se o antigo não sair. O aplicativo retomará suas rotinas normais, inclusive aprendizado já configurado; o ativador não solicita refresh ou treino adicional.

A confirmação da ativação exige novo snapshot, contrato do leitor em resultado novo do laboratório e resposta reconhecida do novo endpoint. O relatório inclui as contagens de captura e as causas de ligação das posições, sem exportar o array de identidades/contas no relatório do ativador. O frontend deve ser recarregado após a ativação para carregar o novo JavaScript.

Se a ativação ficar pendente por trabalho ativo, repita somente o ativador em Downloads quando o ciclo terminar. Reexecutar o instalador já aplicado verifica os hashes e testes e encerra sem novo reinício. O marcador do ativador evita reinícios duplicados quando PID, início e hashes coincidem.

Para testes cloud, `PORQUINHO_SKIP_ACTIVATION=1` adia explicitamente a ativação e `PORQUINHO_ACTIVATOR_DIRECTORY` escolhe uma pasta fora do projeto para gerar o ativador. Não são necessários para o uso normal no Mac.

## Verificação

427 testes Python e 18 verificações de frontend aprovados com pandas 2.2.3 e 3.0.3. Cobertura nova: contexto exato, moedas arbitrárias, fontes múltiplas, ausência de dados, journal real sintético validado, posição fechada, heartbeat obsoleto/futuro, falha de seção, estado canônico não promovido, rota GET com POST recusado, ausência de escrita/rede, HTML escapado, throttling, textos legados bloqueados e uso da ação canônica quando corresponde.

Instalador exercitado com aplicação, repetição, divergência de baseline recusada, CSV original e sentinela preservados. Ativador: 32 testes com processos/HTTP simulados, incluindo preservação do Bridge, recusa de tarefas, PID/launcher/código, SIGTERM ignorado, concorrência, contratos antigos/futuros, leitura incremental e GET do diagnóstico. Nenhum processo real do Mac foi reiniciado nesses testes. Não houve verificação num navegador macOS; os testes de frontend usam Node/DOM simulado. A saída local será a evidência da ativação e da captura real.
