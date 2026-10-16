# A24 — Preservar seções expansíveis do Mercado

O redesenho periódico do Mercado recriava o painel Acompanhamento global, removendo o estado aberto dos elementos details. A seção de avaliação fechava durante a leitura.

A correção registra o estado atual antes de executar o renderizador anterior e antes de substituir o painel; restaura esse estado por chave estável e escopo da tela após a montagem. Preserva tanto a abertura quanto o fechamento manual da avaliação e das pendências econômicas. Ausência temporária do painel não apaga o estado. Não depende do número de contextos nem do texto do título. Estado mantido apenas em memória durante a sessão da página, sem gravar histórico ou preferências persistentes.

Mantém as atualizações, leituras e cadências existentes. Não altera fonte, cálculo, modelo, previsão, aprendizagem, snapshot, decisão, autorização, rede ou operação financeira. Não modifica backend. Instalar e recarregar Mercado no navegador; nenhum serviço precisa ser reiniciado.

Instalador com baseline e SHA, backup do código e regressões em cópia temporária. Validado com 757 testes Python e 79 verificações JavaScript nos ambientes pandas 2/3, sem skips. Casos específicos: abertura restaurada, fechamento manual respeitado, ausência temporária sem perda de estado e captura antes da substituição pelo renderizador existente. Instalador aplicado duas vezes, divergência recusada e dados/CSV/configuração preservados. Verificações locais não equivalem a interação com o navegador remoto.
