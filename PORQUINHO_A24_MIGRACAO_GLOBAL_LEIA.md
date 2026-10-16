# A24 — primeira migração versionada da tabela de mercado

Este patch migra `data/database/market_daily.csv` para um novo componente global de pesquisa em `data/brain/global_market_migrations_a24/<SHA256-do-original>/`. Não substitui ainda a entrada consumida pelo Brain em execução. Não migra snapshots, previsões ou modelos neste passo.

Cada versão contém `original.csv` byte a byte, `observations.jsonl` com todas as linhas na mesma ordem e `manifest.json` com hashes, contagens e mapeamento das colunas. Cada observação preserva todos os valores originais, inclusive campos desconhecidos, células vazias e duplicados, e expõe identidade, medidas neutras e estado de unidade. Números permanecem como texto decimal sem arredondamento. A leitura verificada regenera o mapeamento e compara todos os registros com o original arquivado.

O sufixo `_eur` não certifica a unidade. Medidas antigas são transferidas, mas continuam com moeda nula/estado não verificado. Apenas medidas já neutras com contexto explícito completo preservam a moeda declarada; isso não certifica a fonte, a identidade ou o modelo. O patch não reatribui identidades por ticker, não mistura moedas e não altera datas ou maturação. Valores inválidos permanecem no arquivo com estado inválido, sem descarte. CSV estruturalmente inválido interrompe a migração.

O instalador adiciona três fontes/testes, verifica os baselines anteriores, executa 371 testes em cópia de fontes e cria backup do patch. Depois executa a migração da tabela local. A fonte é conferida novamente antes e depois da publicação da cópia. Cada versão completa é publicada por renomeação sob trava; arquivos são fsync antes da publicação. Uma nova tabela gera outra versão; repetir o mesmo conteúdo verifica e reutiliza a versão existente. Versão corrompida é recusada, nunca reparada/sobrescrita automaticamente. A versão mais recente não é ativada implicitamente. Um arquivo de lock separado é criado para sincronizar migrações concorrentes.

Nenhuma operação financeira, rede, FX, treinamento, reinício ou publicação canônica é solicitada. O histórico de snapshots, resultados maturados e modelos continua nos locais atuais e não é escrito pelo módulo. A migração copia dados privados apenas dentro do próprio projeto; nenhum dado local é publicado no GitHub.

## Reexecutar ou verificar

```bash
root="$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2"
"$root/.venv/bin/python" -I -B "$root/tools/migrate_global_market_a24.py" --root "$root"
```

Para verificar uma versão existente, acrescente `--verify-bundle HASH` com o `bundle_id` impresso no relatório. Isso verifica a integridade e lê os registros sem migrar novamente.

## Escopo e próximos passos

Esta é uma cópia global migrada e verificável da tabela de mercado. A troca dos leitores do Brain e a migração dos demais componentes exigem patches próprios e verificação de compatibilidade. O patch não resolve os 44 pares com identidades ausentes no catálogo nem confirma vínculos de provedores. Os seis criptoativos mantêm suas posições e seu histórico atuais.

## Verificação

371 testes offline: linhas/células e bytes preservados, duplicados, ordem, precisão, moedas explícitas arbitrárias, unidades legadas não inferidas, corrupção recusada, repetição idempotente, novas versões, alteração concorrente da fonte, fonte por symlink recusada, snapshots/modelos/maturados intactos e ausência de rede/subprocesso no migrador. Instalador validado com aplicação, repetição, baseline divergente e CSV original/sentinela preservados. Não constitui validação de dados reais do Mac.
