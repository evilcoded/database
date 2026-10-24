# Reverter V119 para V118

Restaura exclusivamente os cinco arquivos que existiam antes do V119 usando os bytes publicados no instalador V118. Não depende de escolher uma pasta de backup local. Aceita somente os hashes conhecidos V118/V119 e recusa qualquer outro conteúdo antes de escrever. Faz backup próprio, reaplicação idempotente e reinício opcional verificado.

Não altera ledger, saldos, compras, modelos ou observações coletadas. O diagnóstico local acrescentado pelo V119 pode permanecer, sem executar nem mudar o aplicativo. Não remove módulos do V118. Não pretende corrigir o intraday que já estava pendente no V118; restaura a apresentação e o leitor anteriores enquanto se identifica a regressão da instalação ativa.

Verificação em projeto sintético: cinco arquivos finais exatamente iguais aos payloads V118; preservação de sentinelas do ledger, modelo e diário; repetição sem novo backup; divergência recusada sem mutação parcial.
