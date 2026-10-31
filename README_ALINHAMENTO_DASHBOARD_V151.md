# V151 — alinhamento dos cartões, filtros fixos e rolagem completa

Aplica sobre V150. Preserva onze portlets na distribuição 4/3/2/2, gráficos nativos, cores e regras de decisão.

- Filtros em faixa fixa fora da área rolável. Controles originais mantêm os eventos, foco, busca em digitação e filtros Global/EUR/BRL. Não se sobrepõem aos portlets.
- Substitui a altura calculada para o cabeçalho antigo por uma área flexível que ocupa o espaço restante. O último rodapé fica acessível em desktop e celular.
- Cartões de ações e proteção alinhados, com altura comum de 132px. Contadores de ações compactos abaixo dos cartões. A prévia prioriza ações existentes de compra, venda, realização e realocação; os detalhes preservam todas as posições, valores e ações originais.
- Três blocos dos planos com altura, tipografia e espaçamento consistentes. Detalhes continuam acessíveis nos popups.

Validação Chromium com dados sintéticos em 1440×1100 e 390×844: fim real da página alcançável, faixa fixa sem sobreposição, cartões alinhados, onze portlets e gráficos/períodos/popups preservados, sem erro JavaScript ou POST automático. DOM confirmou foco, busca em digitação, atualização direta, moeda e contadores. Regressões dos cinco tipos de sugestão, botões de moeda e dez testes do conhecimento passaram.

Instalador: quatro arquivos de apresentação/registro, backup, preflight antes de escrita, idempotência, preservação de código de decisão, ledger, configuração, modelos e memória. Mantém validação sintética dos cinco fluxos e sincroniza somente o registro descritivo do Brain. Não coleta mercado, treina ou executa operações financeiras.

Aplicar `PORQUINHO_ALINHAMENTO_DASHBOARD_V151.command --reiniciar`, depois Cmd+Shift+R. Mensagem final: `PATCH_ALINHAMENTO_DASHBOARD_V151_OK`.
