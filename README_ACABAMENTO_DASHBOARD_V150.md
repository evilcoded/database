# V150 — acabamento visual e correção do cabeçalho

Refina a página sobre V149 preservando a paleta, os onze portlets na distribuição 4/3/2/2, alturas, gráficos, cores BRL/EUR, dados e regras de decisão.

## Ajustes

- Corrige a altura real herdada do cabeçalho: de 72px para 54px em desktop, com logo aumentado de 28px para 38px. Em telas estreitas, a altura se adapta para evitar sobreposição.
- Reduz status “Sistema operacional”, data/hora e botão “Gerar ciclo” para 10px; melhora alinhamento e espaçamento dos controles.
- Devolve os botões originais de Chat e Histórico ao cabeçalho, preservando seus nós e funções. Não duplica atalhos a cada atualização. O módulo de relatórios continua acessível no menu com o nome “Relatórios”; Histórico é o atalho existente de histórico/importação.
- Retira o comportamento sticky dos filtros. Eles acompanham a rolagem normal, sem flutuar sobre os portlets.
- Acabamento discreto de bordas, profundidade, peso tipográfico, campos, foco e links de detalhes; preserva o esquema de cores e a disposição aprovada. Valores mantêm os números, unidades e escalas originais.

## Verificação

DOM completo confirmou os mesmos botões antes/depois da movimentação, ausência de duplicação, rota de relatórios preservada, onze portlets 4/3/2/2 e cores nativas intactas. Regressões dos gráficos fixos, sugestões V146, moedas, proteção e dez testes do conhecimento passaram.

Chromium com dados sintéticos (1440×1100 e 390×844): altura 54px e logo 38px em desktop, fonte 10px do ciclo, filtros deslocando-se exatamente com a rolagem, ausência de overflow horizontal, gráficos/popups/períodos preservados e cliques únicos em Chat/Histórico. Nenhum erro JavaScript ou POST automático. Não houve coleta, importação ou execução financeira real.

Instalação sintética confirmou quatro payloads, backup, recusa de divergências antes de escrita, idempotência e preservação de código de decisão e sentinelas de ledger, configuração, modelos e memória. O instalador mantém a validação sintética dos cinco fluxos e sincroniza somente o conhecimento descritivo do Brain.

Aplicar `PORQUINHO_ACABAMENTO_DASHBOARD_V150.command --reiniciar`, depois Cmd+Shift+R. Mensagem final: `PATCH_ACABAMENTO_DASHBOARD_V150_OK`.
