# V141 — Continuação do V139 R2: referências nativas atualizadas

O ciclo confirmou nove análises de ações e 19 registros prospectivos. A revisão encontrou um defeito independente do perfil de decisão: BRAPI consultava uma ação por ciclo e deixava de atualizar a referência corrente após registrar a primeira amostra diária. Com nove ativos, a rotação podia exceder a janela de atualidade. O caminho CoinGecko já separava amostra diária e referência intradiária; o BRAPI passa a usar o mesmo mecanismo existente.

## Correções

- Planeja também os vínculos já observados no dia e atualiza a referência corrente sem duplicar o diário de aprendizado. O primeiro registro válido por identidade/provedor/moeda/dia continua imutável.
- Consulta até 20 identidades por lote, usando a rota BRAPI e o separador de lote já existentes no projeto. Nove ações podem ser atendidas com uma consulta. O limite é de duas consultas por ciclo; populações maiores ficam explicitamente adiadas, com rotação operacional sem ranking financeiro.
- Reutiliza referências válidas por dez minutos. Cada resposta é validada por identidade, moeda, preço e horário. Respostas parcialmente inválidas não descartam as demais linhas válidas quando o envelope da resposta é válido. Não há repetição imediata após HTTP 429.
- Aceita horário UTC em segundos Unix e ISO com fuso. Não adivinha milissegundos nem o fuso de horários sem zona. Não relaxa a janela de atualidade ou declara uma sessão de bolsa conhecida.
- Atualiza referências de posições verificadas BRAPI mesmo sem demanda para novo investimento, com revalidação de conta, posição e ledger. Essa rota de posição não gera amostras diárias de pesquisa por si só, como já acontecia com CoinGecko.
- Mantém os provedores independentes: falha no caminho CoinGecko não impede a atualização BRAPI. Resultados parciais ficam explícitos. Identidades BRAPI não são enviadas ao transporte CoinGecko.
- O diagnóstico resumido mostra as cotações nativas consultadas/em cache/atualizadas/adiadas, o horário de referência por ação e a cobertura dos cálculos técnicos existentes.

## O que a análise confirmou sobre o modelo

**Este patch não conclui os índices operacionais das ações.** A regra global continua a mesma; ela ainda precisa receber `promising_pct`, `entry`, `risk`, `reversal_risk` e `asymmetry` com significados compatíveis. O escore especializado de oportunidade não foi rebatizado como esses indicadores. Não houve ativação ou treinamento de modelo, mudança de pesos ou relaxamento de limites para produzir COMPRA.

No pacote V114 já fornecido pelo usuário, a inspeção local verificou 78 bundles selados. Os nove vínculos de ações tinham pedidos e retornos de três meses, com 62/63 observações. As respostas continham capitalização, quantidade negociada e máxima de 52 semanas; não continham os mesmos insumos completos do escore cripto. Máxima de 52 semanas não foi tratada como máxima histórica, volume em ações não foi tratado como volume monetário e a capitalização em BRL não foi tratada como capitalização em EUR.

A nova cobertura técnica expõe os requisitos declarados pelas próprias funções existentes, incluindo a média de 200 observações quando indisponível. Isso é informação de cobertura, não um novo limite para compra nem uma condição de ativação acrescentada ao sistema. O trabalho remanescente é definir e verificar a compatibilidade dos indicadores do modelo global; não é preencher novas simulações bancárias ou corrigir novamente a geração das análises.

A janela de atualidade continua sendo respeitada: se o provedor devolver horário antigo, a referência permanece indisponível para uso como cotação atual. Preço atualizado não significa preço de execução, sessão aberta comprovada ou disponibilidade do ativo no banco.

## Instalação e verificação

Aplicar `PORQUINHO_REFERENCIAS_NATIVAS_V141.command --reiniciar` sobre V139 R2 ou V140. São cinco arquivos Python existentes. Os três arquivos de interface do V140 não são alterados. O instalador verifica todas as bases antes de escrever, mantém backup e recusa divergências.

Após um ciclo normal:

```bash
"$HOME/anaconda3/bin/python" -I -B "/Applications/Bridge_Companion/porquinho_v33_web_foundation-2/tools/diagnose_decision_pipeline_a24.py" --resumo
```

Conferir `COTACOES_NATIVAS` e `current_exact_quote_count`. `standardized_action_metric_count` continua separado e não deve ser interpretado como resolvido por este patch.

## Testes e limites da verificação

328 testes de regressão passaram. Depois dos últimos ajustes, 37 testes diretamente afetados passaram novamente. Incluem nove ativos em um lote, renovações ao longo de uma hora preservando os bytes do diário, cache, linhas inválidas, moedas distintas, fontes antigas, timestamps, limites de chamadas, HTTP 429, falhas independentes de provedores, alteração de vínculos/funding, posição com ledger real de teste, ausência de roteamento BRAPI para CoinGecko e integração da cotação corrente com a análise de ações sem promover índices.

Fixtures antigas foram ajustadas ao ciclo atual: o teste de posição V109 agora declara explicitamente a rota somente de posição, já que desde V110 também pode haver pesquisa acima do orçamento; a verificação do agendador usa a atribuição atual e verifica a reutilização da coleta anterior. Isso não muda a política de funding em produção.

Compilação dos cinco arquivos, sintaxe shell e teste do instalador passaram: reaplicação, recusa de divergência antes de escrever e preservação de sentinelas financeiros/modelos/configuração/legado. Não houve coleta ao vivo ou execução no Mac do usuário. Dados do arquivo anexado foram apenas inspecionados localmente; não foram copiados para o repositório ou instalador. O patch não altera posições, caixa, compras, modelos ou histórico legado.
