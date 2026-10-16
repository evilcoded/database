# A24 — correção da leitura de posições no diagnóstico

O adaptador de consolidação anterior aceitava apenas dicionários. O read model verificado retorna uma tupla de objetos congelados `SeededPosition`, definidos em `opening_seeded_derivation.py`. A rejeição desse formato gerava `runtime_positions: ValueError` e diagnóstico parcial, embora captura, laboratório e endpoint estivessem ativos.

O patch aceita especificamente `SeededPosition` e os dicionários já suportados. Converte para uma cópia de leitura sem modificar objetos, abertura, ledger, posições, modelos, snapshots, aprendizagem, vínculos ou journals. Nenhum formato arbitrário de dataclass é promovido a posição. As referências de conta textuais só são tratadas como contas verificadas quando o `account_status` corresponde a um dos contratos explícitos já emitidos pelo read model. Nome de banco ou referência não resolvida não é convertido em identidade canônica. Conflitos entre referências continuam bloqueados.

A UI e seu endpoint permanecem com o mesmo contrato. A correção não liga por ticker os IDs antigos da carteira aos novos IDs de pesquisa. Estados de fonte pendente ou identidade incompleta ainda podem aparecer legitimamente. Também não conecta o produtor canônico nem produz recomendações de manter/comprar/vender/realocar; essa integração permanece na F4.

O instalador verifica os baselines e acrescenta a correção e os testes em cópia temporária, faz backup, aplica o código e inspeciona o estado em processo separado somente leitura. Depois gera em Downloads o ativador V7 e tenta a ativação controlada com as mesmas proteções de PID, Bridge, fonte e tarefa ativa. Não envia SIGKILL, não inicia segundo servidor se o antigo não sair e não solicita refresh/treinamento/operação financeira. O aplicativo retoma suas rotinas normais. Ativação bloqueada por tarefa ativa pode ser repetida usando somente o ativador V7.

V7 também distingue `CONSOLIDATION_UI_ACTIVATED_PARTIAL_DIAGNOSTIC` de uma observação completa quando o endpoint ainda reporta diagnóstico parcial. A presença do endpoint e do leitor não é tratada como prova de que toda posição foi reconciliada.

## Verificação

433 testes Python e 18 verificações de frontend aprovados com pandas 2.2.3 e 3.0.3. Os seis testes novos usam o `SeededPosition` real, referência de conta textual verificada, referência legada não promovida, mistura com dicionários, rejeição de outro dataclass e preservação de objetos/valores financeiros. O instalador passou em aplicação, repetição, baseline divergente recusado e preservação dos arquivos sentinela/CSV. Ativador V7: 33 testes simulados, incluindo reporte distinto para diagnóstico parcial. Os testes não substituem a confirmação local das posições do Mac após ativar.

Não publica dados privados ou comprovantes do usuário. A observação de novas capturas deve ser interpretada separadamente de validação de modelos, conclusão de horizontes e autoridade canônica.
