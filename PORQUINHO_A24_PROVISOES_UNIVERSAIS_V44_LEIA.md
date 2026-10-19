# A24 V44 — Cálculo universal de provisões de tarifas

Etapa preparatória das provisões de realocação. Requer o código V43. Não fecha F3/F4.

## Entrega

Motor puro, sem bancos, ativos, moedas ou taxas predefinidos. Calcula `fixo + principal × percentual / 100`, aplicando mínimo e máximo explicitamente documentados. O resultado é estimativa de referência, sem arredondamento monetário de execução. Regras com outra ordem, escalões, descontos condicionais ou forma de arredondamento não são traduzidas automaticamente para esta fórmula.

Exige conta, instituição, localidade declarada, instrumento, moeda, local de execução, lado BUY/SELL, plano tarifário, produto e canal exatamente iguais entre contrato e consulta. CLI valida conta/instituição/moeda contra o registro atual. Não usa o provedor de preços como local de execução.

Todos os seis componentes precisam de estado explícito: brokerage, exchange_fees, spread, slippage, taxes, other_costs. UNKNOWN deixa o total indisponível, mesmo quando há subtotal de tarifas conhecidas. NOT_APPLICABLE exige evidência; não é usado como zero presumido. Todas as parcelas têm a mesma moeda; sem FX.

O contrato requer URL HTTPS, SHA256 do documento, data da consulta, vigência e declaração explícita de verificação da fonte oficial/aplicabilidade. Estas são declarações do contrato fornecido: o motor NÃO baixa o documento nem verifica independentemente a titularidade do domínio ou o conteúdo do SHA256. Não aceite contratos não revisados como prova de tarifa real.

## Uso após instalação

```
python tools/simulate_official_tariff_a24.py ROOT CONTRATO.json CONSULTA.json
```

A ferramenta lê os dois documentos e o registro local de contas; escreve apenas o resultado na saída padrão. Não grava evidência revisada no store, tarifa, transação, ordem, histórico, modelo ou snapshot.

## Limites deste patch

Não inclui tarifas reais de N26, Revolut ou outros bancos: o acesso HTTPS às fontes oficiais foi bloqueado no ambiente de desenvolvimento. Nenhuma taxa foi inventada ou copiada de histórico. Não inclui robô universal de descoberta/extração da internet. Não resolve a diferença entre identidades financeiras antigas e identidades de pesquisa. Não altera UI, meta semanal, aprendizados, planejamento, recomendação nem valor aprovado de realocação. Não conecta provisões parciais à seleção automática de tamanho. A integração dessas fontes verificadas é a etapa seguinte.

O instalador adiciona somente três arquivos: módulo, ferramenta e testes. Confere baselines V43, valida em cópia temporária, mantém backup/rollback, recusa divergências e é repetível. Não exige alteração do runner local e não reinicia serviços.

## Verificação

15 testes novos: fixo/percentual, mínimo/máximo, precisão Decimal, fontes vencidas/futuras, divergência de qualquer campo de contexto, moedas e instrumentos arbitrários, componentes ausentes/desconhecidos, fonte sem revisão e ausência de autoridade/mutação. Junto à regressão V43: 1171 testes Python e 247 verificações JavaScript em staging. Aplicação/repetição e recusa de baseline divergente com sentinelas de dados, modelos, snapshots e runner local preservadas. Dados sintéticos; não demonstra cálculo de tarifa efetiva de nenhuma conta real.
