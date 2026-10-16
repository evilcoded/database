# A24 — ativação controlada do leitor global (V5)

Este comando macOS ativa as fontes já instaladas. Não instala patches, não reescreve históricos e não executa migrações. Reinicia somente o listener identificado do Porquinho na porta 8765 com SIGTERM e o launcher canônico `.venv/bin/python -m webapp.server`, no diretório esperado e do usuário atual. Verifica os hashes das fontes atuais, inclusive os patches de pesquisa por moeda, aquisição, migração e leitor. Preserva o listener e o horário de início do Bridge na porta 8787.

Se houver trabalho queued/running, processo inesperado, fonte divergente, listener compartilhado, cadeia P35 inválida ou mudança de estado, recusa a ação. Confere o estado novamente antes de sinalizar. Espera o processo antigo sair; nunca envia SIGKILL e não cria segundo servidor se ele permanecer. Uma trava local impede ativadores simultâneos. O marcador de ativação evita reinício duplicado quando PID, início e hashes continuam iguais.

Após o HTTP responder, observa por até 12 minutos usando apenas GET /api/status e leitura de arquivos. Não envia POST de refresh, treino ou operação financeira. O status HTTP grande é processado por leitura incremental. As rotinas normais já configuradas do aplicativo retomam sua execução, inclusive aprendizagem e atualização dos resultados; o ativador não solicita operações financeiras ou treinamento adicional.

A confirmação GLOBAL_READER_ACTIVATED_AND_OBSERVED exige novo snapshot, ausência de trabalho pendente no momento da observação e um input_contract reconhecido em prediction_lab.json com timestamp entre a ativação conhecida e o momento da leitura. O contrato deve ter contagens coerentes, hash de origem válido, hash do coletor esperado e flags de ausência de autoridade/atestado. Um snapshot novo ou timestamp isolado não basta. A prova é de integração observada, não de validade econômica ou identidade histórica.

O relatório em Downloads inclui a preservação do prefixo dos registros P35 e dos forecasts cold-start anteriores. Não exporta preços, quantidades, saldos ou chaves. O comando não exclui snapshots, previsões, modelos ou versões migradas. Não promete que a aplicação em execução deixará de escrever seus resultados normais.

Se terminar em WAITING_FOR_GLOBAL_READER_RESULT, isso significa ausência de comprovação no período observado, não falha de instalação. Reexecutar o mesmo comando usa o marcador, evitando reinício repetido quando confirmado. A opção `--verificar` impede qualquer reinício, mas só comprova ativação se houver marcador compatível. Não reutilize ativadores anteriores com hashes desatualizados.

## Validação

30 testes com processos simulados: seleção estrita do PID, Bridge preservado, tarefa ativa recusa, mudança de estado recusa, SIGTERM ignorado não cria outro servidor, idempotência por marcador, trava de concorrência, logs e relatórios, preservação de prefixo, contratos antigos/ausentes/inválidos/futuros não comprovam ativação, snapshot novo sem contrato não conclui, e leitura incremental de resposta grande. Nenhum serviço real foi reiniciado no ambiente cloud. A execução no Mac e seu relatório serão a evidência da ativação real.
