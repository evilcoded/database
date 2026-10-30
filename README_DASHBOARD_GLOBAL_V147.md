# V147 — dashboard de decisão global e navegação superior

Entrega visual sobre a consolidação V146. O instalador altera quatro arquivos: a nova camada JavaScript, seu CSS, o template que os carrega e o descritor de arquitetura do Brain. Não modifica fórmulas, regras, decisões, coletores, agendamento, saldos, posições ou modelos.

## Navegação e organização

- Ícone do Porquinho e seletor de módulos no topo, reutilizando os botões e rotas da navegação existente. A lista abre por clique ou teclado; fecha ao selecionar, sair ou pressionar Escape. O módulo escolhido fica preservado na sessão após recarregar.
- À direita: status existente, data/hora local e botão explícito “Gerar ciclo”, conectado à mesma função `/api/refresh` já existente. O relógio não chama APIs nem inicia ciclos.
- Abaixo: barra dos ativos mais bem classificados e seletor Cripto/Ações; depois os filtros da tela e o conteúdo. Retira a faixa “Porquinho · Universo Global” e os títulos repetidos da área principal. Ferramentas existentes como Chat, Histórico e Patch Center continuam acessíveis no menu.
- A mensagem de acompanhamento e o snapshot aparecem em Ganho/Perda, substituindo a barra extensa no dashboard.

## Moedas, gráficos e ranking

- Global mostra os portlets e gráficos separados por moeda: patrimônio, minigráficos, P/L, evolução patrimonial, intraday, alocação e desempenho. Não soma EUR com BRL, converte preços ou fabrica histórico.
- Usa os renderizadores e registros existentes. Preserva segmentação por cobertura/população, filtros de conta, janelas temporais, períodos e modos de intraday. Sem série compatível, apresenta ausência em vez de reutilizar outra conta/moeda.
- Fontes e tabelas dos gráficos possuem chaves distintas por moeda; os gradientes SVG também. Vale para intraday patrimonial e cotações de mercado.
- Destaques passam a usar leituras operacionais atuais do fluxo global, em vez de depender do portfólio legado EUR. Ordenação pelo índice existente, até quatro cripto e quatro ações; não há novo modelo de ranking ou promoção de recomendação.
- EUR exibe somente EUR; BRL somente BRL; Global reúne as melhores avaliações disponíveis de ambos, sempre identificadas. Conta e busca também são respeitadas. Não força cotas por moeda quando os índices mais altos pertencem à outra moeda. Na ausência de ações atualmente avaliadas em EUR, informa essa ausência, conforme a preferência expressa pelo usuário.
- Ativos repetidos entre contas são deduplicados por identidade/fonte/moeda; divergências de índices recusam o destaque. Os detalhes mostram os critérios das contas correspondentes, sem escolher uma ação arbitrária entre uma posição já detida e outra conta sem posição.

## Decisão e informação compacta

- Resumo com patrimônio e minigráfico por moeda, Ganho/Perda e meta/projeção. Diferencia meta semanal definida, projeção de pesquisa e objetivo ainda pendente; não fabrica progresso.
- Evolução e intraday recebem mais espaço. Ações pendentes continuam explícitas em pequenos blocos clicáveis, preservando COMPRA/VENDA/MANTENHA/REALIZAR/REALOCAR e ACOMPANHE.
- Proteção do capital destaca perdas desde a compra, por conta e moeda, com detalhes do alerta existente. Não cria stop-loss ou venda forçada.
- Novo gráfico “Risco × potencial” usa os índices descritivos existentes. Pontos próximos são agrupados visualmente e abrem todas as avaliações correspondentes. A posição do grupo usa uma avaliação real, sem modificar valores. A zona sombreada usa apenas dois limites configurados; os detalhes explicam que COMPRA também exige entrada/contexto/dimensionamento.
- “Dados e análises dos planos” vira um conjunto de caixas informativas clicáveis para planos, entradas pendentes e acompanhamento global. Os horizontes prospectivos continuam separados de modelo validado/ativado.

## Validação

- 185 testes Python de regressão do fluxo V146 passaram, incluindo decisões, valores/frações, captura, horizontes, fontes e conhecimento. A seleção mantém a exclusão já documentada do teste AST obsoleto `test_actual_normal_cycle_hook_uses_funded_research_context`.
- Teste DOM com scripts locais completos: dois gráficos por moeda no Global, dois minigráficos, tabelas e popups separados, modo intraday de cotações, filtros EUR/BRL/conta/busca, ausência de ações EUR sem fallback BRL, ranking, pontos agrupados, teclado e preservação dos dados de origem.
- Regressões DOM de sugestões V146, critérios V145, proteção e botões de moeda passaram.
- Chromium real em 1440×1100 e 390×844: sem rolagem horizontal e sem erros JavaScript. Foram exercitados gráficos e detalhes, navegação real, restauração de módulo após reload, filtros e teclado. Nenhum POST automático; o clique explícito no botão manual chamou o endpoint original em simulação, sem servidor financeiro real.
- Instalação sintética verificou quatro payloads, dependências V146, backup, recusa de divergência antes de escrita, idempotência e preservação de sentinelas de ledger/configuração/modelos/memória e código de decisão. Instalação também repete a validação de controle dos cinco fluxos e sincroniza o conhecimento descritivo.

Os dados de demonstração dos testes são inteiramente sintéticos. A existência de um gráfico depende dos registros que já estejam armazenados; este patch não preenche o passado com as posições atuais nem faz coleta de mercado. Testes visuais não atestam rentabilidade ou validade estatística dos índices.

## Aplicação

Executar `PORQUINHO_DASHBOARD_GLOBAL_V147.command --reiniciar` sobre V146. O reinício usa a proteção existente contra ciclo em andamento. Depois, Cmd+Shift+R.

Mensagens esperadas: `CINCO_FLUXOS_VALIDADOS`, `CONHECIMENTO_DESCRITIVO_ATUALIZADO; DIVERGENCIAS=0` e `PATCH_DASHBOARD_GLOBAL_V147_OK`.
