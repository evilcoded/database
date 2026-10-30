# V148 — dashboard compacto, layout local e alertas de avaliação

Entrega de apresentação sobre V147. Quatro arquivos: nova camada JS/CSS, template e registro descritivo do Brain. Não modifica decisões, critérios, valores, fontes, modelos, dados financeiros ou agendamento.

## Interface compacta

- O seletor de módulos mostra o ícone do módulo ativo ao lado do nome. A lista original continua com ícones, rotas e controles existentes.
- Cabeçalho e destaques ficam centralizados e limitados a 1320px; redução de altura, espaçamentos e tamanho dos gráficos.
- Gráficos SVG do dashboard passam a aproximadamente 145–155px de altura. Mantêm os mesmos registros, filtros, fontes e detalhes clicáveis.
- Tabelas de desempenho por ativo usam colunas fixas, quebra de texto e limites para rótulos longos. A moeda fica explícita no título. Os detalhes completos continuam no clique da posição.

## Portlets dinâmicos

“Personalizar layout” habilita uma alça de arraste, botões antes/depois e tamanhos Pequeno, Médio e Largo. “Concluir edição” oculta esses controles. Os tamanhos ocupam 4/6/12 colunas em tela larga, ajustando-se a duas ou uma coluna em telas menores. Os gráficos preservam sua proporção e não são recalculados pelo redimensionamento.

- Arraste nativo no desktop, com colocação antes/depois conforme a metade do portlet de destino. Suporte de ponteiro em alças touch/pen e botões de movimento utilizáveis por toque ou teclado.
- Preferências salvas automaticamente no armazenamento local deste navegador, independentes dos dados financeiros. Não é sincronização de conta ou entre dispositivos.
- Os controles e conteúdos existentes são movidos como nós DOM, preservando cliques e identificadores. Atualizações da tela reaplicam ordem e tamanhos.
- Layout preserva preferências de portlets temporariamente ausentes por filtro. “Restaurar padrão” limpa somente a preferência de layout.
- Em celular, os portlets ocupam a largura disponível para preservar legibilidade. A edição é reversível e não altera carteira ou recomendações.

## Alertas no topo

Uma faixa exibe transições explícitas de ação ou de disponibilidade/dimensionamento da avaliação, por identidade exata do ativo, conta e moeda. Exemplos: ACOMPANHE → COMPRA ou referência disponível → valor pendente. Os detalhes listam até 20 mudanças recentes observadas neste navegador, e os avisos podem ser dispensados.

A primeira leitura estabelece a referência sem alarmar. Alterar moeda, conta, busca ou layout não constitui mudança de avaliação. Leituras anteriores ao estado já observado não revertem a referência. Estados tecnicamente equivalentes são normalizados; oscilações dos valores numéricos dos índices, sem mudança de estado, não produzem avisos. Não é notificação de negócio executado nem previsão de mercado. Não infere remoção de ativo apenas por ausência em uma resposta parcial.

O armazenamento local contém identificadores/estados e avisos, sem gravar saldos, quantidades ou modelos. Acompanhamento funciona entre atualizações e recarregamentos deste navegador; não substitui um histórico de auditoria no servidor.

## Validação

- DOM completo: reordenação, tamanho, reaplicação, restauração, ícone, primeira leitura sem aviso, filtros sem falso aviso, mudança real de ação/estado, deduplicação e recusa de leitura antiga. Regressões dos gráficos globais e das cinco sugestões V146.
- Chromium real em desktop 1440×1100 e celular 390×844: arraste nativo, redimensionamento, preferências, tabelas com identificação extensa sem overflow horizontal, fontes/gráficos, navegação e teclado. Nenhum erro JS; apenas o clique manual explícito chama o endpoint de ciclo existente em simulação.
- Instalador com backup, verificação de dependências V146/V147, recusa de divergência antes de escrita, quatro payloads, idempotência e preservação dos sentinelas de carteira/configuração/modelos/código de decisão. Validação de controle das cinco ações e sincronização descritiva do conhecimento preservadas.
- Cenários de demonstração são sintéticos; os testes não consultam mercado, movimentam recursos ou validam desempenho financeiro.

Aplicar `PORQUINHO_PORTLETS_DINAMICOS_V148.command --reiniciar`, depois Cmd+Shift+R. Mensagem final: `PATCH_PORTLETS_DINAMICOS_V148_OK`.
