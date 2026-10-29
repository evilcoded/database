# V137 — Consolidação operacional global

Prioridade: recuperar o fluxo original de decisão e acompanhamento, antes da reformulação visual do dashboard. A integração usa as mesmas fórmulas e regras originais para todas as fontes, preservando identidade, conta e moeda nativa. Não há negociação automática ou conversão cambial.

## Fluxo entregue

1. Métricas atuais → regras originais → leitura por identidade/conta/moeda.
2. COMPRE: dimensionamento original, competição pelo caixa/orçamento existente, teto de posição e quantidade máxima de instrumentos por moeda. Ativos ainda não presentes na carteira também chegam ao bloco de decisões. Falhas dos critérios de compra ficam explícitas; não se fabricam compras.
3. VENDA: avaliação original e quantidade real da posição. REALIZE: avaliação original por convergência de sinais, preservando revisão quando não há quantidade definida. MANTENHA/ACOMPANHE não viram vendas por diferença de peso ou por um novo stop arbitrário.
4. REALOCAR: apresentação conjunta de saídas e entradas já decididas, na mesma conta/moeda. Não constitui otimização líquida validada e não gasta antecipadamente receitas de vendas.
5. Brain experimental permanece identificado e separado da ação de produção. Universo original de sinais também fica acessível sem inventar vínculo bancário.
6. Ciclo operacional independente dos contratos da pesquisa econômica. A falha dessa pesquisa não impede a consolidação original e seu acompanhamento.
7. Registro prospectivo separado em `data/brain/global_operational_outcomes_a24`, com avaliação em 30/60/90/120 dias corridos. Leituras repetidas intraday não se tornam amostras diárias independentes. São retornos brutos de preços, não lucro de operações realizadas. Sem ativação automática de modelos ou alegação de validação já concluída.

## Limites preservados

Valores dimensionados são referências operacionais brutas para decisão manual; não são ordens líquidas executáveis. O produtor econômico certificado continua separado e mantém seus contratos. Perfis operacionais ausentes (incluindo ações ou renda fixa sem métricas compatíveis) continuam pendentes, com motivo explícito. Caixa desconhecido, avaliação incompleta, dados antigos ou configuração ausente não geram valores inventados. Não foram criados orçamentos nem alterados saldos, posições, compras, modelos ou limiares.

O aprendizado legado e sua cadência continuam intactos. O novo acompanhamento começa com observações futuras; não recria retrospectivamente decisões nem garante modelos aprovados em todos os horizontes. Os portlets globais e o novo layout de gráficos ficam para depois da validação deste fluxo em execução.

## Instalação e diagnóstico

Aplicar sobre V136 com `PORQUINHO_CONSOLIDACAO_SUGESTOES_V137.command --reiniciar`. O instalador verifica todas as bases antes de escrever, cria backup, recusa divergências e pode ser reaplicado sem mudanças adicionais. São 14 arquivos de código/template; os dados existentes ficam preservados.

Após um ciclo normal:

```bash
"$HOME/anaconda3/bin/python" -I -B "/Applications/Bridge_Companion/porquinho_v33_web_foundation-2/tools/diagnose_decision_pipeline_a24.py"
```

O diagnóstico consulta somente `/api/recommendations/operational`: não inicia coleta, treinamento, ciclo ou operação. Não é necessário preencher novas simulações bancárias para validar as regras originais.

## Verificação em ambiente de desenvolvimento

437 testes Python passaram, incluindo 2.000 casos de paridade aleatória das fórmulas originais, compra EUR/BRL, orçamento, teto global de posições, venda/realização, Brain experimental separado, referências antigas, independência do ciclo econômico e maturação prospectiva. Verificação AST preserva o restante do motor original.

Testes DOM com os scripts da página passaram para compra de ativo não detido, venda, realocação, quantidades/valores, cliques, expiração e filtros. Regressões de oportunidades, todas as moedas e formulário de custos também passaram. Instalador validado em cópia temporária: 14 arquivos, reaplicação, recusa de divergência antes de qualquer escrita e preservação de sentinelas financeiras/modelos. Sintaxe shell validada.

Não houve teste no Mac do usuário, treinamento real, coleta ao vivo ou comprovação de uma compra atual elegível. O diagnóstico após instalação confirma o estado real sem forçar uma recomendação.
