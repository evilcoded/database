# V113 — validação temporal da calibração original

Corrige duas fontes de informação futura em `training.py`: o treino de cada teste agora exclui alvos que ainda não amadureceram, e a normalização é estimada exclusivamente no treino daquele teste. O mínimo de datas de treino é verificado após a exclusão dos alvos não maturados.

Preserva as fórmulas dos cinco componentes, a regressão ridge, regularização, limites configurados de ativação e regras de compra/venda. A validação corrigida pode produzir outras métricas e outra elegibilidade de calibrações futuras. Não revalida automaticamente nem substitui modelos já salvos.

O alvo legado continua sendo o retorno após 90 observações por ativo; sua data efetiva é transportada até a validação e a unidade OBSERVATIONS é gravada explicitamente em novos modelos. Não converte esse alvo em 90 dias corridos. Recusa mais de uma observação por ativo/dia e moedas explicitamente incompatíveis com as colunas EUR legadas. Não importa BRL para o treinamento EUR nem conecta pesos de carteiras globais a pesos de KPI.

A importação de training.py deixa de ler configuração/criar diretórios. O método usado para o ajuste final continua usando todos os alvos já conhecidos no corte temporal do treino, como é apropriado para esse ajuste final; apenas a avaliação fora da amostra usa normalização por janela.

O instalador altera somente três arquivos de código, com conferência de hash da base, preflight completo, backup e substituição atômica por arquivo. Não executa treinamento, não reinicia serviços e não altera modelos, histórico, carteira ou configurações. Não ativa recomendações globais.

Inclui `tools/validate_calibration_temporal_a24.py`: diagnóstico opcional que calcula validação em memória, sem salvar/ativar pesos. Se o banco legado estiver ausente ou insuficiente, informa isso sem fabricar métricas. A execução requer o ambiente Python do projeto com pandas/numpy.

Validação: 13 testes sintéticos (alvos maturados, limite no mesmo dia, normalização apenas no treino, independência de outlier futuro, datas explícitas, amostra insuficiente, entradas inválidas, maturação por observações, duplicatas intraday e moeda). As fórmulas originais e a regressão foram comparadas com as novas. Instalador testado em ambiente sintético: instalação, repetição sem nova alteração, recusa de base divergente antes de qualquer escrita e preservação de sentinelas de modelo/ledger. Ferramenta testada sem criar modelo/diretórios e sem alterar arquivos de entrada.
