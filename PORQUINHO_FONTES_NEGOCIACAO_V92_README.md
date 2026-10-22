# Aquisição encadeada de fontes públicas — V92

Coletor independente, sem alterações no aplicativo. Segue links HTML relevantes de tarifas, ações, renda variável, negociação e tributação a partir das URLs públicas fornecidas. Não contém bancos ou tickers fixos. Restringe a descoberta aos hosts das fontes de entrada ou ao host efetivamente observado após um redirecionamento. Salva páginas/PDFs como bytes, hashes e relação de origem dos links; não executa scripts nem aplica taxas.

Limites operacionais: até 12 documentos, 12MiB no total, 3MiB por documento, profundidade 4, timeout de 25s por conexão. Esses limites não são regras de negociação. Não declara coleta exaustiva ou que uma resposta 200 prove a aplicabilidade de uma tarifa à conta. Rejeita URLs com credenciais ou query, registra erros e não salva documentos truncados. Não carrega tokens nem credenciais do Porquinho; não solicita treinamento/negociação, não modifica modelos ou arquivos do aplicativo e não exige reinício.

Motivo: ambiente cloud retorna Tunnel connection failed: 403 Forbidden ao consultar os destinos B3 e NuInvest apontados na tabela oficial já recebida. A aquisição no Mac evita supor taxas a partir de páginas inacessíveis. URLs iniciais são dados passados na execução.

Validação local com HTML/PDF sintéticos: descoberta em sequência, captura de PDF, exclusão de host externo e prevenção de loop. Não foi possível validar acesso real neste ambiente; HTTP e documentos reais devem ser analisados após a coleta.
