# Custos por rota e prévias V124 — sobre V123

Corrige o fallback que confundia falta de tarifa aplicável com necessidade de componentes de bolsa. O leitor de rotas retornava `None` quando nenhum documento cobria o instrumento ou o plano da conta; o monitor então usava o caminho banco/bolsa. Isso ocorria, por exemplo, quando um documento cobria um instrumento específico e o cenário pesquisava outro.

A seleção continua dirigida pelos dados das políticas, não por listas de ativos ou bancos no código. Agora a ausência de documento, o plano não informado/não coberto, a classe ambígua, o documento expirado, o conflito entre políticas e a prévia exigida têm estados distintos. `None` fica reservado ao caminho não pertencente ao namespace de rotas descrito pelas políticas, preservando o fallback existente de banco/bolsa quando apropriado. Falta de documentação nunca é tratada como indisponibilidade permanente do ativo. Nenhuma tarifa nova ou desconto é inferido. Catálogo ausente/inválido torna-se erro explícito.

O custo documental conhecido, o ajuste condicional de orçamento, as hipóteses de bolsa e seus limites permanecem os existentes. Cenários mistos incompletos continuam sem total; este pacote não inventa custo para completar uma alternativa.

Prévias relatadas recebem um inventário separado dos cenários. Assim, um registro existe e pode ser consultado mesmo sem plano conciliado ou se seu valor divergir do cenário atual. O inventário preserva conta, moeda, identidade e valor exatos. Se a conta mudou de moeda/contexto, marca essa mudança. Comissão explicitamente relatada como zero aparece como tal, com custo total e spread desconhecidos. Não extrapola taxas, quantidades ou preços para outro valor ou momento. Não cria revisão de conta nem certificação independente.

O plano da conta já registrado passa a integrar a projeção de leitura do cockpit. Não altera o cadastro nem preenche Standard/Metal/Ultravioleta automaticamente. A UI acrescenta apenas detalhes recolhíveis de prévias e rotas dentro do popup existente “Custos e fontes”, nos filtros atuais. Cartões de patrimônio, meta, P/L, minigráfico e intraday são preservados.

Seis arquivos: leitor de rotas, leitor de prévias, conexão no monitor, projeção do cockpit, detalhes de custos e cache do script no template. Não altera modelos, aprendizagem, critérios, documentos de tarifas, ledger, saldos ou compras. GET não grava; não há treinamento, execução ou nova recomendação.

Instalar `PORQUINHO_CUSTOS_ROTAS_E_PREVIAS_V124.command --reiniciar`; atualizar a página e abrir Dados e análises dos planos → Custos e fontes. A publicação completa ainda depende das validações econômicas e de evidência atual de custos. O pacote não remove esses bloqueios.

Validação: 137 testes Python aplicáveis passaram, mais testes JS de isolamento, escape de textos, comissão zero explícita, prévia sem cenário, preservação do minigráfico e intraday. Dois testes antigos que esperavam fallback silencioso para plano/classe não cobertos foram substituídos por expectativas de estados explícitos. Um teste antigo de avaliação sem prova de identidade já incompatível com a base V108 foi excluído. Instalador testado para igualdade do payload, idempotência, preflight de todos os arquivos, divergência recusada e preservação de ledger/modelos. Não houve validação visual no navegador do usuário.
