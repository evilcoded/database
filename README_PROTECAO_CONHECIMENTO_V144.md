# V144 — explicação de perdas e manutenção do conhecimento

O último diagnóstico do ETH indicou ACOMPANHE, não MANTENHA. A regra de venda
atual avalia índice de risco ou tese fraca com confirmação diária; a perda desde
o custo de aquisição não é um gatilho percentual de venda. O índice de risco
também não é a porcentagem que o investidor já perdeu. Este patch torna essa
situação visível sem forçar saída, alterar limites ou inventar proteção financeira
que a configuração não tem.

## Proteção do capital: alerta separado da ação

Qualquer perda verificada em posição com custo e valor atuais compatíveis recebe
`LOSS_REVIEW_REQUIRED` / `REVISAR_PROTECAO_DO_CAPITAL`. Não há limiar novo de 19%,
20% ou outro percentual. Isso é um aviso para revisão; não substitui COMPRE,
VENDA, REALIZE, MANTENHA ou ACOMPANHE, não dimensiona uma venda e não envia ordens.

A comparação é feita por identidade financeira, conta e moeda, desde o custo
registrado. A cotação precisa ser atual e respeitar o instante mínimo da operação.
Sem custo/cotação compatíveis, a posição fica pendente, não com perda zero.
Inconsistência entre P/L reportado e valor menos custo também fica pendente.
Não há conversão EUR/BRL, comparação de dinheiro entre universos ou soma global.

A posição ganha um aviso compacto “Revisar proteção”. Ao clicar, aparecem:

- perda nominal e percentual desde o custo registrado;
- valorização matemática necessária para voltar ao custo (19% de perda exigiria
  aproximadamente 23,46% de alta; isso não é projeção ou promessa de recuperação);
- ação real do mecanismo e distinção explícita entre ACOMPANHE e MANTENHA;
- valores atuais e limiares configurados para as duas vias de venda;
- presença ou ausência de confirmação dos dois dias UTC completos;
- data da referência e indicação de que não existe stop-loss percentual nessa regra.

As condições detalhadas completas continuam disponíveis no mesmo bloco clicável.
O alerta vale para todas as moedas/provedores e é exibido apenas enquanto a
referência estiver dentro da validade existente de 30 minutos. O perfil comum
V143, seus índices, limites de compra/venda e dimensionamento não foram alterados.

## Conhecimento do Brain: causa e correção

O painel compara hashes de um catálogo descritivo salvo com os arquivos atuais.
Patches alteram arquivos e deixam o catálogo salvo divergente se ele não for
sincronizado. Essa divergência não significa esquecimento da memória financeira.
Além disso, o registro anterior incluía arquivos de dados mutáveis, gerando
“conhecimento desatualizado” até por alterações legítimas nos dados de domínio.

O catálogo atualizado:

- descreve o perfil comum, proteção por custo, aprendizado prospectivo e regras
  globais, mantendo claras as autoridades de posição, conta e transação;
- rastreia código e UI; dados continuam listados como fontes, mas seu conteúdo
  variável não é tratado como alteração do código da arquitetura;
- informa `descriptive_only: true` e `financial_validation_granted: false`;
- preserva a versão anterior em `data/brain/system_knowledge/history`;
- verifica mudanças de definição e do conjunto de caminhos, além dos hashes;
- não declara um cache ausente ou corrompido como se estivesse atualizado.

A instalação humana deste patch verifica seus payloads e, em seguida, sincroniza
somente o catálogo descritivo. Não usa a atualização de hashes para declarar
correto o comportamento do código ou validado um modelo financeiro.

Nos ciclos normais, a manutenção verifica divergências. Se ainda não houver
catálogo, pode inicializar essa descrição sem tocar em código. Para um catálogo
existente divergente ou corrompido, **não aceita silenciosamente os novos hashes**:
gera uma proposta no Patch Center, limitada ao JSON do conhecimento. A proposta
é vinculada ao conteúdo/código atual, não se repete a cada ciclo para a mesma
situação e não é aplicada automaticamente. Uma proposta rejeitada ou que sofreu
rollback fica para revisão, sem gerar uma nova cópia em todo ciclo.

Antes da aplicação manual, o Patch Center revalida o candidato e os hashes atuais.
Mudança de código ou do próprio candidato impede a aplicação. O fluxo existente
de validação e rollback continua ativo. Nenhuma proposta desse tipo tem permissão
para alterar fonte, finanças, modelos ou confiança. Ela sincroniza uma descrição;
um defeito funcional de código ainda precisa de diagnóstico e correção próprios.

O painel passa a dizer “Conhecimento sincronizado”, em vez de “Arquitetura
consistente”, para não confundir descrição atual com certificação funcional.
Ao reabrir Aprendizado, consulta o estado atual em vez de reusar indefinidamente
o cache JavaScript da sessão. O autorretrato genérico também identifica o escopo
de investimentos globais e as capacidades reais de revisão/proposta.

## Instalação e diagnóstico

Aplicar após V143. São 13 arquivos de código/UI, com dois módulos novos. O
instalador pré-valida todos os hashes, recusa divergências e symlinks, faz backup,
verifica os payloads instalados e sincroniza o conhecimento descritivo. A
reaplicação preserva a descrição já atual, sem gerar novos backups de fonte.
Há novos cache tags para carregar as alterações; os botões Global/EUR/BRL e os
gráficos existentes foram preservados.

Após instalar e reiniciar, atualizar o navegador com Cmd+Shift+R. Nos detalhes da
posição com perda atual deve aparecer o aviso e sua explicação. Depois do ciclo
normal concluir, o diagnóstico `tools/diagnose_decision_pipeline_a24.py --resumo`
mostra `PROTECAO_CAPITAL` e `CONHECIMENTO_SISTEMA`, além das sugestões e índices.
As APIs GET continuam sem gravações; a manutenção escreve somente durante ciclo
normal ou instalação/aplicação explícita de atualização descritiva.

Não altera ledger, compra real de SOL, saldos, posições, configurações, índices
V143, limites, agendamento, memória financeira SQLite ou arquivos de modelos.

## Verificação

Testes cobrem perda de 19% mantendo a ação ACOMPANHE, perda com MANTENHA/VENDA,
mesma política de alerta em moedas diferentes, prejuízo mínimo, lucro, custo
indisponível, P/L conflitante, cotação antiga/futura e referência anterior à compra.
Os testes de DOM usam os scripts completos e verificam aviso clicável, recuperação,
explicação, conta/moeda, expiração, ausência de POST financeiro e preservação dos
botões de moeda e dos blocos de decisão.

A manutenção foi verificada para atualização após instalação, cache inválido,
leituras sem escrita, dados financeiros que não causam drift de arquitetura,
proposta única, aplicação manual somente de JSON, recusa após alteração de
código/candidato, recusa de symlink e preservação do conteúdo anterior. O
instalador foi testado para idempotência, preflight de divergência e preservação
de sentinelas de finanças/modelos/memória. Nada disso valida rentabilidade de
estratégia nem comprova o valor atual da perda de ETH no Mac do usuário.
