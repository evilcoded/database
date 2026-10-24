# Intraday global V119 (sobre V118)

Corrige a projeção do histórico de P/L observado e adiciona curva intraday ao cartão Ganho/perda. O leitor V118 conservava apenas quatro lotes, comparava somente dentro do mesmo arquivo diário e descartava intervalos superiores a 30 minutos. Além disso, não expunha uma série intraday de P/L à UI.

Agora são lidas as observações disponíveis na janela de 48 horas (cauda limitada por arquivo), inclusive na virada UTC do dia, sem transformar a evolução diária em uma série interpolada. Contas e moedas permanecem separadas. A curva usa o P/L desde o custo registrado; caixa e depósitos não viram lucro. Mudanças de população/custo/quantidade interrompem a curva e a comparação. A UI informa o intervalo real, a quantidade de leituras e oferece tabela de horários/cobertura. Exige leitura atual para a variação principal, compatível com a população atual. Histórico antigo continua identificado como histórico, sem parecer cotação atual.

Não altera coleta de preços, modelos, aprendizagem, recomendações, saldos ou transações. Reutiliza o diário de observabilidade do V118 e o ciclo normal; GET não grava. Não cria amostras fictícias. O gráfico inferior legado de cotações continua separado; esta nova curva é explicitamente P/L intraday, não cotação de ativo em base 100.

A imagem enviada não demonstra quantos ciclos foram registrados na máquina ativa. A correção resolve os defeitos reproduzidos no código; se houver somente uma leitura real, ainda será necessária uma segunda leitura normal. Não é possível concluir do screenshot que o coletor parou.

Instalar `PORQUINHO_INTRADAY_GLOBAL_V119.command --reiniciar`. Sem dados financeiros novos, o gráfico usa as leituras V118 já existentes. Se o diário tiver apenas um lote, aguardar dois ciclos normais concluídos. Não reiniciar entre os ciclos é uma conveniência, não requisito de integridade; os dados são duráveis.

Diagnóstico opcional, local e somente leitura:

```bash
cd /Applications/Bridge_Companion/porquinho_v33_web_foundation-2
"$HOME/anaconda3/bin/python" -I -B tools/diagnose_global_intraday_a24.py
```

Verificação: 126 testes Python aprovados, incluindo mais de quatro observações, separação de conta/moeda, meia-noite, intervalo de 50 minutos, população alterada e somente uma leitura. Teste JS verifica curva, delta, filtros e recusa de população divergente. Sintaxe e instalação/reaplicação/divergência/preservação de sentinelas verificadas. Um teste legado EUR já incompatível com a prova de escopo da base anterior permanece excluído. Nenhum teste usou conta ou posição real.
