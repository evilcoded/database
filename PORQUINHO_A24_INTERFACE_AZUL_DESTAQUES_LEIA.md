# A24 V38 — portlets azuis, ícones e destaques

Camada de apresentação sobre os painéis existentes. Preserva Brain, modelos, memória, aprendizado, dados, metas, transações e histórico.

- Fundo dos portlets em azul profundo (#031d2b e gradientes próximos da referência), mantendo identidade verde e cores das ações. Estilo compartilhado nas páginas e cartões existentes, inclusive formulários/modais, sem modificar sua lógica.
- Pequenos ícones vetoriais antes dos títulos dos painéis. Logos locais para BTC, ETH, SOL, BNB e USDC, com fallback para símbolos ainda sem arquivo. Ícones servem somente à apresentação; não vinculam preços ou posições.
- Meta do Porquinho em grade como a referência: ícone/alvo, frase, moeda; meta alvo, progresso e retorno objetivo; prazo e estratégia. Meta alvo = capital de referência + ganho objetivo registrado. O objetivo permanece rascunho; não inventa progresso, prazo de início/fim ou promessa de retorno. Progresso sem reconciliação aparece assim identificado, sem barra de zero por cento fabricada.
- Linha central: Evolução do Patrimônio menor, Insights ao centro e ações pendentes à direita. Linha inferior: alocação ocupa 1/3, desempenho por ativo 2/3. Rosca e legenda crescem dentro da alocação; layout se adapta em tablet e celular.
- Topo da Visão geral: até quatro cripto e quatro ações por avaliação existente, separados por pipe; pesquisa reduzida; estado/data/hora e botão original de solicitar ciclo preservado ao final. Chat, histórico e controles continuam disponíveis em suas rotas/telas, sem duplicação de ciclo.
- Destaques respondem à moeda e conta selecionadas; o seletor Universo dos destaques controla Todos/Cripto/Ações somente no topo. Não altera o universo de pesquisa do Brain ou recalcula indicadores financeiros. Ordena avaliações já existentes (promising_pct), sem produzir recomendação/ordem ou usar retorno de pesquisa para substituir score ausente.
- Classe e moeda precisam estar explícitas ou vir de metadados de identidade exata. Compatibilidade do produtor legado EUR só é mostrada como referência, quando existe seu contrato explícito; não aparece como BRL/USD. Nome/ticker não estabelece classe, moeda ou identidade financeira. Cotações _eur não são relabeladas para outra moeda. Ausências de leituras ficam nos respectivos espaços, sem preencher quatro ações ou cripto fictícios. O adaptador brasileiro anterior pode ter observações sem score; elas não são inventadas como recomendações.

## Ícones

Arquivos locais de cryptocurrency-icons, https://github.com/spothq/cryptocurrency-icons, licença CC0 incluída em static/crypto-icons/LICENSE.md. Cores/logos são os arquivos do projeto, não imagens geradas. Sem consulta externa de ícone no navegador. Vínculos financeiros não são derivados de ícones ou símbolos.

## iPhone e instalação local

É possível usar o Safari real no iPhone; isso permite testar o layout e interações no aparelho, além da emulação desktop já verificada. O servidor atual está em 127.0.0.1:8765, portanto o IP Wi-Fi do Mac não o torna acessível diretamente. Este patch não abre listener ou porta de rede.

Uma rede privada/Tailscale Serve pode dar acesso à visualização, mas operações protegidas validam Host/Origin como localhost. Elas podem recusar um domínio de rede privada, e essas validações são preservadas. Para testar também essas funções sem afrouxar a política, uma opção é um cliente SSH no iPhone com encaminhamento local: porta local 127.0.0.1:8765 no iPhone -> 127.0.0.1:8765 no Mac por SSH autenticado; Safari abre http://127.0.0.1:8765. Isso requer SSH no Mac e um cliente iOS com túnel local mantido ativo; a continuidade em segundo plano precisa ser verificada no aparelho. Nenhuma ferramenta ou serviço de acesso remoto foi instalado/configurado pelo patch. Alternativamente, um ambiente separado de testes pode ter uma política de acesso própria. A versão iOS real ainda não foi testada.

## Verificação

1.107 testes Python +197 verificações JavaScript em pandas2/3;38 simulações do ativador. Chromium sintético desktop/mobile: oito destaques, pipe, filtro de universo, logos locais, relógio, botão preservado, fundo azul, proporções da grade, meta, popups e rotas; fluxo explícito de meta semanal mantido. Zero POST financeiro; duas chamadas simuladas de planejamento existentes. Sem erro JavaScript ou overflow horizontal. Fixtures não equivalem à aplicação real no Mac/iPhone.

Instalador validado em cópia: baseline divergente recusado, instalação/repetição, regressões completas, backup único e sentinelas de dados/CSV/config intactas. Não altera código do Brain nem sua segurança/autoridade. Ativação V38 controlada somente do Porquinho, Bridge preservado, sem SIGKILL/segundo servidor/refresh forçado. Ciclo ocupado: repetir só o ativador indicado; depois Command+Shift+R.

Ativação anterior confirmada pelo relatório local. V38 aguarda instalação/ativação e conferência visual local. F3/F4 e certificação financeira permanecem separados desta alteração de UI. Pacote público contém somente fontes, ícones licenciados, fixtures e logs sintéticos.

SHA-256: `ff92bbf8cb6b9ca0d47cd97cbbce7a8d836b398bd90bed2df125e263cf1c79bd`.
