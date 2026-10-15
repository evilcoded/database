# A24 — instrumentos efetivamente acompanhados pelo Brain

Coleta de revisão, sem validação econômica ou vínculo automático. Lê as previsões persistidas de results/prediction_lab.json e as observações de results/latest.json separadamente. Não comprova todo o universo global: candidatos shadow que existam somente em memória ficam fora desta coleta.

Exporta rótulo, identidade/origem/moeda quando explícitos, unidade declarada, grupos champion/ensemble e datas das observações. Mostra contagem/cobertura histórica pelo rótulo exato, explicitamente sem tratar esse agrupamento como prova de identidade. Quando a previsão já possui identidade e origem completas, conta observações iniciais da mesma identidade, provedor, provider_id, moeda e data; duplicatas aparecem como contagem maior que um, não são eliminadas para fingir validação.

Inclui referências de identidade dos catálogos existentes separadas dos casos: não as associa por símbolo ou sufixo, não normaliza IDs e não cria identidades. Moeda da conta não é tratada como cotação. Previsões de champion/ensemble com o mesmo contexto são um caso de revisão, preservando os grupos e as datas; contagens originais também são exportadas.

Para posições atuais, chama o modelo de leitura real canonical_runtime_read_model.build, com hash do módulo principal conferido e audit hook bloqueando escrita, rede e processos. O modelo deriva a visão usando seus verificadores existentes. Exporta somente IDs de posições com quantidade não nula/zero; valores positivos e negativos não são exportados. Quantidade/identidade ausente é reportada como indisponível. Não exporta contas, quantidades, custos, saldos, preços, valores ou percentuais de previsão. Se a leitura falhar, não substitui por carteira legada ou catálogo.

O cruzamento com a carteira usa igualdade literal de instrument_id. Identidade ausente ou carteira indisponível significa resultado indeterminado (null), não prova de ausência da carteira. Não associa ticker/sufixo a identidade para preencher essa lacuna. Vínculos globais e comparações econômicas permanecem pendentes até revisão explícita.

A inspeção ocorre em subprocesso Python -I -B, sem iniciar servidor, refresh, coleta de mercado, treino ou operação financeira. Audit hook bloqueia efeitos colaterais. Arquivos alterados durante a leitura provocam recusa do pacote. O processo externo grava exclusivamente em Downloads (ou PORQUINHO_REVIEW_DIR fora do projeto) um ZIP com BRAIN_UNIVERSE_REVIEW.json e manifesto SHA256. O nome usa o horário Europe/Lisbon.

O pacote gerado no Mac contém identificadores reais necessários à revisão e deve ser compartilhado aqui pelo usuário; ele não será publicado automaticamente no GitHub. Esta entrega pública contém somente código, testes e documentação, sem os dados coletados.

Verificados: 14 testes com fixtures temporárias — preservação de identidades, contextos separados, deduplicação de grupos, ausência explícita, duplicata histórica, não associação por símbolo, privacidade, recusa de symlink/escrita, leitura sem alterações, exportação do ZIP, manifesto e indisponibilidade da carteira. A extração de posições foi testada com modelo simulado; a execução real do modelo no Mac será evidência local. Sintaxe Bash conferida.
