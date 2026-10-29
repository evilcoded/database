# V138 — Captura operacional antes da pesquisa e cobertura verificável

## Problema observado

O diagnóstico V137 mostrou plano composto e 18 leituras cripto, mas nenhum registro prospectivo. Esse diagnóstico não distinguia ausência de um ciclo após instalação, falha de captura e ausência de cotação de referência compatível. Também mostrou nove ações brasileiras e um CDB sem leitura padronizada. Essas lacunas não equivalem a recomendação de manter.

A revisão do código encontrou a captura depois das etapas longas de pesquisa, com risco de expirar as referências antes do registro. Encontrou também um coletor de métricas restrito ao perfil CoinGecko. O índice especializado antigo de ações tem outra escala e não pode ser promovido como índice global sem uma transformação fundamentada.

## Correção entregue

- O ciclo normal atualiza as fontes configuradas e captura as decisões originais antes da pesquisa econômica. As etapas seguintes reutilizam os resultados dessas coletas; não solicitam duas vezes a mesma coleta por esse caminho.
- Uma falha de coleta não interrompe as demais etapas operacionais. Uma falha posterior na pesquisa econômica preserva o resultado operacional já obtido. O aprendizado legado segue no mesmo ponto e com a mesma cadência.
- O acompanhamento conta decisões elegíveis, registros novos, decisões já registradas e motivos para não registrar. Sem cotação compatível, informa pendência; não anuncia captura concluída com zero registros.
- Uma alteração de caixa, regras, dimensionamento ou decisão durante a leitura continua invalidando a captura. Alteração apenas no universo visual de mercado não invalida decisões cujos dados relevantes permanecem iguais.
- O resultado do último ciclo fica disponível, com horário, em um arquivo de observabilidade selado e atualizado atomicamente. A leitura do diagnóstico continua sem rede externa, ciclo ou treinamento.
- O mesmo diagnóstico mostra as fontes de ações já presentes: esquemas, horários, contagem e nomes de indicadores. Não exporta credenciais, respostas brutas de provedores ou arquivos financeiros.

## Escopo que continua pendente

**Este patch não conclui a cobertura operacional das ações ou do CDB.** Ele não inventa métricas, não converte a escala antiga em probabilidade de compra e não altera os limiares comuns. O diagnóstico atualizado fornece a evidência da instalação necessária para concluir a compatibilização dessas entradas. A presença de um preço, isoladamente, não fornece risco, assimetria e confirmação diária.

As regras de COMPRE/VENDA/MANTENHA/REALIZE e as fórmulas de dimensionamento do V137 não foram modificadas. O aprendizado novo segue prospectivo, com 30/60/90/120 dias corridos, sem promoção automática. Sem reconstrução de decisões passadas, negociação automática, alteração de modelos ou de dados financeiros. A interface e seus portlets não foram alterados.

## Instalação

Aplicar `PORQUINHO_CAPTURA_GLOBAL_V138.command --reiniciar` sobre V137. Quatro arquivos de código são verificados e copiados com backup. Divergência local recusa a instalação antes de qualquer escrita. Reaplicar o mesmo patch não sobrescreve dados adicionais.

Após um ciclo normal, executar:

```bash
"$HOME/anaconda3/bin/python" -I -B "/Applications/Bridge_Companion/porquinho_v33_web_foundation-2/tools/diagnose_decision_pipeline_a24.py"
```

Os novos blocos são `ULTIMO_CICLO_OPERACIONAL` e `COBERTURA_DE_ENTRADAS`. O primeiro distingue ciclo não observado de captura pendente/indisponível ou realizada. O segundo identifica os contratos ausentes e os artefatos disponíveis.

## Verificações

461 testes Python passaram. Incluem os testes anteriores do fluxo operacional, regras, dimensionamento, identidade, moedas, custos e histórico, mais cenários de captura antes da pesquisa, falha parcial de coleta, diagnóstico durável, ausência/ambiguidade de preço, métricas antigas, contagem diária e inspeção sem promoção de índices antigos. O teste anterior de mudança de plano foi atualizado para mudar o capital efetivo, em vez de um campo arbitrário de apresentação.

Compilação dos quatro arquivos e sintaxe shell passaram. Instalador testado sobre cópia da base: reaplicação idempotente, recusa de divergência antes de escrever e preservação de sentinelas de ledger, modelos, configuração e aprendizado legado. Não houve coleta ao vivo, treinamento ou teste no Mac do usuário. A causa efetiva de zero registros na instalação será identificada pelo resultado persistido do próximo ciclo; o risco de ordenação foi corrigido, sem alegar que era a única causa possível.
