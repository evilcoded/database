# V127 — Processamento independente de políticas de pesquisa

Uma rejeição de contrato durante o aprendizado de um grupo interrompia todos os seguintes e publicava somente `PolicyError`. O produtor agora mantém o grupo rejeitado bloqueado e tenta os outros grupos independentes. Mantém o limite de uma nova versão por chamada, o bloqueio de escritor concorrente e as verificações globais de fontes e contexto financeiro antes de persistir.

O monitor passa a indicar o código específico de rejeição de grupos ainda sem política. Essa inspeção reaplica o contrato existente em memória, sem ajuste de modelos, rede ou escrita. Somente códigos de erro predefinidos são publicados; textos arbitrários são omitidos.

Não altera seleção, pesos, indicadores, normalização, cortes temporais, maturidade dos rótulos, requisitos de população comum, métodos de treinamento, limites de recomendação ou modelos ativos. Nenhum conjunto incompatível é normalizado ou aprovado artificialmente. Novas versões de pesquisa continuam identificadas pelo código do produtor; arquivos antigos são preservados. A disponibilidade de candidatos e recomendações não é garantida.

Reprodução em auditoria anterior encontrou `COMPLETE_COMMON_CURRENT_FORECAST_REQUIRED` em alguns experimentos. O diagnóstico fornecido pelo usuário confirma `PolicyError` no servidor atual, mas ainda não identifica seu código; o V127 expõe essa distinção.

## Aplicação

Instalador com precondições SHA-256 exatas, backup, recusa de divergências e reinício opcional existente. Altera somente dois módulos de processamento e instala uma ferramenta de leitura. Não altera a UI, cadastro financeiro ou modelos ativos.

Depois de aplicar com `--reiniciar`, executar um ciclo normal na interface e aguardar a conclusão. Consultar:

```bash
"$HOME/anaconda3/bin/python" -I -B tools/diagnose_policy_pipeline_a24.py
```

## Verificação

Testes sintéticos reproduzem grupo inválido seguido de válido, ausência de publicação do inválido, bloqueio global por alteração de financiamento, diagnóstico sem rede/ajuste/escrita e supressão de textos arbitrários. Testes existentes cobrem seleção e validação temporal, associação às contas, base econômica, custos, transporte e acompanhamento prospectivo. Comparação AST confirma que funções de aprendizado, pontuação, planejamento de versões e reconstrução permanecem idênticas. Instalador testado para repetição, divergência e preservação de sentinelas de modelos e ledger.
