# V136 — fontes e revisões no formulário de custos

Conecta os adaptadores documentais existentes ao formulário de revisão de cada cenário. O monitor e a leitura estreita da API reutilizam o mesmo adaptador de cenário; não há novo catálogo de tarifas nem novo cálculo de comissão.

## Entrega

- Em Revisar custos, uma seção compacta mostra as fontes documentais aplicáveis ao valor exato, com links, condições, prazo e componente documental quando disponível. A referência é identificada como parcial, não como prévia atual do banco. Uma política que exige prévia é exibida dessa forma, sem comissão inventada.
- Referências exigem o contexto produzido pelos adaptadores existentes. Fonte expirada, endereço inseguro, outra conta/moeda/instrumento/operação/valor não é reutilizado. Fontes condicionais de bolsa conservam as condições; sessão e faixa não são assumidas.
- Documentos não preenchem campos de custos. Os seis componentes continuam desconhecidos por padrão. Uma falha apenas nas referências informativas não impede o registro de uma revisão factual pelo fluxo existente.
- Revisões salvas e ainda válidas podem ser carregadas para edição por ação explícita. Conta, instituição, plano de preços, instrumento, moeda, operação e valor devem permanecer compatíveis. Revisões substituídas ou vencidas não aparecem como opções atuais.
- Carregar mantém fonte, data observada, componentes e validade original. Desmarca a confirmação, não estende o prazo e não envia POST. Novo registro continua usando a sessão humana local e as verificações e substituições existentes.
- Valores decimais em notação científica são apresentados no formato decimal aceito pelo formulário, sem arredondamento ou conversão de moeda.

O preview histórico de outro valor continua separado de uma revisão atual. Nenhuma taxa pública é promovida automaticamente a cotação bancária, custo completo ou validação independente. Ausência de referência é exibida como ausência, sem taxa zero inventada.

## Preservação e verificação

Sem alterações no motor, pesos, modelos, critérios, ledger, saldos, orçamento ou evidências armazenadas. Não cria treinamento, negociação ou requisição externa de mercado. Abrir a revisão é leitura local; gravar uma revisão exige o envio explícito já existente.

Testes cobrem os adaptadores documentais existentes com dados sintéticos, escopo exato, prazos, links seguros, revisões substituídas, ausência de gravações, conflito de campos, formato decimal e o formulário com todos os scripts do template. As regressões incluem oportunidades, identidades revisadas, Todas separadas, custos, monitor, aprendizado, intraday e gráfico patrimonial. O instalador foi verificado para reaplicação, recusa de divergências e preservação de sentinelas de modelo e ledger.

Não houve consulta real ao aplicativo bancário, nova coleta de mercado ou teste visual no Mac.

## Após instalar

Use `--reiniciar`, atualize a página e abra Custos revisados por cenário → Revisar custos. As fontes e opções usam os dados atuais já armazenados; a função não exige novo ciclo para aparecer. Onde o documento exigir prévia, informe os fatos da prévia atual da conta para o valor exato. Isso não é uma escolha de risco nem uma definição de algoritmo.
