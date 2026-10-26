# V133 — corrigir Todas, separadas em Oportunidades

O V132 comparava a moeda de cada linha com o valor vazio do filtro Todas, separadas. Isso ocultava todas as leituras, embora elas continuassem disponíveis no servidor.

O V133 renderiza um bloco por moeda nessa seleção. Conta e busca continuam aplicadas dentro do recorte. Contagens, expansão da lista e identificadores dos popups são separados por moeda; clicar em um ativo BRL não abre os dados de uma linha EUR de mesmo índice. Renderizar não muda o filtro salvo. Selecionar uma moeda específica mantém o recorte correspondente.

Somente `static/experience_panels_v37.js` e o identificador de cache no template mudam. Nenhum cálculo do motor, indicador de fonte, limite, modelo, dado financeiro ou coleta foi alterado.

O teste DOM com todos os scripts reais reproduziu a falha na versão anterior e passou na versão corrigida. Cobre duas moedas simultâneas, cartões, listas expandidas, detalhes, retorno, conta, busca e recorte vazio. Também passaram os testes existentes de oportunidades, gráfico patrimonial, intraday e revisão de custos, além da reaplicação do instalador, recusa de divergência e preservação de sentinelas de modelos e ledger.

Após instalar, atualize a página. A correção usa os dados já disponíveis e não exige um novo ciclo para corrigir o filtro. Não foi feito teste visual no Mac.
