# A24 V36 — Visão geral compacta

Aproxima a composição da interface original: indicadores, dois gráficos lado a lado e grade de quadros compactos. Mantém a identidade verde existente, com dados reais disponíveis em cada moeda. Brain, modelos, memória, aprendizado e histórico não são modificados.

## Organização

- Visão geral: indicadores financeiros da moeda/conta selecionada; diário e intraday lado a lado; ações pendentes do Brain; principais ativos com minigráficos diários da própria série/fonte; cash por conta; composição por custos registrados; estado do acompanhamento; oportunidades de realocação; velocímetros e quadro de variações.
- Carteira continua focada em posições e resultados, Mercado em cotações/fontes, Cockpit em estado/evidências do Brain, Ativos em catálogo e Oportunidades em comparações. Reduz espaçamento/tipografia dos painéis universais e melhora uso do espaço do menu lateral no desktop.
- Gráficos da Visão geral menores, mantendo seletores de período, medida e moeda. Layout adapta para tablet/celular. Detalhes, fontes e notas explicativas abrem em popup, sem menus expansíveis.
- Novos quadros são projeções dos dados já carregados. Sem novo endpoint, polling, coleta ou requisição financeira. Botões levam às funções/páginas existentes. Formulários originais e transações manuais permanecem preservados.

## Dados e limites

Não copia números ilustrativos, metas, notícias, maturações ou estados de prontidão da imagem. Campos indisponíveis não viram zero. Patrimônio e resultado exigem cotação com identidade/moeda financeira exata; não atribui preços por ticker ou alias de pesquisa. Cash registrado não é saldo automaticamente disponível para uma ordem. Composição é por custo de aquisição conhecido, sem FX ou soma de moedas distintas.

Sinais COMPRE/VENDA e demais ações elegíveis continuam vindo das leituras atuais do Brain, sem exigir o fim de ciclos 30/60/90. Uma indicação sem contexto monetário confirmado é identificada como referência. O patch não cria sinais, modelos, dimensionamento ou ordens.

Realocação bruta sem custos/dimensionamento mostra que o valor a mover não foi definido. Capital comparado não é instrução de negociação. Intraday existente mantém seus horários e a cadência legada de 10 minutos, detalhada no popup; não inventa observações de um minuto nem reatribui histórico EUR a posições financeiras. Linhas globais explícitas continuam aceitando moedas declaradas universalmente.

## Validação

1.091 testes Python e 175 verificações JavaScript nos ambientes pandas 2 e 3; 38 simulações do ativador. Chromium com fixture sintética desktop/mobile: gráficos lado a lado abaixo de 310px por painel, seis quadros compactos, minigráficos, popup de notas, filtros, rotas, popups de posições/ativos/fontes, input original de importação preservado, um GET compartilhado, zero POST, sem erro JavaScript ou overflow horizontal. Fixture isolada não equivale à aplicação real do Mac.

Instalador testado em cópia temporária: baseline divergente recusado, aplicação e repetição com regressões, backup único e dados/CSV/config preservados. Nenhuma alteração no código do Brain ou em seus registros. Ativador V36 verifica hashes, preserva Bridge e recusa reiniciar durante ciclo ativo; sem SIGKILL, segundo servidor ou refresh manual. Relatório exporta contagens/estado, sem séries de preço ou valores financeiros.

A ativação V35 foi confirmada pelo relatório local enviado. V36 aguarda aplicação/ativação local e conferência visual. Depois de ativar, usar Command+Shift+R. Se o ciclo estiver ocupado, repetir somente o ativador indicado na saída. F3/F4 permanecem em consolidação; reorganização visual não certifica decisões ou execução automática.

SHA-256 do instalador: `0e57bb1e1ac88c5a234684066d3eb19ce64966f40238e9d58898aae695e214d8`.
