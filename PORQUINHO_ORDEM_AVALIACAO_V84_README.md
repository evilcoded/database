# Ordem da avaliação econômica — V84

O refresh compunha a avaliação econômica antes de coletar observações, atualizar os experimentos e produzir componentes. A projeção econômica daquele ciclo, portanto, não podia incorporar os novos resultados produzidos em seguida.

A nova sequência lê a demanda de pesquisa atual, executa os produtores existentes na mesma ordem e com os mesmos critérios, e só então recompõe o bridge e chama o avaliador existente uma vez. A resposta preserva os resultados dos produtores e inclui decision_input_phase=AFTER_RESEARCH_STAGES. Uma exceção invalida a projeção do ciclo e permanece visível como SHADOW_ERROR.

Esta alteração não cria evidências, políticas de risco, tarifas ou recomendações finais; não troca runtime_wiring do contrato canônico para true e não altera modelos ou os critérios de validação. O produtor de publicação final e as entradas econômicas ausentes continuam pendentes. O avaliador já era chamado antes deste patch; o problema corrigido é sua posição no ciclo, não a ausência total da chamada.

Validação: 131 testes de handoff, comparação por conta/moeda, histórico, laboratório e componentes; teste executa o bloco real de refresh com produtores sintéticos e verifica ordem, estado atualizado, chamada única e falhas. Instalador testado com repetição e preservação de base divergente. Nenhum teste usa dados reais para gerar sugestões.

Instalação: backup e substituição de webapp/server.py com hashes. Aguarde o ciclo terminar, encerre somente o servidor Porquinho com Ctrl+C e reinicie pelo start_web.command de /Applications. O Bridge não precisa ser reiniciado.
