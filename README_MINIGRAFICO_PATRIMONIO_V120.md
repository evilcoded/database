# Minigráfico do patrimônio V120

Sobre V118 após a reversão do V119. Corrige somente a omissão da chamada ao minigráfico dentro do cartão de patrimônio, introduzida no V118. Dois arquivos: JavaScript do painel e referência de cache no template.

Reutiliza `v36Spark` e o histórico patrimonial já disponibilizado ao painel, no recorte atual de conta/moeda. O gráfico fica abaixo do valor/subtítulo e antes das três métricas. Uma leitura é representada por um ponto; nenhuma leitura produz mensagem explícita. Não mistura moedas, não rateia histórico entre contas e não conecta coberturas diferentes. Não é um novo intraday nem uma correção do coletor.

Não altera valores, backend, saldos, compras, modelos, regras ou persistência de observações. Instalador verifica hashes antes de escrever, guarda backup, aceita reaplicação e recusa divergências. Reinício opcional usa o mecanismo verificado existente.

Testes JS: presença do gráfico no local correto, exclusão de EUR em BRL, histórico de conta incompatível, filtro de ativo e cobertura alterada. Instalação em fixture: igualdade de payload, reaplicação idempotente, divergência recusada e preservação de modelos/ledger. Não houve validação visual na instalação real do usuário.
