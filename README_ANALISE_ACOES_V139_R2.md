# V139 R2 — Correção do empacotamento

A primeira versão do instalador V139 exigia `equities/technical.py`, `risk_regime.py` e `opportunity.py`, mas não distribuía essas dependências. Na instalação relatada, o instalador parou nessa verificação antes de criar backup, escrever arquivos ou reiniciar serviços.

A R2 inclui o conjunto completo de dependências locais: `__init__`, `contract`, `market`, `fundamentals`, `historical`, `technical`, `risk_regime` e `opportunity`. Pode completar um pacote parcial ou instalar o pacote inteiro quando ausente. Os cálculos são os mesmos do V139; não há nova fórmula ou alteração de limites de decisão.

Somente os oito arquivos declarados do pacote `equities` podem estar ausentes. Arquivos centrais continuam exigindo a base correta. Arquivos existentes precisam ser idênticos ao destino ou corresponder a uma base conhecida; divergências locais são recusadas antes de qualquer escrita. A verificação de links simbólicos e os backups foram mantidos.

São 13 arquivos de código. A R2 pode ser aplicada diretamente sobre V138, após a falha relatada, ou reaplicada sobre o V139 correspondente. Não é necessário executar o instalador anterior. Usar `PORQUINHO_ANALISE_ACOES_V139_R2.command --reiniciar`.

Cinco testes de instalador passaram: pacote totalmente ausente, pacote parcial, reaplicação, importação isolada sem credenciais, recusa de alteração local, recusa de arquivo central ausente e recusa de symlink. Sentinelas de ledger, modelos, configuração e aprendizado legado foram preservados. Sintaxe shell validada. Os seis arquivos distribuídos no primeiro V139 permanecem byte a byte iguais; esta revisão corrige a distribuição das dependências.

O escopo funcional e as pendências descritas em `README_ANALISE_ACOES_V139.md` continuam os mesmos: geração de evidência de análise não equivale a recomendações globais de ações concluídas. Não houve teste no Mac do usuário.
