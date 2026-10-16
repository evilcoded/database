# A24 — Leitor de séries globais para pesquisa econômica

O fluxo econômico consultava somente o resultado do laboratório legado. Agora sua leitura de disponibilidade de evidências também consome o journal global de pesquisa, verificando as cadeias existentes e expondo o contrato de séries. O monitor e sua UI mostram os totais de séries e retornos observados. O laboratório legado e seus resultados continuam preservados e separados.

Cada série mantém instrumento completo, provedor, ID do provedor, moeda de cotação, evidência de identidade, método de preço e amostragem explícitos. Não há associação por ticker, conversão de moeda ou junção com dados históricos sem identidade. Cada ponto preserva preço decimal, datas, IDs de registros e digests de proveniência. Alteração de evidência de identidade particiona a série.

Uma janela de 30 OBSERVAÇÕES exige 31 registros. Seu resultado é a variação percentual realizada do preço entre pontas, sem custos ou fluxos de carteira. Os dias corridos são registrados separadamente. Não se trata de fechamento diário, retorno esperado, resultado líquido da carteira, probabilidade de sucesso ou maturação de episódio canônico em 30/60/90 dias. Um dia com cotações não gera artificialmente 30 observações.

O novo leitor oferece frames de pesquisa com preços e retornos observados para consumidores futuros. O fluxo econômico e a UI consomem apenas o resumo sem valores ou identificadores individuais. O patch não treina modelos, não cria alternativas econômicas governadas, sizing ou recomendações. Todos os estados de comparação, certificação de modelos, publicação canônica e execução permanecem não autorizados. O produtor independente da F4 continua pendente.

Leitura limitada a 4096 partições e 64 MiB, com verificação de estabilidade antes/depois, recusa de symlinks, registros futuros, duplicidades, preços inválidos e cadeias corrompidas. Falhas são exibidas como indisponibilidade, nunca como contagem zero certificada. Nenhum lock ou arquivo é criado pelo leitor.

Instalação: valida baselines e executa 490 testes Python e 22 verificações JavaScript em cópia temporária sem dados; backup e substituição atômica por arquivo com rollback. Testado com pandas 2.2.3 e 3.0.3, instalação e repetição, recusa de baseline divergente e preservação de CSV, configuração local de compatibilidade e sentinela de dados. Todos os testes usam fixtures sintéticas.

Ativação V9: 33 testes simulados; recusa ciclo ativo/enfileirado, preserva Bridge, não envia SIGKILL nem inicia servidor concorrente. Prova revisão do endpoint e novo snapshot independentemente de um novo timestamp do laboratório; a evidência do leitor de mercado continua sendo relatada separadamente. Aplicação e UI real no Mac ainda dependem da execução local.

Escopo do roadmap: integração das novas observações ao insumo de pesquisa da F4. Não encerra comparação econômica, validação prospectiva de modelos ou publicação canônica. A correção de fontes específicas de produtos de renda fixa não é feita por este leitor.
