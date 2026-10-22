V64 — Custos revisados e disponibilidade manual revisável

O motor não contém regras por banco ou ativo. A disponibilidade é um registro de dados com conta, instrumento, moeda, canal, estado, data e origem USER_REPORT. Uma declaração posterior AVAILABLE ou UNKNOWN substitui o estado efetivo anterior sem apagar o histórico. Não há detecção automática de mudança no aplicativo do banco nesta etapa. Sem declaração, disponibilidade permanece desconhecida. O universo e os resultados do Brain não são alterados.

O instalador aceita opcionalmente quatro argumentos: ACCOUNT_ID INSTRUMENT_ID CURRENCY STATUS. STATUS pode ser AVAILABLE, UNAVAILABLE ou UNKNOWN. A conta/moeda e o instrumento precisam existir nos cadastros locais. A declaração é gravada de forma acrescentável em data/manual_execution_availability_a24; repetir o mesmo estado é idempotente. Parâmetros particulares da conta não estão embutidos no instalador público.

Reaproveita evidências de custos já revisadas pelo leitor existente para o mesmo ativo, lado, moeda e fração de capital do cenário. Custos completos permitem calcular projeção bruta menos custos declarados, com o calculador existente. Custo desconhecido não é zero; múltiplas rotas geram variantes, sem escolha automática. Essa aritmética não certifica lucro líquido da conta, comparação com preservar caixa, nem um valor de compra financiável. Disponibilidade declarada como negativa identifica o cenário como indisponível nessa rota, preservando-o como pesquisa e sem redirecionar capital.

Não modifica modelos, memória, treinamento ou regras do Brain. Não gera compra/venda, ordens, metas semanais ou sugestão final. Os dados financeiros e modelos não são alterados; a declaração de disponibilidade é um novo dado revisável.

Validação: 10 testes de custos; 7 de disponibilidade e reversão; 28 do monitor; 6 do transporte de cenários; 12 dos painéis e 29 do Dashboard. Testes adicionais de instalação idempotente, mudança UNAVAILABLE para AVAILABLE, preservação dos cadastros e interface. Casos de testes sintéticos, sem consulta ao banco nem validação ao vivo no Mac.

Instalação em Applications com backup e recusa de versões divergentes. Reiniciar somente o Porquinho após concluir ciclos em andamento e atualizar o navegador.
