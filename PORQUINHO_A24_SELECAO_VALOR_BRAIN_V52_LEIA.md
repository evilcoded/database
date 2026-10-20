# A24 V52 — seleção indicativa do valor pelo Brain

Acrescenta um seletor específico para realocações de posições existentes. Reutiliza previsões e avaliações purgadas dos experimentos globais atuais, conferidos pelo laboratório existente. Não aplica pesos de distribuição de cash novo como metas da carteira e não substitui estimadores, modelos, memória ou aprendizado anteriores.

## Como escolhe

O seletor compara manter a posição com modelos/destinos/frações candidatos. As frações são 1/k, com k entre 1 e o número de contextos de fonte presentes no universo atual, reutilizando a família de frações da pesquisa existente. Não é um otimizador contínuo de todas as frações possíveis nem uma otimização conjunta da carteira.

O objetivo declarado deste novo método é maximizar o crescimento geométrico relativo a manter, nos períodos de seleção. Para cada período, usa somente as previsões disponíveis na origem para decidir se a troca superava as comissões; depois mede o resultado realizado daquele cenário. As comissões documentadas atuais são aplicadas como hipótese contrafactual sobre um capital de referência constante. Não são taxas históricas comprovadas. Entre categorias documentais ainda condicionais, usa o resultado menos favorável de cada cenário.

A separação cronológica segue o protocolo já usado pela pesquisa: metade anterior para selecionar, removendo alvos que alcancem o início da metade posterior; intervalos sem sobreposição em cada fase; pelo menos dois períodos em cada lado. Isso não comprova independência estatística. Modelo, destino e fração são escolhidos apenas nos períodos anteriores. Empates usam menor giro e fração menor, seguidos de identificadores estáveis; não usam a avaliação posterior.

A escolha fica congelada para avaliação posterior. Se não superar manter nessa avaliação, o seletor se abstém e não procura outro vencedor com os mesmos resultados posteriores. Se o treino não superar manter, ou se a previsão atual não sustentar a troca após as comissões, retorna manter. Falta de referência financeira, previsões, provisões ou população comparável produz abstenção explícita, sem inventar um valor zero como ordem de venda.

Há no máximo uma alternativa selecionada por posição de origem/conta/moeda. Valores são limitados ao capital de referência daquela posição; cada cenário deve financiar a própria compra e comissões, preservando a parcela não vendida e o saldo residual. Não usa outro saldo da conta e não reserva capital.

## O que aparece

O cartão mostra uma leitura de manter, abster-se ou realocar um valor **indicativo**, com a fração e o orçamento total provisionado da compra, já incluindo a comissão. **Como o Brain chegou a esta leitura** abre modelo, protocolo, períodos, métricas e fluxo de caixa da fração escolhida. Não mistura o valor escolhido com tarifas calculadas sobre a posição inteira; os cenários integrais permanecem como referência nos detalhes. Os popups mantêm Voltar e Fechar.

A avaliação é retrospectiva, sem comprovar que as fontes estavam disponíveis no passado. Vantagem relativa a manter não significa retorno absoluto positivo. Não há probabilidade de acerto, rentabilidade futura garantida ou lucro líquido validado. O método pode retornar manter ou abster-se para todas as posições; não força uma realocação.

## Limites e preservação

É uma indicação experimental para análise manual. O valor final de negociação continua dependente da cotação líquida bancária e dos custos/condições restantes, como spread, impostos, lotes e elegibilidade. `final_transfer_amount` continua indisponível; não há publicação canônica ou autorização automática. A observação diária e os ciclos de aprendizado de 30/60/90 dias continuam existentes; o seletor não exige aguardar um novo ciclo canônico para avaliar o histórico já disponível.

A seleção é calculada somente em memória sobre os experimentos existentes, sem chamar fit/treino de estimadores, provedores de cotação ou endpoints financeiros. Os parâmetros são reavaliados quando os experimentos correntes mudam. Não cria evidência prospectiva retroativa. Repetições da pesquisa não são ensaios independentes.

O estágio opcional calcula uma cópia da projeção. Se falhar, descarta inclusive decisões parciais e mantém as leituras anteriores. Os arquivos financeiros e históricos não são alterados. O diagnóstico exporta somente contagens de estados; não exporta valores escolhidos, frações ou saldos.

## Instalação e ativação

O instalador valida hashes e uma cópia temporária antes de aplicar, com backup único dos fontes alterados. Repetição não gera outro backup; baseline divergente é recusado. Snapshots anteriores, modelos, memória, aprendizado, transações, posições, saldos e runner local são preservados.

O ativador protegido pode reiniciar apenas o Porquinho identificado na porta 8765, preservando o Bridge 8787. Se houver trabalho ativo/em fila, repita depois somente `PORQUINHO_A24_ATIVAR_CONSOLIDACAO_V52.command` salvo em Downloads. Não usa SIGKILL, segundo servidor, refresh manual, treino solicitado ou operação financeira. Após ativar, recarregue o navegador com Command+Shift+R.

## Validação

1344 testes Python, 290 verificações JavaScript e 38 testes do ativador. Cobrem seleção de fração/modelo/destino, avaliação posterior sem seleção por seus resultados, abstenção, custos condicionais, conservação de caixa, isolamento de conta/moeda/identidade, uma alternativa por posição, fontes/digests, preservação de leituras após falha parcial e diagnóstico sem valores privados. O instalador foi exercitado com aplicação/repetição, backup único e divergência recusada; sentinelas de dados/modelos/histórico/runner local permaneceram intactos.

Chromium desktop e mobile 390px verificaram o valor da fração escolhida, orçamento com comissão incluída, estados manter/abster-se, detalhes/Voltar e ausência de overflow horizontal ou erros JavaScript. Um teste sintético com 30 pares, 10 estimadores, 6 frações e 4 categorias tarifárias levou cerca de 0,34 segundo neste ambiente. Isso não certifica desempenho, valores ou decisões no Mac: a ativação e os resultados reais precisam ser confirmados pela saída local.
