# Leitura intraday V122 — sobre V120, depois da reversão do V119

A coleta V121 demonstrou que o diário patrimonial já recebe leituras e que o monitor calcula diferenças de P/L. O quadro inferior de intraday, porém, continuava conectado ao leitor de cotações, que é outra fonte. O novo leitor projeta o diário de observabilidade existente com seus horários reais de 48 horas, separado por conta/moeda. Não altera a gravação ou o ciclo.

Somente o quadro intraday existente ganha duas visões: P/L da carteira (observado, desde o custo registrado) e Cotações de mercado (gráfico anterior preservado). Mantém seletor de janela. Fontes/tabela acessíveis por clique. Não adiciona curva ao cartão superior de ganho/perda, não muda sua altura e não remove o minigráfico do patrimônio.

Verifica digest, schema, horários conscientes de fuso, escopo e população/cobertura. Recusa arquivo parcial, modificado durante leitura, symlink ou pontos conflitantes. Usa uma cauda limitada de 2 MB por dia, no máximo três dias para 48 horas. Não transforma ausência de preço em zero. Curva interrompida em mudanças de quantidade/custo/cobertura ou lacuna superior a 30 minutos. Um ponto permanece um ponto. Aporte não é lucro; não há interpolação de observações adicionais. Horários exibidos no fuso do navegador.

Não corrige nem promove componentes econômicos. Critérios operacionais, validação dos modelos, política de comparação, recomendações e custos permanecem os existentes. Um modelo com erro maior que sua referência não é certificado pelo instalador. O horizonte de 30 observações permanece sem conversão para meta semanal.

Quatro arquivos de código: novo leitor puro, conexão nos painéis existentes, renderer do quadro intraday e cache do script no template. Nenhuma alteração em ledger, patrimônio, dados, modelo, pesos, algoritmo ou artefatos de aprendizagem. GET não grava, não treina e não coleta mercado.

Instalar `PORQUINHO_LEITURA_INTRADAY_V122.command --reiniciar`, atualizar a página e abrir o quadro intraday. Não depende de criar novo histórico se o diário V118 já contém pontos. A evolução diária/minigráfico podem ter somente um dia observado; não são reconstruídos para preencher o passado.

Validação: 126 testes Python aplicáveis aprovados; um teste legado EUR já incompatível com o contrato da base anterior continua excluído. Testes JS verificam filtros, seis pontos, janelas, gráfico de cotações preservado e minigráfico inalterado. Replay privado dos pontos de seis lotes da auditoria confirmou a leitura sem alteração da fonte. Fixtures públicas sintéticas. Instalação/reaplicação/divergência e preservação de sentinelas verificadas. Não houve validação visual no aplicativo real; não se presume que esses testes comprovem seu layout em todos os navegadores.
