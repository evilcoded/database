# A24 V43 — Realocação consolidada e diagnóstico das fontes

Requer V42 instalado. SHA256: `ed1e1c774e05170f4af120cedf1829b1e9c8b785304dd9d24f6c34c1cd1b6a11`.

## Entrega

Um cartão por par reúne comparação, capital, disponibilidade de custos e valores de cenário; elimina a duplicação entre os portlets bruto e líquido. Comparação e custos continuam acessíveis em popups com Voltar e pelo botão Todas as comparações. Filtros de conta, moeda e pesquisa preservados. Não altera contas, P/L, intraday ou acesso móvel.

O comparador distingue: vínculo somente de pesquisa sem identidade financeira, quantidade ausente, cotação exata ausente, cotação ambígua ou quantidade/preço não positivos. As fontes são conferidas por identidade, provedor, moeda e origem da previsão; não por ticker. Campos existentes de capital e cálculo líquido não são reatribuídos. Os diagnósticos de custos separam venda/compra e componentes desconhecidos. Não estima uma tarifa nova a partir de uma taxa antiga.

## O que ainda depende dos dados reais

O print V42 mostra SOL sem capital financeiro exato, mas não demonstra qual vínculo ou entrada falta. Este patch informa a causa; NÃO aplica identidade financeira automaticamente. Da mesma forma, não fabrica cotações de custos para preencher os zero cenários completos do relatório anterior. Decisão final, valor aprovado, liquidez e execução continuam separados da pesquisa.

O instalador cria `PORQUINHO_A24_DIAGNOSTICO_FONTES_V43.command` em Downloads e executa o diagnóstico. Ao terminar, imprime `ZIP_PARA_COMPARTILHAR=...`. O ZIP local contém:

- IDs de posição/instrumento/conta, moeda, instituições e jurisdições registradas;
- IDs financeiros e de pesquisa, contextos de origem/provedor dos modelos e motivos de falta de capital;
- disponibilidade de quantidade/preço (somente booleanos), contagens/estados de fontes de custos e nomes dos campos de precificação declarados;
- somente os campos de identidade das fontes de abertura, vínculos canônicos, fontes de mercado e catálogo existentes.

Não contém saldos, quantidades, preços, custos monetários, previsões numéricas, transações, credenciais ou cópias de arquivos brutos. Nomes de instituições e identificadores são incluídos para revisão; nomes pessoais de contas e revisores não são exportados pelos campos selecionados. Documentos de fonte não reconhecidos são reportados como desconhecidos, sem interpretar seu conteúdo como instruções ou inferir vínculos.

O ZIP é criado apenas em Downloads, com permissão600 e nome exclusivo; nenhum upload é automático. Fontes são lidas com limites e conferência de estabilidade; mudanças durante leitura pedem repetição. O helper exige saída fora do projeto. Repetição do diagnóstico não depende de novo reinício. Se falhar, execute somente o helper de diagnóstico quando o ciclo normal terminar.

## Aplicação e preservação

174 baselines, validação em cópia temporária, backup e aplicação atômica. Não exige nem sobrescreve run_monitor_ui_regressions.py local. Sem escrita em ledger, posições, cash, modelos, memória, aprendizagem, snapshots, journals ou vínculos. Nenhuma coleta de rede ou treinamento solicitado pelo diagnóstico. Rotinas normais já configuradas no aplicativo não são desligadas.

Ativador V43 preserva Bridge8787, recusa trabalhos ativos e reinicia somente Porquinho8765. Se estiver ocupado, repita apenas `~/Downloads/PORQUINHO_A24_ATIVAR_CONSOLIDACAO_V43.command`. Cmd+Shift+R depois da ativação. Relatório de ativação continua agregado, sem valores financeiros individuais.

## Validação

1156 testes Python +247 verificações JavaScript;38 testes simulados de ativação. Classificação dos casos de valoração, fontes parciais de custos, redacão de campos privados/números aninhados, ZIP privado/exclusivo/fora do projeto, recusa de fontes alteradas e preservação dos originais. Chromium: dois pares exibidos uma vez cada, motivo do vínculo só de pesquisa separado de quantidade/preço, cenários anteriores preservados, popup/Voltar, desktop/mobile390 sem overflow ou erroJS. Instalador aplicado/repetido com backup único, baseline divergente recusada, helper local e sentinelas de dados/modelos/histórico intactos; dois ZIPs locais gerados no fixture. Testes sintéticos: a correção efetiva da ligação e das fontes do Mac depende de revisão do ZIP real, sem certificar retornos ou fechar F3/F4 por alteração de layout.
