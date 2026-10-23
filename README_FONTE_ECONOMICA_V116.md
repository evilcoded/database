# V116 — emissão da fonte econômica e identidades das ações

Corrige o encaminhamento estrutural até o produtor manual da V115. Não cria algoritmos de retorno, risco, custo, utilidade ou dimensionamento, nem modifica critérios de validação ou modelos salvos.

## Alterações

- Os rascunhos DEPLOY_CASH/INCREASE passam a informar explicitamente o instrumento de destino; KEEP/SELL/REDUCE informam o instrumento de origem. REALLOCATE mantém ambas as pontas. Os identificadores de alternativas existentes são preservados. Não há mudança em posições, ledger ou regras de compra/venda.
- Um emissor no ciclo normal reúne os componentes ligados às ações e usa `economic_component_set_producer_a24` para verificar o contrato completo já existente. Não remove alternativas incompletas de uma comparação. Uma comparação inteira incompleta não é emitida; outras comparações independentes completas podem prosseguir.
- Além do escopo por instrumento/conta/moeda/horizonte, a emissão automática exige `action_context` em cada componente, com correspondência explícita de case_id, alternative_id, kind, source_instrument_id, destination_instrument_id e reference_capital. Isso impede aplicar automaticamente o custo/contrafactual de outra ação ou outro capital ao mesmo instrumento. A ligação deve vir do produtor que avaliou aquele componente; não é inferida nem acrescentada a pesquisas pelo patch.
- O capital de referência deve existir no contrato da ação; orçamento e caixa não se tornam valor de compra. O baseline de caixa precisa de identidade e modelo explícitos: não são inventados rendimento zero ou um ativo financeiro de caixa. Componentes, validade de publicação e candidatos de dimensionamento são transportados somente quando fornecidos, sem preencher valores ou flags.
- Somente conjuntos completos aceitos geram `results/governed_economic_components_a24.json` com o contrato original. A geração usa trava local, revalidação dos insumos, limite de tamanho e substituição atômica. Resultados próprios obsoletos são retirados quando deixam de ter insumos completos. Arquivos governados preexistentes de outro produtor são preservados. Sem conjuntos aceitos e sem arquivo próprio anterior, nenhum arquivo vazio é criado.
- O resultado do emissor acompanha o cache/API de publicação manual. O diagnóstico agora preserva a razão real do transporte e mostra `source_production` com contagens e motivos. Falta de envelope e falha de hash deixam de ser confundidas.

## Situação atual

A V114 mostrou componentes de pesquisa sem validação completa. Eles continuam bloqueados. Este patch implementa o emissor e corrige identidades; não calcula nem certifica os modelos econômicos ainda ausentes. Com os dados atuais pode continuar havendo zero sugestões. Não é necessário nem correto editar flags de pesquisa ou criar modelos manuais para fazer o diagnóstico passar.

A V116 não altera o aprendizado nem a calibração, não inicia treinamento e não envia ordens. O instalador muda apenas seis arquivos de código, com conferência de hash, backup e preflight completo. A escrita do artefato econômico ocorre no ciclo normal somente nas condições acima. Não há novo agendador.

## Validação

172 testes Python passaram, incluindo 16 testes novos do emissor e regressões de planos, comparação, componentes e publicação. O caminho positivo sintético percorre emissão de arquivo → transporte por hash → comparação → dimensionamento → publicação de sugestão. Os testes verificam pesquisa não promovida, ausência de componentes, escopo divergente, ligação por ação obrigatória, capital não inferido, fonte externa preservada, mudanças concorrentes de insumo, idempotência, retirada de conjuntos próprios obsoletos, links simbólicos e preservação de modelos/ledger. A etapa efetiva do servidor foi executada isoladamente com o emissor real e revalidação dos insumos. Os testes das identidades também verificam a manutenção dos IDs antigos.

Instalador testado em árvore sintética para instalação, repetição, recusa de base divergente e preservação de sentinelas de modelo e ledger. Python e Bash verificados. Não houve execução no Mac ou nos bancos do usuário.

Após instalar e reiniciar com um ciclo normal concluído, `tools/diagnose_manual_publication_a24.py` mostra o resultado resumido, sem pedir novo treinamento ou coleta de mercado.
