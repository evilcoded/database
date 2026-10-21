# V54 — P/L atualizado e leitura limitada de snapshots maiores

O portlet de ganho/perda priorizava cotações completas de posições obtidas na captura diária de pesquisa, mesmo quando o snapshot operacional já era mais recente. A leitura do histórico também recusava cada snapshot acima de 2 MiB; o crescimento dos resultados de pesquisa podia fazer snapshots válidos deixarem de aparecer no P/L de dez minutos e no patrimônio diário.

O leitor agora permite até 8 MiB por snapshot, mantendo orçamento de 64 MiB por leitura, limite de quantidade de arquivos e leitura individual limitada. O P/L de dez minutos continua exigindo dois valores totais armazenados, separados por dez minutos com tolerância de dois minutos e amostra recente. Não estima resultados a partir das quantidades atuais. Recusas por limite no leitor de P/L passam a ter contador explícito.

O valor principal do portlet usa a fonte elegível mais recente entre as referências completas de posições e o snapshot operacional. Para referências de múltiplas posições, a data da cotação mais antiga limita a atualização do conjunto. Fontes preservam rótulo, escopo e data. Snapshots globais continuam excluídos sob filtros de conta ou ativo; moedas não são convertidas nem somadas entre si. Referências legadas EUR só são admitidas pelo contrato explícito já existente. A captura diária de pesquisa não se transforma em cotação contínua.

## Instalação e limites

Destino fixo: /Applications/Bridge_Companion/porquinho_v33_web_foundation-2.

Altera somente static/balance_accounts_v41.js, universal_portfolio/cockpit_intraday_a24.py e universal_portfolio/experience_panels_a24.py. Verifica bases conhecidas, cria backup e recusa divergências desconhecidas antes de editar. Não reinicia serviços, solicita coleta/treino/operação, altera posições, dados, modelos, aprendizado ou histórico. Repetição é idempotente. Após o ciclo normal terminar, reinicie apenas Porquinho e recarregue o navegador sem cache.

Não reconstrói lacunas da indisponibilidade nem certifica todo o histórico recuperado. Patrimônio inclui fluxos e não é rentabilidade ajustada; variação do P/L total armazenado também não é retorno ajustado por fluxos. O patch não publica valor final de realocação.

## Validação

- Suíte de release: 1364 testes Python sem falhas/skips; 295 verificações JavaScript.
- 6 testes Python novos: snapshots acima de 2 MiB, patrimônio diário, intervalo incompatível, amostra antiga, recusa acima de 8 MiB e orçamento total.
- 5 verificações JavaScript novas: snapshot mais recente que captura diária, filtros de conta/ativo, referências mais recentes preservadas e data do conjunto limitada à cotação mais antiga.
- Instalador: aplicação, repetição, backup, preservação de sentinelas de dados/modelos e recusa de base divergente antes das edições.
- Verificação privada e temporária dos snapshots fornecidos: leitura de intervalo de P/L e patrimônio diário, sem modificar o ZIP original. Nenhum desses dados integra esta entrega pública.
- A bateria legada ampliada não foi repetida para V54; suas falhas preexistentes estão registradas na entrega V53. A declaração de aprovação refere-se à suíte de release acima.
