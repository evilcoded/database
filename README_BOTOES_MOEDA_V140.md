# V140 — Botões no filtro Moeda

Substitui o menu do filtro Moeda por três botões no mesmo campo: 🌐 Global, 🇪🇺 EUR e 🇧🇷 BRL. Mantém o rótulo Moeda, a largura flexível existente e a altura do controle (33px nas telas compactas, 42px no estilo base). O estado ativo aparece destacado e é exposto por `aria-pressed`. Os botões nativos também permitem uso pelo teclado.

Reutiliza o estado e a persistência existentes. Trocar de moeda limpa a conta anterior, como o menu fazia; clicar na moeda já ativa preserva a conta. O texto de pesquisa é preservado. Global corresponde ao filtro vazio e mantém as moedas separadas, sem conversão. Valores antigos de filtro fora de EUR/BRL passam para Global. Conta e pesquisa continuam nos controles anteriores.

Aplica-se às telas que compartilham esse filtro. Altera somente `static/universal_cockpit_a24.js`, `static/universal_cockpit_a24.css` e as versões de cache desses dois recursos em `templates/index.html`. Não altera serviços, aquisição, modelos, decisões ou dados financeiros.

Aplicar `PORQUINHO_BOTOES_MOEDA_V140.command` e fazer uma atualização completa do navegador (Cmd+Shift+R no Mac). Não é necessário usar a opção de reinício para esta entrega estática; o refresh completo carrega os arquivos atualizados e a seleção salva. O instalador padrão não reinicia serviços.

Verificações: sintaxe JavaScript e shell; teste DOM com os scripts da página cobrindo três botões, clique nos ícones, destaque, foco, filtro de conta, Global, limpeza, persistência após nova carga e ausência de chamadas de API ao mudar a moeda. Regressões de filtros globais de oportunidades e publicação operacional também passaram. Instalador testado para três arquivos, reaplicação idempotente, recusa de divergência antes de escrever e preservação de sentinelas financeiros/modelos. A revisão visual no Mac do usuário continua necessária; a tentativa de renderização Chromium no ambiente de desenvolvimento não ficou disponível.
