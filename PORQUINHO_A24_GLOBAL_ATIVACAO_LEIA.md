# A24 — ativação global V4 e diagnóstico de vínculos

Requer os patches globais V2 e de reconciliação já aplicados. Esta ferramenta não altera fontes da aplicação.

Confere 11 hashes de fontes, o único listener 8765, proprietário, diretório de trabalho e launcher .venv/bin/python -m webapp.server. Recusa trabalhos ativos/em fila, divergências de código e processo compartilhado com o Bridge. Confere novamente a identidade, hashes e Bridge imediatamente antes do sinal.

Usa SIGTERM somente no processo identificado, como na ativação V3 bem-sucedida. Aguarda sua saída por até 45 segundos; não usa SIGKILL nem inicia outro servidor enquanto o antigo permanecer. Inicia o mesmo launcher em sessão separada, com log em Downloads, confere HTTP e registra PID/início/hashes para evitar reinícios repetidos. O marcador anterior da captura não comprova ativação global, pois os hashes agora incluem os novos arquivos.

Depois aguarda até 12 minutos pelo ciclo normal, fazendo apenas GET /api/status. A resposta é processada em memória limitada, retendo snapshot.timestamp e jobs.status. Um timestamp deve avançar para contar como snapshot novo. Não envia POST, pedido de atualização, compra, venda, treinamento ou publicação. O aplicativo retoma suas rotinas normais existentes; elas podem produzir dados e aprendizado segundo a configuração vigente.

O diagnóstico lê market_daily.csv, prediction_lab.json e o journal P35E. Exporta somente contagens de campos ausentes, situações de vínculo e timestamps. Não deduz identidade de ticker ou _eur, não converte moedas, não altera registros nem exporta dados individuais. Distingue linhas históricas da data mais recente e previsões champion/ensemble. Verifica a cadeia local P35E e compara o prefixo antigo antes/depois, sem tratá-la como arquivo independente atestado. Leituras que mudam durante a inspeção são sinalizadas; o diagnóstico posterior pode ficar indisponível sem apagar o resultado do reinício.

O relatório, salvo em Downloads/PORQUINHO_A24_GLOBAL_ACTIVATION_*.json, distingue:

- fontes verificadas e processo compatível iniciado/marcador compatível;
- snapshot novo observado em ciclo normal;
- timestamp do resultado do laboratório posterior à ativação;
- metadados explícitos, ausentes ou não verificados em cada estágio;
- preservação do prefixo do journal e dos arquivos cold-start existentes.

Uma nova previsão do laboratório pode não aparecer no primeiro ciclo. Seu timestamp posterior, sozinho, também não certifica a cadeia de produção ou o modelo. Nenhum desses sinais autoriza promoção canônica. independent_global_identity_binding_proven permanece false: esta ferramenta não faz atestado independente de identidades. Uma contagem EXPLICIT_BINDING_UNATTESTED significa apenas metadados presentes no arquivo.

Verificação cloud: 43 testes — 18 de orquestração com processos simulados; 12 do leitor HTTP, incluindo resposta de 34 MiB; 13 de diagnóstico com arquivos temporários. Não houve reinício de processo real do Mac pelo assistente. A evidência local virá da execução pelo usuário. Bash verificado com bash -n.

Para repetir só a observação, sem reiniciar: ./PORQUINHO_A24_ATIVAR_GLOBAL_V4.command --verificar. A ferramenta também evita novo reinício quando encontra o mesmo PID/início e todos os hashes do marcador V4.
