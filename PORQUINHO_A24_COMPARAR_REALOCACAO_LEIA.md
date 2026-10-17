# A24 — comparação de realocação entre ativos

Fecha a lacuna entre enumerar REALLOCATE e comparar manter a origem versus trocar pelo destino. Usa posições e alternativas existentes e previsões já produzidas pelo laboratório global com os estimadores do Brain. Não aguarda novos ciclos canônicos para exibir a análise e não modifica o aprendizado existente.

## Comportamento

Mercado e Carteira recebem a seção **Realocação entre ativos**, com origem → destino, conta e moeda. Cada par compara somente previsões da mesma moeda, origem temporal e horizonte de 30 observações; preserva a distinção dos ciclos de 30/60/90 dias. Exibe todos os estimadores disponíveis, sem escolher um campeão, contar modelos como votos independentes ou ocultar discordâncias.

Mostra retorno projetado de manter a origem e do destino, diferença bruta em pontos percentuais, risco histórico pareado e, quando existe avaliação exata, diferença monetária no capital comparado. O risco é a raiz da média dos retornos negativos ao quadrado, usando apenas as mesmas janelas maturadas nos dois ativos. Não é risco futuro certificado, e as janelas podem se sobrepor.

Estados: vantagem bruta sem maior downside histórico nos modelos disponíveis; sem vantagem bruta; divergência/maior risco histórico; ou falta de previsões comparáveis. A seção explica por par o que falta. Esse é um comparador real de previsões existentes, não a simples contagem de possibilidades do patch anterior.

O capital da posição inteira serve somente para um cenário comparável. Não é quantidade recomendada para vender nem tamanho de ordem. Correspondência de pesquisa revisada pode ligar análises, mas não autoriza valorar uma posição financeira ou gerar uma ordem a partir de um alias. Conta, moeda e identidade financeira nunca são inferidas por ticker, país ou sufixo _eur. Metadados do catálogo são usados somente para os rótulos.

## Custos e limite da entrega

Evidências futuras de custo já revisadas podem formar cenários explícitos SELL + BUY por conta, instrumento, moeda, prazo de validade e notional exatos. O valor destinado à compra mais sua taxa deve ser exatamente o que resta depois da venda e de sua taxa. Não escala tarifas de outra transação, não usa taxas históricas como tarifas futuras e não escolhe local de execução automaticamente. A comparação mostra quando esses custos anulam a vantagem bruta.

Custos ausentes continuam desconhecidos. Mesmo com um cenário de custos revisados, liquidez, manutenção, seleção do cenário e dimensionamento continuam explicitamente separados. Não entrega recomendação financeira final, utilidade líquida completa, autorização ou ordem. Não representa transferência bancária ou FX. O mecanismo aceita qualquer moeda declarada da conta.

Não altera posições, cash, transações, tabelas, snapshots, modelos, memória, aprendizado, episódios ou journals anteriores. Não treina, solicita refresh, coleta cotações ou chama endpoints financeiros. Apenas lê fontes verificadas e transporta a nova análise pelo endpoint de acompanhamento já existente. Arquivos divergentes ou fontes que mudam durante a leitura são recusados.

## Validação e instalação

1.055 testes Python e 122 verificações JavaScript; validação nos ambientes pandas 2 e 3. Inclui comparação de origem/destino, modelos divergentes, risco maior, dados futuros, moedas distintas, identidade ambígua, aliases sem valor financeiro, custos que eliminam vantagem, ausência de treino/escrita e preservação dos dados. Mais 38 testes simulados do ativador. Instalador validado em cópia temporária, com recusa de baseline divergente, repetição idempotente e backup único; dados, CSV e configuração preservados.

O instalador testa uma cópia temporária, cria backup e tenta a ativação controlada V32. Preserva o Bridge e recusa reinício durante trabalho ativo; não usa SIGKILL nem inicia servidor duplicado. Quando necessário, repetir apenas o ativador após o ciclo normal. Depois recarregar o navegador com Command+Shift+R. O relatório local compacto informa pares comparados e candidatos brutos; o instalador não comprova carregamento no navegador ou resultado financeiro real.

Mantém o escopo da consolidação F3/F4; não abre nova fase. Validação no Mac e conteúdo das comparações reais pendentes da aplicação pelo usuário.

SHA-256 do instalador: `935edf7ddaf55c9225b6fe370b960f1e79dde41a6603038aebd441c3b77c8b06`.
