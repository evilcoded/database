# A24 — custos das candidatas por contexto

Continuação da consolidação F3/F4. Reutiliza taxas realizadas do ledger e consulta o contrato existente de custos revisados para as candidatas aprendidas pelo Brain. Sem recadastro de transações ou limites manuais de alocação.

## Comportamento

- Liga taxas históricas somente ao mesmo instrumento, conta, moeda e lado BUY das hipóteses incrementais de cash. Mantém referência/hash dos eventos e taxas; não calcula tarifa futura a partir do passado.
- Consulta as evidências de custos revisados somente quando o capital hipotético exato da parcela coincide com o valor explícito da evidência. Usa frações exatas: 100/3 não coincide com 33,33.
- Reutiliza a validação vigente de conta/instituição/país, validade, componentes e evidência. Mantém locais de negociação como candidatos, sem selecionar um automaticamente.
- Detecta fontes alteradas durante a leitura, apresenta falha própria e preserva a base econômica existente. O resumo da UI contém contagens, sem valores financeiros.
- Custos totais e retorno líquido permanecem desconhecidos. Não cria ranking, vencedor, dimensionamento ou recomendação canônica. Nenhum registro histórico, memória, modelo ou snapshot é reescrito. Não coleta preços nem treina.

O cadastro atual não contém contrato de preços/local de negociação. Recibos históricos não comprovam tarifa vigente; a ligação não fecha esse requisito econômico. Evidências revisadas ausentes produzem zero correspondências, nunca custo zero.

## Validação e ativação

964 testes Python e 100 verificações JavaScript em pandas 2.2.3 e 3.0.3; 33 testes simulados do ativador. Instalador validado em cópia temporária, aplicado e repetido, recusando baseline divergente e preservando dados/configuração/CSV.

O instalador gera backup dos arquivos de código alterados, faz regressões em cópia temporária antes de aplicar e tenta ativação controlada V27. Recusa trabalho ativo/em fila; nesse caso repita somente o ativador gerado em Downloads após o ciclo terminar. Preserva o Bridge, sem SIGKILL, servidor duplicado, refresh manual ou operação financeira. Ativação no Mac ainda precisa ser observada.

SHA-256 do instalador: `736b9b3b151f341f1cd9421a1c557ed76fa1fe3433378f912c586fe70745eab1`.
