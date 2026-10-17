# A24 — cockpit universal e consolidação da experiência

Primeira entrega do cockpit global, dentro da consolidação F3/F4. Organiza as saídas já existentes e os registros financeiros por instrumento, conta e moeda. Não conclui dimensionamento, decisão econômica final ou negociação automática.

## Experiência

- Cockpit: cash e custo de aquisição por moeda, posições canônicas, quantidade, valor e resultado de referência quando existe cotação explícita, leitura disponível por contexto e candidatos de realocação. Sem FX, soma entre moedas ou associação financeira por símbolo.
- Mercado global: contextos de qualquer instrumento/moeda que já tenham fontes vinculadas. Cotação e data por identidade/provedor/provider_id/moeda exatos. Fonte ausente, desatualizada ou histórico insuficiente permanecem explícitos.
- Carteira: mesma base universal de posições/cash; controles e leitura anteriores preservados em seção própria. Transações continuam acessíveis pelo mecanismo já existente; nenhum formulário de compra/venda, ledger ou autorização foi reimplementado.
- Oportunidades: comparação de realocação por origem, conta e moeda. Candidatos brutos aparecem primeiro em cartões, com nomes de conta/banco do registro. Outras comparações agrupadas por origem; tabelas dos modelos, IDs e pendências disponíveis sob demanda.
- Filtros compartilhados de moeda, conta e ativo/fonte. Nenhuma lista fixa BRL/EUR/USD e nenhuma moeda inferida pelo país do banco. A pesquisa por conta contempla posições e demandas de acompanhamento explícitas, incluindo instrumentos ainda não detidos.
- Brasil: removido o item duplicado no menu; acervo regional e controles mantidos dentro de Mercado global. Dados de renda fixa, B3 e ativos brasileiros não foram apagados nem reatribuídos.
- Análises/Analytics: acesso a modelos e resultados históricos concentrado em Aprendizado; rotas e funcionalidades preservadas. Menu Notícias retirado por ser uma entrada sem feed conectado. Áreas administrativas de Contas e Bancos, Ativos, Transações, Importação, Histórico, Sistema e Configurações mantidas.
- Regras de layout escopadas; evidências e seções abertas preservadas durante atualizações. Navegação volta ao topo do conteúdo; layout adaptado a desktop e celular.

## Leituras, dinheiro e histórico

O cockpit só associa uma leitura a uma posição quando instrumento, conta e moeda correspondem exatamente. Os sinais já existentes sem esse contexto continuam acessíveis em Leituras atuais de referência, com escopo e data próprios. Não reutiliza uma leitura em EUR como decisão em BRL e não exige maturação canônica para mostrar uma leitura existente.

Cotação de pesquisa não é preço executável. Valor e resultado de referência são separados de lucro realizado e não entram num patrimônio global convertido. Campo desconhecido continua indisponível. Capital de comparação de realocação não é valor proposto para negociar; intervalos dos estimadores não são probabilidades de acerto ou votos independentes. Custo de aquisição e cash são fatos distintos de valor de mercado.

O endpoint de acompanhamento da interface inclui a projeção financeira apenas quando explicitamente solicitada pelo handler local. Inspeção/relatórios de diagnóstico mantêm o padrão sem valores financeiros; o ativador exporta apenas contagens e moedas. Nenhum dado local, saldo ou posição real foi incluído neste pacote público. Nomes pessoais fixos do template foram substituídos por texto neutro; o cadastro de contas não muda.

Sem alterações em modelos, memória, aprendizado, snapshots, CSV, episódios, transações, posições, cash ou journals. Sem treino, coleta, refresh manual, operação financeira, novo timer ou nova chamada de polling. Reutiliza o GET de acompanhamento e sua cadência. Não transforma candidatos de pesquisa em ordens.

## Validação e instalação

1.067 testes Python; 137 verificações JavaScript (122 existentes +15 da experiência universal), em pandas 2 e 3. Mais 38 testes simulados do ativador V33, incluindo relatório sem valores financeiros. Teste Chromium com DOM e navegação em desktop/celular, filtros, evidências inicialmente recolhidas, estado preservado em atualização, seção regional integrada, controles anteriores presentes, um GET compartilhado, zero POST, ausência de erros e de overflow horizontal móvel. Browser usa fixture sintética e fundação de interface isolada; não certifica preços, decisão ou execução no Mac. Instalação/repetição em cópia temporária com regressões completas, baseline divergente recusado, backup único e dados/CSV/config preservados.

O instalador cria backup e tenta ativação controlada V33. Bridge preservado; ciclo ocupado adia ativação; sem SIGKILL, segundo servidor ou requisição financeira. Depois usar Command+Shift+R no navegador. Arquivo local de ativação tem resumo de contas/posições/moedas e comparador, sem valores privados. Validação real do navegador e de todos os fluxos administrativos continua necessária após aplicação no Mac. A entrega não declara F3/F4 encerradas.

SHA-256: `c000eba64636156ea93decbef58602ecc434bde309e864aad28a261b6b31a6a5`.
