# V130 — Abertura da revisão com retorno imediato

O botão iniciava a consulta antes de mudar a tela. Enquanto a resposta pendia, a interface permanecia igual e parecia não responder. A consulta de casos também passava pelo monitor completo, incluindo resumos que não são necessários ao formulário.

O V130 abre imediatamente a tela de carregamento. Depois substitui seu conteúdo pelo formulário existente, sem adicionar uma etapa extra ao histórico de Voltar. A consulta de abertura tem limite de espera de 45 segundos e erro visível. Uma resposta atrasada não reabre o formulário após Voltar ou fechar a tela. A gravação também informa imediatamente seu andamento.

O servidor passa a consultar somente a ponte verificada e os contratos existentes de visibilidade, transporte, avaliação, disponibilidade manual e custos. Não chama o monitor completo para abrir ou salvar a revisão. A validade da declaração é conferida novamente depois de obter o contexto, antes de gravar. Não se elimina a validação de conta, moeda, cenário, valor, rota ou fontes.

Não altera aprendizado, regras de compra/venda, modelos, orçamento, saldos, ledger, estimadores de custos ou requisitos para recomendações. Este patch corrige o acesso ao fluxo; não libera recomendações ainda bloqueadas.

## Validação

- Reprodução do problema com a versão anterior: clique real em um DOM com os scripts locais completos, os diálogos existentes e a resposta HTTP pendente deixava a tela anterior visível.
- Teste de regressão com jsdom: carregamento imediato, formulário, envio com sessão local, zero explícito, desconhecidos, Voltar, resposta atrasada e tempo excedido.
- Comparação dos casos e valores com a projeção existente; manutenção do bloqueio de uma rota declarada indisponível; leitura sem escritas.
- 38 testes Python do contexto e fluxo de custos, além do teste DOM e regressões do painel de custos.
- Instalador verificado para repetição, divergências e preservação de modelos/ledger com sentinelas sintéticas.

O teste DOM é de desenvolvimento, não uma dependência do Porquinho instalado. Pode ser executado com Node e `jsdom@26` disponível no caminho de módulos. Não equivale a inspeção visual no Mac do usuário.

## Aplicação

Aplicar com `--reiniciar`, atualizar a página e clicar em **Custos revisados por cenário → Revisar custos**. Deve aparecer **Carregando a revisão deste cenário…** imediatamente, seguido pelo formulário ou uma mensagem de erro. Abrir essa tela não registra evidência nem compra.
