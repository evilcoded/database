# V114 — evidências existentes dos modelos globais

A V112 capturou apenas parâmetros do motor original. A validação V113 avaliou o histórico legado e não certifica os laboratórios globais. Para implementar a ligação sem substituir o significado dos modelos, a V114 reúne os experimentos e avaliações já salvos, hipóteses de alocação, acompanhamento prospectivo, fontes históricas e o contexto econômico atual.

É uma coleta, não uma correção do mecanismo de recomendação. Não importa código do projeto, não treina, não muda modelos, não inicia ciclos, não altera carteira/histórico/configuração. Faz um GET local ao monitor existente (sem redirecionamentos ou proxy); não solicita dados a provedores. Grava somente um ZIP privado em Downloads. Pode rodar com o servidor ativo.

Lê apenas caminhos explícitos de modelos JSON e fontes de código. Não coleta config.json, SQLite, ledger, venv, binários de estimadores ou logs. Credenciais em chaves JSON conhecidas e tokens em query strings são removidos. O manifesto registra conteúdo redigido e hashes originais; conteúdo redigido não deve ser tratado como prova de integridade de um selo original. O ZIP pode conter identificadores de instrumentos/contas presentes no contexto de análise e deve ser compartilhado apenas para esta investigação, não publicado no repositório.

Arquivos limitados a 8 MiB, payload total 96 MiB, quantidades por pasta explicitamente limitadas. A amostra por data de modificação não prova que uma versão seja atual ou utilizável: a resposta do monitor e as referências de fontes são necessárias para essa verificação. Limitações e arquivos indisponíveis aparecem no manifesto. API indisponível não impede a coleta dos artefatos locais.

Cinco testes sintéticos verificam preservação dos arquivos, redação de credenciais, recusa de links simbólicos, falha de API, limites por grupo e limite total com manifesto preservado. Sintaxe Bash validada.
