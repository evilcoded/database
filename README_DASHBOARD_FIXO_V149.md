# V149 — composição fixa e curvas globais por moeda

Reestrutura a apresentação sobre V148, sem modificar decisões, limites, posições, saldos, modelos, coletores ou agendamento. O instalador contém quatro arquivos: novo JS/CSS, template e registro descritivo do Brain.

## Composição

Em desktop, onze portlets fixos em quatro linhas:

1. Patrimônio por moeda, Ganho/Perda, Meta e projeções, Alocação de ativos.
2. Evolução do patrimônio, Intraday de P/L, Risco × potencial.
3. Ativos com ações pendentes e **Proteção do capital**, conforme esclarecimento do usuário.
4. Dados e análise dos planos e Desempenho por ativo.

Todos têm a mesma altura em cada breakpoint: 270px em tela larga e 260px em telas menores. Larguras iguais dentro de cada linha; as linhas conservam suas quantidades diferentes de colunas. Tablet/celular reorganizam as colunas para legibilidade. Conteúdo excedente fica disponível no painel completo, acessível por clique no portlet, botão ou teclado. Previews limitam tabelas e listas sem remover os dados dos detalhes.

O arraste e a edição de tamanhos estão desativados. Preferências antigas do V148 são ignoradas, sem apagar dados do navegador. Alertas de mudança de avaliação continuam ativos.

## Global com curvas no mesmo gráfico

Patrimônio/minigráfico, evolução e intraday patrimonial passam a um gráfico por portlet, com BRL verde (`#19d49b`) e EUR azul (`#529bff`, tracejado para distinguir curvas coincidentes).

- Valores e horários são os registros originais. Não existe conversão, soma de moedas, reconstrução histórica ou cotação simulada.
- Cada moeda tem escala nativa independente, identificada na legenda e nos eixos. A altura das curvas não compara patrimônios entre moedas. Detalhes e tooltips preservam valores exatos e sua moeda.
- Populações/coberturas diferentes interrompem os segmentos, assim como lacunas intraday superiores a 30 minutos. Valores indisponíveis não viram zero.
- Filtros de conta, moeda, busca e janelas são preservados. Histórico global não é reutilizado como histórico de uma conta individual.
- EUR/BRL mantêm somente a moeda selecionada. Outras moedas, caso presentes, ficam identificadas nos detalhes quando o gráfico de duas escalas não puder apresentá-las.
- Cotações intraday de mercado continuam disponíveis separadamente no painel completo, em base 100 por ativo; não são confundidas com P/L.

Alocação possui um único portlet, com bases de cada moeda separadas, sem um percentual financeiro combinado obtido somando EUR e BRL. Desempenho por ativo reúne as posições em uma tabela com a moeda explícita por linha.

## Navegação e leitura

Menu superior no formato de seletor textual com lista vertical compacta, seguindo a organização da referência, mantendo ícones e paleta do Porquinho. Área de logo/menu mais estreita. Filtros da tela ficam aderentes ao topo da área rolável. Avisos de avaliação, módulo ativo e botão de ciclo manual são preservados.

## Verificação

- DOM completo: ordem 4/3/2/2, onze portlets, ausência de edição/arraste mesmo com preferências antigas salvas, curvas combinadas com cores e escalas, detalhe completo por moeda, filtros estritos, tabela global única e alertas preservados.
- Chromium real (1440×1100 e 390×844): alturas uniformes, filtros fixos durante rolagem, menu compacto, cliques/popup, filtro EUR, textos extensos sem overflow e nenhum erro JavaScript ou POST automático. Dados sintéticos; nenhum acesso financeiro real.
- Regressões das cinco sugestões V146, botões de moeda e proteção; dez testes do conhecimento descritivo.
- Instalação sintética: quatro payloads, dependências V146/V147/V148 verificadas, backup, recusa de divergência antes de escrita, idempotência e preservação dos sentinelas de carteira/configuração/modelos/código de decisão. Controle das cinco ações e sincronização descritiva continuam na instalação.

Aplicar `PORQUINHO_DASHBOARD_FIXO_V149.command --reiniciar`, seguido de Cmd+Shift+R. Mensagem final: `PATCH_DASHBOARD_FIXO_V149_OK`. Não é necessário restaurar manualmente o layout antigo ou aguardar um novo ciclo para a camada visual carregar; dados dos gráficos dependem dos registros já existentes.
