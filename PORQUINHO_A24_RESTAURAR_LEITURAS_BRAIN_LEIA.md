# A24 — leitura operacional do Brain restaurada

Corrige a regressão que subordinou a exibição dos sinais existentes à publicação canônica ainda não integrada. O modo manual volta a exibir a leitura analítica disponível na própria linha, sem aguardar maturação de 30/60/90 dias. Não cria novos sinais nem converte leituras anteriores em publicação canônica.

## Interface

- Tag principal sem publicação canônica: LEITURA · COMPRE/VENDA/ACOMPANHAR/MANTER etc., usando somente action já presente na linha e uma lista explícita de ações reconhecidas.
- REALIZE em revisão permanece REALIZAÇÃO EM REVISÃO. Percentual só aparece quando execution_state e execution_fraction_pct existentes o especificam; alvo zero não gera venda ou dimensão de ordem.
- Fonte da leitura identificada; data da linha ou do snapshot visível. Horário ausente é informado como tal; heartbeat não se torna data da análise. Isso não atesta atualização minuto a minuto.
- Contexto global incompleto/divergente é marcado como leitura de referência, sem criar identidade, conta, moeda ou FX. Não procura sinal em outra linha por ticker nem consome intelligence aninhada que possa vir de um join por símbolo.
- Publicação canônica existente com correspondência exata continua preservada e prioritária. A ausência de publicação deixa de apagar uma leitura analítica existente. O aviso geral passa a dizer Publicação canônica — indisponível, sem declarar todo o Brain indisponível.
- Métricas da página Mercado contam também os sinais analíticos agora exibidos. A cadência de coleta/cálculo não muda: este patch restaura a apresentação, não cria alimentação de minuto em minuto.

Não modifica o motor analítico, estimadores, calibração, alvos, modelos, memória, histórico, snapshots, registros prospectivos, transações, posições ou saldos. Não altera API de negociação, autorizações ou execução automática; nenhuma ordem/compra/venda é disparada pela leitura. Ausência de análise continua explícita, nunca preenchida com ACOMPANHE por padrão.

## Premissas de aprendizagem e auto-otimização

Registra no autoconhecimento estrutural: análise disponível antes da maturação dos horizontes e aprendizado de programação para auto-otimização progressiva do código. Caminho registrado: aprender, propor, testar em sandbox, revisar e reverter quando necessário, com autonomia futura mediante escopo autorizado.

Esta é a premissa/objetivo de desenvolvimento. Não implementa por si só toda a aprendizagem de programação nem habilita autoalteração irrestrita em produção. Preserva os mecanismos existentes de autoconhecimento, diagnóstico e patches. Maturação de modelos pode gerar evidência para melhorias; melhoria efetiva precisa ser medida, não presumida.

## Instalação e validação

Backup, regressões em cópia temporária e ativação controlada V31 do Porquinho. Preserva Bridge, sem SIGKILL, servidor duplicado, refresh manual ou endpoint financeiro. Se houver ciclo ativo, repetir somente o ativador após o ciclo terminar.

Após ativação, recarregue a página do Porquinho no navegador com Command+Shift+R. O ativador verifica código/endpoint/snapshot no servidor, mas não comprova que o navegador carregou o novo JavaScript. O relatório completo continua em Downloads e a saída no Terminal é compacta.

1.021 testes Python e 112 verificações JavaScript nos ambientes pandas 2.2.3 e 3.0.3; 38 testes simulados do ativador. Testes atualizados para o comportamento solicitado: análise sem canônica visível, origem/data explícitas, sinais desconhecidos recusados, ausência de join por ticker/derivação por alvo, realização em revisão preservada e prioridade canônica exata. Inclui leitura de autoconhecimento sem escrita/reset da memória. Instalador aplicado/repetido, baseline divergente recusado, backup único e dados/CSV/config preservados. Validação real no navegador/Mac ainda pendente.

Mantém a consolidação F3/F4. A cadeia econômica canônica continua pendente, em paralelo à leitura operacional já existente.

SHA-256: `ff7b7dbc572c633670541158e0d8d68b3b5952d7c1629077f8ade527c301e4c0`.
