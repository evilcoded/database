# A24 V45 — Reconciliação de referências das posições

Requer V44 instalado. Etapa das provisões de realocação; meta semanal permanece na sequência.

## O que muda

O comparador deixa de rejeitar automaticamente uma referência apenas porque o identificador financeiro antigo é diferente do identificador de pesquisa. Exige a cadeia completa: cadastro canônico confirmado da posição, conta e portfólio existentes, correspondência de pesquisa previamente revisada e vínculo de provedor explícito na moeda exata da conta. A quantidade continua vindo da posição atual projetada pelo plano, e a cotação deve ser única para identidade, provedor, provider_id, moeda e origem da previsão.

Não extrai relações do ticker, nome, prefixo ou país. Não contém lista de bancos, moedas, ativos ou formatos de identificadores. Uma relação de pesquisa isolada permanece insuficiente. Conta, moeda, identificador, provedor ou data incompatíveis impedem o uso da referência. A origem da previsão não pode preceder a vigência do vínculo da cotação. Fontes alteradas durante a leitura recusam a projeção.

A correspondência é composta em memória, com referências aos registros que a sustentam. Não altera os identificadores originais nem cria uma nova equivalência financeira no ledger. O resultado é um valor analítico de referência para comparar cenários, não preço de execução, migração de titularidade, comprovação de elegibilidade de corretora ou recomendação.

## Custos e UI

A UI distingue a referência reconciliada do vínculo somente de pesquisa e de uma cotação ausente. As regras anteriores continuam: tamanho não selecionado, custos desconhecidos pendentes, todas as fontes e moedas explícitas. Cenários com custos revisados continuam vinculados aos identificadores financeiros originais; as tarifas não são transferidas por alias. A operação BUY+custos precisa ser financiada exatamente pela SELL líquida dentro do capital de referência; sem cash adicional ou FX. Nenhuma seleção de modelo, ordem ou valor final de realocação é criada.

Não insere tarifas oficiais reais e não ativa a busca automática de tarifas. O motor genérico V44 permanece intacto. Ausência de custos não bloqueia a visualização do valor de referência e da capacidade teórica de custos, mas mantém a recomendação final pendente.

## Preservação e ativação

O instalador verifica 181 baselines, valida 1191 testes Python e 251 verificações JavaScript em cópia temporária e instala seis arquivos de código/teste com backup/rollback. Não exige nem substitui o runner local. Não escreve em dados, posições, abertura, ledger, snapshots, modelos, memória, aprendizado, tabelas ou journals. Não preenche histórico retroativamente.

O ativador confere hashes e reinicia apenas o Porquinho identificado, preservando Bridge. Recusa jobs ativos, não envia SIGKILL e não inicia servidor duplicado. A aplicação retoma suas rotinas normais; ativação não solicita treino, refresh manual ou operação financeira. Se estiver ocupado, repita somente `~/Downloads/PORQUINHO_A24_ATIVAR_CONSOLIDACAO_V45.command`. Após ativação, atualize a página com Cmd+Shift+R.

O diagnóstico V43 é reutilizado e reconhece o novo estado `REGISTERED_POSITION_REVIEWED_SOURCE_REFERENCE`. O ZIP local contém IDs e contagens/estados com os mesmos limites anteriores; não inclui valores financeiros, transações ou provas privadas de confirmação. O console imprime `ZIP_PARA_COMPARTILHAR`. Não há upload automático.

## Evidências e limites

20 novos testes Python para composição e valoração da cadeia, ausência de confirmação, identidade/conta/moeda/provedor divergentes, falta de quantidade, preço ausente/ambíguo, datas, duplicidades, ausência de tarifas, custos nos IDs originais e estabilidade dos arquivos. Quatro novas verificações JavaScript para o estado reconciliado, referências mistas, ausência da cadeia e custos desconhecidos. Total:1191 Python+251 JS. 38 testes simulados do ativador. Instalador aplicado e repetido em fixture sintético, com baseline divergente recusada e dados/modelos/histórico/runner intactos. Chromium desktop/mobile390: referência reconciliada e posição sem cadeia diferenciadas, popup/Voltar funcionando, sem overflow ou erroJS.

Esses testes não comprovam que os registros privados do Mac satisfazem toda a cadeia. O ZIP anterior exportou IDs, mas omitiu os campos privados de confirmação; a instalação local confere esses campos sem exportá-los. F3/F4 continuam pendentes dos custos reais, dimensionamento, decisão e validação do fluxo manual completo.
