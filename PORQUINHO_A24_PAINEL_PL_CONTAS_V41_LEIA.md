# A24 V41 — P/L, contas e filtros

Requer V40 R1 aplicado. SHA256: `5b9ebba9e1a66dfb953f1ef4b6efbbd53688680fbc589a033cb2231b4cbbed4f`.

O P/L observado das posições aparece independentemente de existir o intervalo de10min. Prioridade: posições com cotações de referência exatas e completas; snapshot explícito por moeda; referência legada EUR sob contrato conhecido, sem filtro de conta/ativo; último P/L total armazenado como fallback datado. Não se infere moeda por sufixo, não se somam moedas e não se substitui dado ausente por zero. A variação de10min é rotulada separadamente como variação do P/L total, podendo ficar indisponível sem esconder o valor principal. Datas/origem acompanham os valores. Cotações de referência e snapshots não são preços de execução ou resultados certificados.

P/L no topo, substituindo Estado do sistema; Estado ao lado do intraday em grade2:1, com intraday compacto. Campos/rótulos transparentes; superfícies azuis mantidas nos controles. Correção do seletor Universo inclui o controle visual Emerald (a largura mínima170px do wrapper causava sobreposição), não apenas o select nativo.

Contas e Bancos abre diretamente a gestão completa anterior, com todos os registros, ações e planejamentos existentes. Não herda o filtro EUR do Dashboard. As funções originais de cadastro, edição, planejamento, reserva e registro de transações são reutilizadas sem alterar suas validações ou guards. Nenhum cadastro/transação/planejamento é criado pelo patch.

Benchmark: o gráfico existente comparava variação patrimonial incluindo aportes/retiradas com preço de um ativo; não era retorno da carteira ajustado por fluxos. A V41 corrige essa identificação para Patrimônio vs Benchmark, mostra número de datas comuns e período, e mantém a primeira data/moeda comum. Há filtro de classe do benchmark com Todos e retorno à seleção completa. Esse filtro não reconstitui carteiras históricas por classe. A tela Ativos também recebe tipo de ativo com Todos. Ausência de série compatível continua explícita. Não calcula alpha ou rentabilidade ajustada sem evidência de fluxos reconciliados.

## Aplicação

O instalador verifica168 baselines, valida em cópia temporária, faz backup e aplica atomicamente. Não exige nem modifica run_monitor_ui_regressions.py local (correção de empacotamento R1 preservada). Brain, modelos, aprendizagem, dados, memória e histórico não estão no conjunto alterado. A ativação controlada preserva Bridge8787 e recusa trabalhos ativos. Caso precise, repita somente `~/Downloads/PORQUINHO_A24_ATIVAR_CONSOLIDACAO_V41.command` quando o ciclo terminar. Cmd+Shift+R após ativação.

## Validação

1126 testes Python +231 verificações JavaScript;38 testes do ativador. Chromium com o seletor Emerald real: classe do benchmark/Todos e períodos, perda atual exibida e vermelha, header com8 leituras sem sobreposição, intraday2:1, roteamento para funções originais de contas, desktop/iPhone390px sem overflow ou erroJS. Fontes sintéticas isoladas: não comprova os registros reais do Mac. Instalador aplicado/repetido, backup único, baseline divergente recusado, sentinelas de dados/modelos/histórico e helper local preservados. Nenhuma operação financeira executada pelos testes. Conferência real de P/L, contas e filtros pendente após instalação no Mac.
