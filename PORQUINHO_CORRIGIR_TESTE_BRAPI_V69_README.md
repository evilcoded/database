# Teste BRAPI V69

Corrige o retorno incondicional CONNECTIVITY_PROBE_UNAVAILABLE para BRAPI. O botão existente agora escolhe deterministicamente um instrumento B3 com símbolo/moeda explícitos no catálogo global, lê a credencial pelo caminho solicitado e consulta o endpoint BRAPI com Bearer no cabeçalho. Não cria vínculos por ticker; a escolha é apenas uma consulta de diagnóstico. Não tenta todos os ativos para encontrar um sucesso.

Sucesso significa uma resposta com símbolo, preço positivo e moeda correspondentes, sem certificar atualização ou cobertura completa do plano. A tela informa que os demais ativos não foram verificados. HTTP 401/403 não é classificado automaticamente como token inválido. HTTP 429, falhas de rede, credencial ausente e falha de leitura têm estados separados. Não salva respostas, tokens ou cotações. Redirecionamentos bloqueados, timeout 10s e resposta limitada a 256KiB.

Não modifica Keychain, credenciais, modelos, seleção, aprendizado, orçamento ou dados financeiros. Twelve Data continua com teste não implementado, agora com texto explícito. Demais adaptadores preservados. Requer V66 para leitura do catálogo. Reiniciar Porquinho após ciclos concluídos e atualizar navegador. Instalador faz backup, verifica bases e é idempotente.

Validação: 24 testes de radar, transporte e teste BRAPI com rede simulada; sintaxe JavaScript verificada. Não houve consulta ao vivo da BRAPI neste ambiente. A auditoria enviada pelo usuário comprovou leitura da mesma credencial e sucesso em ABEV3 no horário coletado; não identifica a causa do 401 anterior.
