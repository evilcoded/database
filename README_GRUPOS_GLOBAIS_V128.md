# V128 — Grupos globais por suporte temporal e processamento em lote

## Problema e comportamento

O servidor reportou `COMPLETE_COMMON_CROSS_SECTION_REQUIRED`: as avaliações não contêm sempre os mesmos ativos em cada origem. Misturar calendários, começos de série e datas atuais diferentes em uma única distribuição por moeda impede o contrato existente de aprendizado. O lote de um experimento por ciclo também deixava nove algoritmos BRL e dez EUR pendentes no diagnóstico recebido.

O V128 prepara grupos de entradas com exatamente os mesmos intervalos históricos e origens atuais por algoritmo. Usa somente identidade, moeda, datas e algoritmo para o agrupamento: nenhum nome de banco/provedor, preço, previsão ou retorno realizado escolhe o grupo. Cada amostra de avaliação/previsão permanece uma vez em algum grupo. Não preenche dados, intersecta datas, corta linhas, converte moeda, mistura intervalos ou presume disponibilidade no banco.

O aprendizado original é reaplicado sem alterações em cada grupo. População divergente entre modelos, dados insuficientes, previsões ausentes, vazamento temporal e excesso de amostras continuam bloqueados. Cada grupo tem versão e fontes brutas vinculadas por hash. A base econômica reconstrói o agrupamento a partir dos experimentos originais antes de aceitar uma referência.

Mais de um grupo na mesma moeda pode produzir cenários mutuamente exclusivos para um plano. As identidades dos grupos devem ser disjuntas. Nenhum grupo é eleito vencedor ou recebe novo orçamento. As alternativas compartilham o mesmo recurso de caixa e não devem ser somadas. O vínculo de custos mantém conta, moeda, cenário e capital exatos.

## Lote e preservação

No ciclo normal, o laboratório percorre moedas alternadamente e usa os algoritmos existentes em lote limitado ao menor entre 20 e o número de moedas elegíveis multiplicado pelo número de algoritmos existentes. Até 20 novas versões de políticas podem ser gravadas por chamada, mantendo revalidação de fontes e financiamento antes de cada gravação. O limite padrão de uma experiência nas chamadas diretas do laboratório continua disponível; o servidor solicita o lote explicitamente.

A duração do ciclo normal pode aumentar. Não há treinamento paralelo adicional: estimadores e limites internos de recursos são os mesmos. Versões antigas e modelos ativos não são substituídos. A mudança de código gera novas versões isoladas de pesquisa, como prevê o mecanismo existente.

O acompanhamento prospectivo identifica separadamente os grupos na mesma moeda e usa somente suas fontes na comparação. Registros antigos sem grupos mantêm seus identificadores e regras de avaliação. Não há reconstrução retroativa ou promoção automática.

Não altera indicadores, estimadores, pesos, pontuação, normalização, horizonte de 30 observações, cortes temporais, critérios de compra/venda, ledger, saldos ou posições. O orçamento BRL acima do caixa continua sendo uma pendência financeira distinta; o patch não altera essa intenção automaticamente. Custos e validação necessários a recomendações permanecem exigidos.

## Validação e aplicação

Testes sintéticos reproduzem o erro exato do servidor e calendários com alvos diferentes; verificam preservação de todas as amostras, ausência de seleção por resultados, rejeição de subconjuntos impostos, diferenças entre modelos, previsões ausentes, moeda, limites de recursos, persistência, reconstrução da base econômica e episódios prospectivos. Testes existentes de aprendizado, contas, custos e transporte também são executados. AST comparada confirma funções centrais de aprendizado, treinamento, atributos, seleção temporal e avaliação prospectiva idênticas. Reprodução somente em memória de três experimentos anteriores de auditoria confirmou grupos compatíveis no aprendizado original; não comprova resultado do servidor atual.

O instalador exige os hashes anteriores exatos, cria backup, recusa divergência/symlinks e permite reinício pelo mecanismo existente. Inclui sete arquivos de código; nenhuma mudança na UI.

Após aplicar com `--reiniciar`, executar um ciclo normal pela interface e aguardar concluir. Depois:

```bash
"$HOME/anaconda3/bin/python" -I -B "/Applications/Bridge_Companion/porquinho_v33_web_foundation-2/tools/diagnose_policy_pipeline_a24.py"
```

Esse diagnóstico somente lê o servidor. Espera-se que indique os experimentos concluídos, os grupos aprendidos ou o motivo específico dos restantes. A existência de candidatos de pesquisa não garante recomendações validadas.
