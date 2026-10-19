# A24 V46 — Plano da conta como metadado universal

Requer V45. Campo opcional e livre `pricing_plan`, até120 caracteres, nos formulários existentes de cadastro e edição de conta. Sem lista de instituições, planos, moedas ou ativos no código. Plano aparece no resumo/detalhe das contas no fluxo completo de Contas e Bancos; não substitui o plano de investimentos nem o orçamento.

## Persistência e compatibilidade

O cadastro grava o plano informado no registro existente. Na edição, campo omitido pela API preserva o valor anterior; nulo/vazio explícito limpa a informação. Contas antigas sem campo continuam legíveis, sem migração de dados ao ler. Tipo inválido, tamanho excessivo e caracteres de controle são recusados antes de gravar. Texto exibido é escapado. IDs, instituição, conectores, permissões, posições, planos de investimento, moeda e outros metadados permanecem sob seus fluxos anteriores; informar plano não altera esses campos nem habilita execução.

O instalador não preenche contas automaticamente e não contém os nomes/IDs reais das contas do usuário. Após ativação, abra Contas e Bancos, edite cada conta e preencha o nome de seu plano. O nome é relativo à instituição da própria conta, não um identificador global compartilhado entre bancos. Não é necessário reenviar transações.

## Retroalimentação

O registro atual passa a fornecer `pricing_plan` ao leitor de contexto de custos. Uma consulta/evidência que declare plano exige correspondência exata com o plano atual da conta; ausência ou troca de plano recusa o uso da tarifa específica. O simulador V44 já chama esse verificador e passa a consumir o dado novo. Cotações exatas legadas que não declaram dependência de plano mantêm seu contrato anterior; não são reclassificadas automaticamente como tarifas de plano.

O plano bancário não participa do fingerprint das séries/solicitações de pesquisa. Alterá-lo não recria pedidos, reinicia séries ou altera modelos, memória, aprendizagem, snapshots, ledger e histórico de investimentos. Informar o plano não certifica uma taxa, não resolve os demais campos de produto/canal/rota e não cria uma recomendação de realocação.

## Limites

Este patch entrega cadastro/API/UI e validação de compatibilidade para custos. Não baixa documentos bancários, extrai tarifas ou insere taxas reais. A rede de desenvolvimento ainda responde403 às fontes oficiais; a inclusão dos domínios foi salva no rascunho das configurações do ambiente e depende de publicação/aplicação externa. Não há taxas Standard presumidas no código. As metas semanais continuam na sequência após as provisões.

## Aplicação

Seis arquivos,187 baselines, validação em cópia temporária, backup/rollback e aplicação repetível. Acrescenta os três módulos de dependência da API à verificação das fontes de teste; não altera esses módulos. Runner local não é exigido nem substituído. Nenhum dado do projeto é modificado pelo instalador.

Ativação protegida apenas do Porquinho identificado, Bridge preservado. Jobs ativos impedem o reinício; repita somente `~/Downloads/PORQUINHO_A24_ATIVAR_CONSOLIDACAO_V46.command`. Nenhum SIGKILL, segundo servidor, refresh manual, treinamento ou operação financeira é solicitado. Rotinas normais do app continuam após ativação. Depois, Cmd+Shift+R e editar plano pelo fluxo existente.

## Validação

15 novos testes Python: compatibilidade sem migração, criação/edição/limpeza/omissão, preservação de outras contas/arquivos financeiros, plano incompatível, consulta legada, estabilidade das solicitações de pesquisa e rotas Flask reais em fixture isolado. Seis verificações JS: formulários, restauração/escape, POST/PUT, limpeza e ausência de default. Total1206Python+257JS.38testes simulados do ativador. Chromium desktop/mobile390: editar/salvar/reabrir, plano arbitrário e texto longo no cartão, sem overflow horizontal ou erroJS. Instalador aplicado/repetido, baseline divergente recusada e sentinelas de dados/modelos/histórico/runner preservadas. Testes sintéticos, sem afirmar cadastro de planos ou aplicação de tarifas nas contas reais.
