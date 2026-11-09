# V152 — elimina recomputações idênticas dentro da leitura do dashboard

O traceback de uma inspeção local interrompida após 15s apontou `recovered_history_composition.compose → validate → global_history_source.validate_bundle → global_research_lab.experiment → research_economic_components.prepare → universal_observation_bridge → monitor.inspect`. A rota da interface não retornou bytes em 20s. Isso localiza trabalho na leitura; não demonstra que seja a única causa de lentidão no ambiente do usuário.

A inspeção agora abre um escopo de reutilização em memória. Experiências determinísticas e validações de histórico idênticas são calculadas uma vez nesse escopo. Chaves incluem conteúdo completo, data/hora e caminho. Mudanças de fonte, conta/moeda no conteúdo ou parâmetros invalidam o reuso. Exceções não são guardadas. Resultados calculados são copiados para impedir contaminação por mutação. Validações que retornam o próprio corpo continuam retornando o objeto atual do chamador.

ContextVar isola requisições/threads; escopo termina inclusive em erro, sem cache em disco ou entre requisições. Limite de 128 entradas/32MiB; ao exceder, o cálculo original continua. Chamadas fora da inspeção preservam comportamento original. Não elimina o custo da primeira execução de cada fonte distinta e não impõe timeout a todo o backend.

Não altera fórmulas, limites, resultados, autoridades, ordens, dados financeiros, modelos salvos ou layout. Não substitui validação por aceitação de dados gravados. O arquivo novo apenas auxilia os quatro módulos existentes.

Validação: 118 testes passaram (85 regressões de pesquisa/histórico/componentes/modelos, 28 de consolidação e cinco de escopo). Cobertura de resultado real integral idêntico, fonte adulterada rejeitada mesmo após acerto de cache, chaves de tempo/caminho/conteúdo, isolamento de threads, encerramento em erro, exceções não guardadas e limites. Teste sintético de 20 experiências idênticas com 364 pontos: 0,381s sem escopo e 0,044s com escopo (8,8× nessa carga; não é medição no Mac do usuário).

Instalador: backup, cinco payloads, hashes da base, recusa de divergência antes de escrita, idempotência e sentinelas financeiras/configuração/modelos preservadas. Validação sintética dos cinco fluxos e atualização apenas do registro descritivo do conhecimento mantidas.

Aplicar sem `--reiniciar`. No Terminal que mantém Flask aberto, Ctrl+C para encerrar o servidor e depois iniciar `/bin/bash /Applications/Bridge_Companion/porquinho_v33_web_foundation-2/start_web.command`. A opção antiga de reinício pode esperar pelas rotas lentas do processo antigo; não há encerramento forçado neste patch. Após reiniciar, Cmd+Shift+R e medir novamente a rota de consolidação se necessário.
