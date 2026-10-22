# Auditoria de histórico brasileiro recuperado V77

Coleta direcionada, sem rede nem importação de módulos do projeto, dos armazenamentos históricos brasileiros existentes e dos seus relatórios conhecidos. Inclui cópias em diretórios de backup conhecidos, com limite de arquivos e bytes. Resume hashes, schemas, fonte, moeda/identidade explicitamente armazenadas, quantidades de pontos e período por série. Não exporta os pontos de preços, parâmetros de modelos ou posições financeiras.

Não junta símbolos automaticamente, não transforma metadados atuais em atestação histórica, não completa moeda ausente, não interpreta adjustedClose como ajuste comprovado e não altera arquivos do projeto. Não executa estimadores, rotinas de refresh ou treinamento. O ZIP em Downloads deve ser revisado para determinar compatibilidade antes de qualquer integração.

Validação: sintaxe shell/Python e execução sobre fixture histórica, com preservação dos bytes de origem. Não comprova que o armazenamento exista no Mac; essa é a finalidade da coleta.

## Entrega ainda pendente: UI e validação brasileira

Depois da integração de fontes compatíveis, consolidar valores BRL por conta e cobertura nos cartões/gráficos, distinguindo caixa, posições avaliadas, parcelas desconhecidas, P/L e fluxos de capital. Exibir fonte/data, referência atual ou antiga e histórico incompleto sem inventar valores ou converter moedas implicitamente.

Expor por ativo e conta o resultado da análise e sua etapa: pesquisa, análise em avaliação, impedimento por dados/custos/disponibilidade ou recomendação final efetivamente produzida. Validar que a leitura publicada deriva do produtor correto, com moeda, horizonte, contexto de conta/plano e custos correspondentes. Mostrar a razão da ausência de sugestão, sem transformar aquisição bem-sucedida ou previsão experimental em recomendação. Preservar modelos, horizontes, critérios e aprendizados; não impor quota diária de sugestões nem uma espera geral de 30 dias.
