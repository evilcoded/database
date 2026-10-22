V60 — integração de caixa e planos existentes com a interface

Transporta os contextos já construídos pelo fluxo de pesquisa e as pendências das alternativas de caixa para o monitor e o popup do Dashboard. Não executa novamente a análise, treina modelos, altera ações, limiares, metas, pesos, regras, planos ou dados financeiros. Distingue saldo, orçamento e valor de proposta, sem transformar enumeração de alternativas ou fonte pronta para revisão em recomendação.

As junções exigem conta, moeda e fingerprint atuais. Classes e orçamento de cada plano são preservados. Diagnóstico ausente ou ambíguo permanece indisponível. A implementação não conclui o produtor de recomendações BRL nem o planejamento semanal autônomo; torna os resultados e impedimentos existentes acessíveis por contexto.

Testes: 6 novos testes Python; 28 testes de consolidação do monitor; 29 testes do Dashboard; 12 testes dos painéis; verificações de interface por moeda, escaping, popup e preservação das entradas. O teste HTTP do monitor utilizou o ambiente local com Flask. Nenhuma validação ao vivo no Mac do usuário.

Instalação com backup e recusa de arquivos divergentes. Requer reinício seguro apenas do Porquinho após terminar ciclos em andamento. Acesso pelo card Insights do Porquinho, seção Caixa e planos por conta.
