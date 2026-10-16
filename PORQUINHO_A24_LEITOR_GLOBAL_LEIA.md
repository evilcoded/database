# A24 — leitor global integrado ao laboratório de predição

O patch troca os três pontos de leitura direta de market_daily.csv em prediction_lab.py pelo leitor global. Não treina, não reinicia serviços e não altera dados durante a instalação. A integração só passa a valer no processo da aplicação após ativação planejada. Os ciclos normais de treinamento da aplicação continuam existentes; este leitor não acrescenta gatilhos ou autorização.

O leitor calcula o hash da tabela atual. Se existir uma versão migrada de conteúdo exatamente idêntico, verifica o manifesto, mapeamento de todas as linhas e arquivo original e utiliza essa cópia. Uma cópia corrompida é recusada; não há fallback silencioso. Se a tabela avançou e não há versão com o hash atual, lê a fonte atual como não arquivada, sem escolher arbitrariamente uma versão antiga nem criar arquivos. Verifica novamente a estabilidade da fonte e do código de suporte.

A projeção neutra expõe, separadamente:

- moeda declarada na linha e moeda da medida neutra, mesmo quando a identidade canônica ainda está ausente;
- candidato EUR apenas quando a origem declara CoinGecko, a medida usada é legada e o código atual de fetch_daily contém o contrato reconhecido de pedido EUR por padrão;
- unidade pendente quando falta evidência, ou declaração inválida quando o código de moeda não é válido.

O candidato EUR tem escopo explícito CURRENT_CODE_COMPATIBILITY_NOT_HISTORICAL_PROOF. A moeda efetiva da medida legada continua nula. O código atual não atesta a origem histórica da linha. Uma declaração de moeda acompanhada somente de price_eur é preservada como declaração da linha, sem certificar a unidade da medida. Nunca infere moeda de conta, identidade, FX ou autoridade pelo ticker, país ou coluna. Qualquer código de moeda válido é aceito, sem lista fixa EUR/BRL/USD.

A camada de compatibilidade fornece ao laboratório as mesmas células, ordem, tipos pandas e colunas anteriores. Campos legados permanecem nessa interface interna para preservar features, alvos de 30 observações e o aprendizado existente. Os futuros resultados do laboratório ganham input_contract com hash, origem e contagens de evidência. Não reescreve snapshots anteriores, previsões emitidas, retornos, ciclos ou modelos. Não importa ainda o journal de novas cotações diárias para treinamento: sua amostragem é diferente da tabela histórica e requer integração própria. Não resolve identidades ou vínculos pendentes.

## Validação

391 testes offline com pandas 2.2.3 e 3.0.3. Testes novos conferem leitura de arquivo migrado, corrupção sem fallback, evolução da fonte sem usar versão antiga, moedas arbitrárias, declaração independente da identidade, contrato legado sem atestado retroativo, estabilidade de fonte/código e preservação dos dados. A paridade foi exercitada com 180 dias e dois ativos: features e datas/alvos de maturação idênticos aos calculados pela leitura anterior. Os três pontos reais de entrada do laboratório foram conferidos, e run_next foi executado com dados insuficientes sem iniciar treino.

O instalador confere baselines, cria backup de fonte e executa a suíte em cópia temporária. Depois faz inspeção local somente leitura comparando as células/tipos e as features/alvos de maturação, sem modelos.fit e sem escrever snapshots. PARITY_VERIFIED_RESEARCH_NOT_CERTIFIED significa compatibilidade do leitor, não validação econômica, atestado do histórico ou prova de ativação do processo em execução. Se a fonte mudar durante a inspeção, o relatório exige repetir. PARITY_NOT_COMPLETED exige análise antes da ativação.

Nenhum dado privado é incluído na entrega pública. Não há treinamento real, compra, venda, reinício, promoção canônica ou autorização automática pelo instalador.
