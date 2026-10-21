# V55 — contexto de tarifas recuperado e leituras visíveis

O leitor de contas restaurado durante a migração omitia o nome da instituição no contexto usado para associar políticas de tarifa. Mesmo com país, moeda e plano cadastrados, as provisões das duas operações permaneciam indisponíveis. O patch recupera a versão já verificada do módulo account_cost_evidence_a24: inclui o nome do registro e verifica plano nas evidências que declaram pricing_plan. Nenhuma instituição/plano/moeda é codificada como exceção no motor. A base antiga foi localizada na entrega pública original e comparada; as duas diferenças são essas.

O portlet de ações pendentes agora mostra um resumo de todas as leituras operacionais, inclusive manter/acompanhar, e disponibiliza os detalhes num popup. Sinais experimentais de negociação são apresentados separadamente e não se tornam ações operacionais nem ordens. Leituras sem identidade financeira completa são explicitamente referências, sem associação por ticker. Ausência da fonte de leituras ou de diagnóstico de realocação aparece como indisponibilidade, não como uma decisão confirmada de manter.

O popup e o resumo informam quantos pares têm modelos comparáveis, quantos estão sem as duas provisões documentais e quantos estão sem dimensionamento. Filtros de conta recusam linhas de conta desconhecida ou diferente; moedas explícitas conflitantes são recusadas. Não há novo timer, endpoint de coleta ou chamada financeira na UI.

## Limites

Este patch não altera critérios de compra/venda, algoritmos, modelos, pesos, aprendizado ou limiares para gerar negociações. Recuperar provisões permite ao mecanismo existente avaliar o dimensionamento, mas não garante uma recomendação positiva. Comissões documentais não equivalem a todos os custos de execução. Seleções indicativas, sinais experimentais, ação operacional e autorização de execução permanecem separados. Não certifica a recuperação integral do histórico após o incidente iCloud.

## Instalação

Destino fixo Applications. Altera apenas universal_portfolio/account_cost_evidence_a24.py e static/dashboard_universal_v35.js, com verificação das bases e backup. Bases desconhecidas são recusadas antes das edições. Não altera contas ou planos cadastrados, dados financeiros, histórico ou modelos. Não reinicia serviços nem solicita refresh/treino/operação. Após terminar o ciclo em curso, reinicie somente o Porquinho e recarregue o navegador sem cache; não é necessário reiniciar o Bridge.

## Validação

Suíte de release: 1370 testes Python e 303 verificações JavaScript, sem falhas/skips nessa suíte. Foram adicionados seis testes sintéticos do registro até a associação de tarifa, cobrindo instituições/moedas/planos arbitrários, ausência de plano, troca de instituição, ambiguidade e preservação dos dados; oito verificações da visibilidade das leituras, separação experimental, escape de HTML, ausência de fontes, filtros e bloqueios.

Instalador testado nas bases antiga e atual reconhecidas: aplicação, igualdade dos arquivos finais, repetição, backup exato, preservação de sentinelas de contas/modelos e recusa de divergência antes das alterações. A bateria legada ampliada não foi repetida; suas falhas preexistentes foram registradas em V53. Nenhum diagnóstico ou registro financeiro privado integra esta entrega.
