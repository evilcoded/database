# A24 V50 — cobertura de custos e comparação por modelo

Continua a etapa de provisões, após a V49. O novo leitor reaproveita o armazenamento de evidências de custos já existente na plataforma. Para cada hipótese, exige conta, instituição, localidade, plano declarado, instrumento, moeda, lado e valor exatos; a rota deve estar explícita na evidência. Não seleciona uma entre fontes conflitantes, não escala uma cotação e não mistura componentes de declarações diferentes.

A cobertura separa comissão documental, referência condicional, valor revisado, não aplicável com evidência e desconhecido. Uma revisão parcial mantém total indisponível. Com evidências completas nas duas operações, recalcula o saldo residual e a diferença por modelo após os custos revisados. Se esses custos excederem o financiamento, sinaliza a falta de cobertura e exige outro valor com evidência exata; não usa cash adicional automaticamente. A comissão documental é substituída pelo componente revisado, nunca somada novamente.

A UI resume cada hipótese em seis campos compactos. **Modelos e cobertura de custos** abre os resultados por modelo e a matriz Venda/Compra; **Fontes e condições das tarifas** abre as fontes documentais. Voltar restaura o popup anterior. O diálogo preserva uma cópia da hipótese exibida para que atualizações do ciclo não troquem seus valores silenciosamente enquanto ela é consultada. Não há novos menus expansíveis.

A diferença após apenas comissões continua separada da diferença após custos revisados completos. Retornos permanecem experimentais e declarações revisadas não constituem atestado independente. Não há escolha de valor, recomendação final, validação de lotes ou ordem. Não se altera a lógica de aprendizado, modelos, memória ou limiares do Brain.

## Dados e fontes

Este patch não adiciona nem renova tarifas bancárias. Reutiliza os contratos atuais e as fontes da V48. Custos variáveis sem evidência exata continuam pendentes; não se presume custo zero, tarifa a partir de uma transação histórica ou taxa fixa de spread. O motor não contém regras específicas de banco, ativo ou moeda.

O leitor é somente leitura: os arquivos de evidências e o cadastro são conferidos novamente antes de aceitar a projeção. Mudança, expiração, conflito ou erro não substituem as leituras anteriores por custos fabricados. O ZIP de diagnóstico adiciona somente contagens de cobertura, sem valores monetários ou componentes privados.

## Instalação

Valida hashes e uma cópia temporária antes de aplicar. Faz backup dos fontes alterados; repetição não cria outro backup. Não modifica saldos, transações, snapshots anteriores, modelos, aprendizado, memória ou histórico. O runner local personalizado permanece intacto.

O ativador protegido reinicia somente o Porquinho identificado na porta 8765, preservando Bridge 8787. Se houver trabalho ativo/em fila, repita apenas `PORQUINHO_A24_ATIVAR_CONSOLIDACAO_V50.command` salvo em Downloads quando o ciclo terminar. Não há SIGKILL, servidor duplicado, pedido manual de refresh, treino solicitado ou operação financeira. Atualize o navegador após ativação com Command+Shift+R.

## Verificação

1282 testes Python, 276 verificações JavaScript e 38 testes do ativador. Incluem identidade/conta/plano/moeda/valor, expiração, ambiguidade, custos sem dupla contagem, insuficiência de financiamento, leitura estável, preservação de dados e diagnóstico sem valores privados. Chromium desktop e mobile 390px: hipóteses compactas, matriz e modelos, fonte documental, popups aninhados/Voltar e ausência de overflow horizontal/erros JavaScript. Instalador exercitado em aplicação e repetição, backup único, baseline divergente recusado e sentinelas financeiros/modelos/histórico preservados.

A ativação e os resultados reais do Mac devem ser confirmados pela saída local e pelo diagnóstico; testes sintéticos não comprovam custos bancários reais.
