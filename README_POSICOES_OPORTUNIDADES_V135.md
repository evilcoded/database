# V135 — reconhecer posições com referência de pesquisa revisada

Corrige uma divergência de classificação introduzida no painel de oportunidades: a posição registrada pode usar uma identidade anterior à identidade de pesquisa, ligada por uma compatibilidade revisada já usada na avaliação da carteira. O painel só procurava igualdade literal do identificador e podia aplicar a regra de entrada a um ativo já mantido.

Agora o painel reutiliza a cadeia de referência já validada pelo reconciliador existente. O monitor transporta essas cadeias para a composição dos painéis mesmo quando falta preço atual; a identidade da posição não passa a depender da disponibilidade do P/L. A leitura exige conta, moeda, identificador financeiro, identificador de pesquisa, provedor, identificador do provedor, vínculo de fonte atual e data efetiva compatíveis.

O mesmo avaliador existente recebe a posição e seu P/L desde a aquisição. A identidade financeira permanece separada em `position_instrument_id`; `research_instrument_id` identifica a fonte analítica. A associação não é uma fusão de instrumentos, migração de saldo ou prova de elegibilidade no banco.

Compartilhar símbolo ou identificador de provedor não autoriza uma associação. Uma sobreposição sem cadeia revisada, uma cadeia incompatível ou ambiguidade fica pendente em vez de ser declarada nova entrada. Múltiplas posições financeiras não são somadas nem arbitrariamente selecionadas. A disponibilidade no banco continua avaliada no contexto exato da referência da pesquisa.

O diagnóstico passa a incluir `context_counts` em `OPORTUNIDADES_GLOBAIS`, separando posições reconhecidas, alternativas de entrada e contagens de ações por conta e moeda. As posições e o resumo de oportunidades têm populações diferentes: o primeiro lista a carteira; o segundo segue as alternativas vinculadas dos contextos de pesquisa. A ação de uma posição reconhecida usa a mesma função de regras e o mesmo P/L, sem garantir igualdade dos totais entre populações diferentes.

## Preservação

Não altera o motor original, os índices, regras, pesos, modelos, ledger, saldos, orçamentos ou vínculos salvos. Não cria nova associação, recomendação dimensionada, treinamento, coleta ou ordem. Os bloqueios econômicos e de custos permanecem.

## Verificação

Passaram 362 testes Python e as regressões JavaScript/DOM. Casos específicos cobrem cadeias canônicas e do ledger, referência incorporada no cockpit, transporte pelos painéis, identidade sem preço atual, ausência de associação, provedor/fonte/data incompatíveis, outra conta ou moeda, cadeias conflitantes e múltiplas posições, além de verificar a ausência de gravações. O instalador passou nos testes de reaplicação, recusa de divergência e preservação de sentinelas de modelos e ledger. Não houve teste visual no Mac nem coleta real de mercado.

Após instalar com `--reiniciar`, atualize a página e execute o diagnóstico existente:

```bash
"$HOME/anaconda3/bin/python" -I -B "/Applications/Bridge_Companion/porquinho_v33_web_foundation-2/tools/diagnose_global_action_metrics_a24.py"
```
