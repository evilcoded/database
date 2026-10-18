# A24 V39 — ajustes universais e preparação iPhone

Corrige apresentação, filtros e navegação sem modificar Brain, modelos, memória, aprendizado, snapshots, ledger, posições, metas ou autoridade financeira. Código do servidor e guards localhost preservados. O instalador inclui a criação/revalidação de diretórios corrigida na V38 R2.

## Interface

- Azul consistente em cartões administrativos, portlets, tabelas/cabeçalhos, campos nativos, selects personalizados e popups; cores dos dados e ações preservadas. Universo dos destaques mais compacto.
- Gráficos de linhas: tooltip pelos dados já presentes, ponto e guia vertical ao passar mouse/tocar; setas/Enter no foco do gráfico também percorrem pontos. Rosca/barras exibem valores existentes sem alterar geometria ou inventar amostras.
- Popups menores (até 820px), com quebra de textos/colunas para evitar scroll horizontal e botão Voltar além de fechar. Voltar restaura os nós DOM reais da janela anterior, incluindo campos e seletor de arquivo; não clona formulários financeiros. Fechar limpa a pilha, preservando os fluxos existentes de confirmação.
- Logos reais locais de BTC, ETH, SOL, BNB, USDC e HYPE. Nomes completos e IDs de apresentação também recebem o logo, corrigindo o caso em que somente uma sigla era reconhecida. Sem duplicar imagens. Mapeamento de nome é exclusivamente visual e nunca estabelece identidade, moeda, preço ou vínculo financeiro.
- Carteira: benchmark/performance e alocação lado a lado em 2/3 e 1/3; posições abaixo; adaptação vertical em celular.
- Ativos: filtro de moeda agora aplicado, por moeda declarada ou contexto de posição/pesquisa com instrument_id exato; filtro de conta exige contexto dessa conta. Sem associação por símbolo/país ou FX. Pesquisa inclui nome do catálogo.
- Contas e Bancos: nova visão imediata com contas/cash/posições dos fatos já carregados, filtros, detalhes e botões para os fluxos existentes de edição/vínculo/registro. Não aguarda o carregamento da gestão anterior de aproximadamente cinco segundos. Se ainda não há dados em cache, mostra carregamento explicitamente. Gestão completa e orçamento permanecem acessíveis em botão próprio; não remove controles ou transações existentes.
- Top Oportunidades: colunas compactas de ativo/moeda, avaliação/risco e leitura; detalhes completos em popup. Ordem e ações continuam vindo do motor existente. Nenhum ranking/ação/valor financeiro novo é fabricado.

Metadados administrativos explícitos de conta/instituição foram acrescentados à projeção já usada na UI para acionar os controles existentes; nenhuma posição/cash ou identidade é modificada.

## Logos e licenças

BTC/ETH/SOL/BNB/USDC: coleção cryptocurrency-icons de spothq, CC0 já incluída. HYPE: imagem de marca da coleção ErikThiart/cryptocurrency-icons, fonte e licença MIT incluídas em static/crypto-icons/HYPE_SOURCE.txt e HYPE_LICENSE.txt. Logotipos de terceiros não significam afiliação. Arquivos são locais, não uma consulta externa em cada tela.

## Acesso iPhone preparado, conexão real ainda depende dos aparelhos

Ao concluir o instalador, ele grava em Downloads **PORQUINHO_A24_PREPARAR_IPHONE_V39.command**. O assistente verifica HTTP local, porta SSH e IP Wi-Fi privado; gera e abre um guia HTML local com os parâmetros. Não instala cliente SSH, habilita Acesso Remoto, cria listeners, altera guards ou envia dados para terceiros. O guia contém IP/usuário locais e não deve ser publicado. Para atualizar IP/estado, execute novamente o assistente.

No Mac, Acesso Remoto precisa estar habilitado para o usuário autorizado. No iPhone, é necessário um cliente SSH com encaminhamento local: endereço local 127.0.0.1:8765 no iPhone -> destino 127.0.0.1:8765 no Mac pela conexão SSH autenticada. Safari usa http://127.0.0.1:8765/. Isso preserva Host/Origin locais e os tokens/fluxos existentes. Não usa reescrita de headers para contornar guard. Tailscale pode transportar SSH privado, mas um domínio Serve direto não satisfaz a política localhost das mutações.

Mac e iPhone devem conseguir se comunicar; o guia trata Wi-Fi de convidados/firewall, IP alterado e manutenção do cliente SSH em segundo plano. Não abrir porta de roteador. O assistente não verifica o iPhone real nem simula transações; é a mesma instalação/dados do Mac. Para encerrar, desconecte o túnel e desative Acesso Remoto se não precisar mais. A configuração/autenticação do cliente no iPhone é uma etapa local do usuário; nenhuma senha/chave deve ser enviada ao chat.

## Validação

1.113 testes Python e 209 verificações JavaScript nos ambientes pandas2/3;38 simulações do ativador. Chromium sintético desktop/mobile: filtro BRL/JPY, logos dos seis ativos carregados, sem duplicação, carteira 2:1, contas imediatas e gestão anterior acessível, oportunidades, mouse/crosshair/toque, rosca sem mudar raio, Voltar com input e nó original do seletor de arquivo preservados, textos longos sem scroll horizontal. Zero POST financeiro; fluxo explícito de planejamento anterior mantido. CLI do assistente também executada em ambiente de teste, sem conexão iPhone ou SSH certificadas.

Instalador validado em cópia: aplicação/repetição, divergência de baseline recusada, backup único, dados/CSV/config preservados e assistente copiado para Downloads. Ativação V39 somente do Porquinho, Bridge preservado; sem SIGKILL, segundo servidor ou refresh financeiro forçado. Se houver ciclo ocupado, repetir só o ativador indicado. Após ativar, Command+Shift+R.

Código/UI em fixture não equivale à validação real do Mac/iPhone. V39 depende da execução local; F3/F4 e certificação financeira continuam separados do trabalho de interface. Pacote público contém apenas fontes, logos licenciados e logs sintéticos, sem relatório/guia privado do usuário.

SHA-256 do instalador: `a2353df503fe4c630086873cbed9d035fd46d3d585981b4d3206f74150d4871b`.
