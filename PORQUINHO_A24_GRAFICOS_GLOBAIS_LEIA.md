# A24 — gráficos universais no cockpit

Acrescenta acompanhamento visual ao cockpit universal, Mercado e Carteira. Lê históricos de cotações existentes e fatos financeiros atuais; preserva o motor, dados, modelos, memória e aprendizado.

## Gráficos e interação

- Linhas diárias por fonte/instrumento/moeda, períodos de 30/90/365 dias, modos cotação nativa, base100 ou queda desde o pico observado no período. Cada moeda tem seu painel e eixos próprios. Legenda permite mostrar/ocultar séries e pontos identificam fonte, data e cotação. Tabelas acessíveis apresentam os dados usados.
- Barras de custo de aquisição por ativo/conta, cash por conta e resultado de referência somente nas posições onde há dados. Moedas nunca somadas ou convertidas. Ausências não viram zero.
- Rosca de composição por custos conhecidos de aquisição, com cobertura identificada e cash separado. Não é uma composição atual a valor de mercado.
- Velocímetros: confiança global e regime do motor já existentes, mais cobertura de cotação das posições filtradas. Confiança é índice de referência, não probabilidade de lucro. Índices globais não são apresentados como específicos da conta/moeda filtrada; ausência de métrica é explícita.
- Mapa de calor das variações das cotações em1/7/30 observações, sem confundir observações com dias corridos.
- Filtros de moeda, conta e ativo/fonte compartilhados com o cockpit; nomes de fonte e moedas explícitos. Nenhuma lista fixa de moedas. Rótulos de posições podem usar metadados de correspondências de pesquisa já revisadas somente para apresentação; identidades e avaliações financeiras não são reatribuídas.
- Resumo financeiro permanece acima dos gráficos. Outros gráficos com dados indisponíveis recebem mensagens compactas. Renderiza somente a tela ativa, mantém seções abertas e evita recriar gráficos nas telas escondidas. SVG responsivo, sem nova dependência de CDN ou biblioteca gráfica.

## Semântica dos dados

O histórico da fonte foi obtido no momento registrado: ele permite mostrar cotações passadas, não comprovar previsões passadas ou reconstruir patrimônio que o usuário possuía em cada data. Base100 é a evolução a partir da primeira observação do ativo no período; não é rentabilidade da carteira. Drawdown é queda desde o pico no período selecionado; não é perda máxima de toda a vida do ativo. Linhas conectam pontos disponíveis, não criam preços intermediários. Os gráficos são diários conforme a fonte; não habilitam alimentação intraday global.

Fontes são bundles existentes verificados, compatíveis com vínculos atuais e elegibilidade. Identidade/provedor/provider_id/moeda e rastreabilidade são preservados. Sem preenchimento retroativo, FX, inferência por símbolo ou sufixo _eur, coleta de novas cotações, treino ou operação financeira. Campo de preço de ativo admite precisão abaixo de centavos; formatação compacta no eixo não altera dados.

Os campos financeiros indisponíveis na versão anterior continuam indisponíveis sem correspondência financeira exata. Aliases revisados podem delimitar um gráfico de pesquisa e melhorar rótulos, mas não são usados para valorar posições ou fabricar resultado financeiro. Resultados de referência não são lucro realizado ou preços executáveis. Não altera dimensionamento, seleção de recomendação ou execução.

## Instalação e verificação

1.079 testes Python e 154 verificações JavaScript (122 anteriores+32 do cockpit e gráficos), nos ambientes pandas 2 e 3. Mais 38 testes simulados do ativador, preservando relatórios sem preços/valores privados. Chromium com fixture sintética em desktop/mobile: SVGs, períodos, modos, legenda, filtros, navegação, estado de evidência, um GET compartilhado, zero POST e ausência de erros/overflow horizontal. Browser de fixture isolada não equivale à validação da aplicação real no Mac.

Instalador testado em cópia temporária: divergência de baseline recusada, aplicação/repetição idempotentes, regressões completas, backup único e dados/CSV/config preservados. Ativação V34 controlada, Bridge preservado e sem SIGKILL, servidor duplicado, refresh manual ou requisição financeira. Se o ciclo estiver ocupado, repetir somente o ativador indicado. Depois recarregar com Command+Shift+R. Novos arquivos estáticos usam cache versionado V34.

Relatório de ativação exporta contagens/estado dos gráficos, não as séries ou valores financeiros. O relatório anterior V33 confirmou endpoint e UI, mas ainda não tinha confirmado um novo snapshot na janela de espera; a validação mantém essa distinção e não fabrica sucesso de ciclo. Aplicação e gráficos reais V34 pendentes da execução local.

Preserva F3/F4 em consolidação; este patch entrega acompanhamento visual, não encerra decisão econômica, sizing ou negociação automática. O pacote público contém somente código/fixtures/logs sintéticos.

SHA-256: `a587549137cb8d233ad387aaa666ca3244e8f7bd31ae2c2a45d390ab18538d98`.
