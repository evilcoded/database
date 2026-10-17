# A24 V35 — Dashboard e interface universal

Primeira versão da reorganização visual, seguindo a identidade verde do Porquinho. Camada de apresentação e leitura dos registros existentes. Nenhum arquivo do Brain, modelo, memória ou aprendizado é alterado pelo patch.

- Dashboard: resumo por moeda, histórico diário, intraday disponível, sinais atuais de ação do Brain, ativos, composição, velocímetros e variações. O portlet de ações lê os sinais existentes; não exige maturação canônica para mostrar uma leitura atual nem cria ordens. Sem moeda declarada, o sinal fica explicitamente como referência sem contexto financeiro confirmado.
- Carteira: posições e resultados, tabela compacta com linhas clicáveis para quantidade, custo e detalhes completos. Não reconstrói patrimônio passado a partir de posições atuais.
- Mercado global: cotações, variações e fontes por instrumento/moeda. Cockpit do Brain: saúde do acompanhamento, cobertura e evidências. Oportunidades: realocações e suas pendências. Ativos: catálogo universal em cards e detalhes por instrumento.
- Popups substituem expansão nos novos painéis, fontes, evidências e oportunidades. Formulários e controles anteriores são preservados como os mesmos nós do DOM; operações manuais continuam nas funções existentes. Não reimplementa revisão, confirmação ou registro de transações.
- Menus Porquinho IA e Importação Financeira removidos; chat migrado preservado. Importação continua acessível por sua rota administrativa, em popup, com o formulário original.
- Gráficos menores, sem nova biblioteca externa. Um conjunto diário/intraday acompanha a moeda selecionada; filtros existentes de conta e pesquisa preservados. Valores de moedas distintas não são somados nem convertidos.

## Limites reais dos dados

Intraday recuperado do CSV existente: o produtor legado reamostra a cada 10 minutos e pode interpolar na coleta original. O leitor não cria nova interpolação, coleta ou falsa cadência de um minuto. Compatibilidade atual do produtor com EUR é mostrada como referência legada separada; não atesta moeda histórica por linha nem vincula a cotação à posição financeira. Linhas globais explícitas aceitam qualquer moeda declarada com identidade/provedor/provider_id. Fontes e horários disponíveis aparecem em popup.

Realocação permanece uma comparação bruta quando custos e dimensionamento estão pendentes. A interface diz claramente que ainda não há recomendação final e que o valor a mover não foi definido pelo Brain. Capital de comparação não vira valor de ordem. Este patch não fabrica decisão, preço, dimensionamento ou rentabilidade.

Patrimônio/resultado de referência só são calculados com fatos válidos e cotações de identidade/moeda exatas. Dados indisponíveis permanecem indisponíveis. Nenhuma inferência financeira por ticker, alias de pesquisa, país do banco ou sufixo _eur. Rótulos de metadados não alteram identidades. Custo de composição não é valor de mercado.

## Validação e instalação

1.091 testes Python e 171 verificações JavaScript nos ambientes pandas 2 e 3; 38 testes simulados do ativador. Chromium com fixture sintética: desktop/mobile, gráficos diário/intraday, moeda, ações, separação de páginas, popups, preservação do input original de importação, um GET compartilhado, zero POST, sem erros JavaScript ou overflow horizontal. Fixture isolada não comprova o runtime real do Mac.

Instalador valida em cópia temporária antes de aplicar. Baseline divergente recusado, aplicação/repetição testadas, backup único e sentinelas de dados, CSV e configuração preservadas. Código público contém apenas fontes e fixtures sintéticas. Sem treino, refresh forçado, coleta, alteração de snapshots/histórico ou operação financeira.

Ativação V35 controlada somente do Porquinho, preservando Bridge. Sem SIGKILL ou segundo servidor. Se houver ciclo ativo, repetir somente o ativador indicado em Downloads. Após a ativação, recarregar com Command+Shift+R. Relatório exporta estado/contagens, não séries de preços ou valores financeiros. Aplicação real desta versão ainda depende da execução local.

F3/F4 continuam em consolidação: a reorganização da UI não certifica modelos, dimensionamento ou execução automática.

SHA-256 do instalador: `f3353aa0aaaefa3bb2985a8657c36ea0456a5fe6b31bc162f558163c112ea1cf`.
