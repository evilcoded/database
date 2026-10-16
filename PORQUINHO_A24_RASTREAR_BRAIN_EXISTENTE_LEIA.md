# A24 — Reaproveitamento do Brain existente: verificação local somente leitura

Dentro da consolidação F3/F4, identifica resultados já persistidos do laboratório multi-algoritmo e os separa do modelo global Momentum/Ridge experimental. Não interpreta o desempenho desse último como avaliação de todo o Brain. Não é instalador, não altera backend/UI e não reinicia serviços.

Relatório agregado: algoritmos/ensemble existentes, métricas retrospectivas já registradas, datas, cobertura explícita de instrumento/provedor/provider_id/moeda, duplicidades e conflitos declarados. Inclui os registros de maturação e captura prospectiva já cobertos pelo preflight existente, por trilha e horizonte. Dias corridos e observações permanecem unidades distintas. Presença dos campos não é verificação de identidade; nenhuma moeda ou identidade é inferida por símbolo, conta ou sufixo _eur. Métricas de modelos distintos não são comparadas sem populações e referências pareadas.

Lê somente os caminhos documentados no código; ausência de um resultado não prova inexistência do mecanismo ou ausência de treinamento em todo o Brain. Maturação descritiva não certifica modelo. Não reexecuta treino nem congelamento de baseline, captura, escrita em memória, reatribuição de histórico ou publicação econômica.

Código Python standalone, sem importar módulos da aplicação. Recusa fontes por symlink e limita tamanhos/populações. JSONs checados quanto a alterações durante a leitura. Auditoria bloqueia rede, subprocessos e escrita no projeto. O projeto continua em operação: arquivos alterados durante a leitura são sinalizados; não há alegação de snapshot atômico de toda a árvore.

Salva somente ZIP agregado em Downloads, contendo BRAIN_EXISTENTE.json e LEIA.txt. Não inclui arquivos de projeto, preços, saldos, quantidades, contas ou previsões individuais. As métricas exportadas são erros/índices de avaliação dos modelos, não valores monetários da carteira. Código/fonte do projeto não é exportado no ZIP local.

Validação: oito testes sintéticos, incluindo métricas existentes, identidade não inferida, contexto completo ainda não certificado, duplicidade, números inválidos, privacidade, preservação de bytes/mtime e execução standalone com ZIP agregado. O resultado real depende dos arquivos locais do Mac e deve ser lido antes da integração.
