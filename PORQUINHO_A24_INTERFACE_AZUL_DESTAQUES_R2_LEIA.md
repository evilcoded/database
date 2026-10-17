# Correção do instalador A24 V38 — R2

Corrige exclusivamente a criação de diretórios de fontes antes da substituição atômica dos arquivos. A versão anterior tentava criar um arquivo temporário em static/crypto-icons antes de essa pasta existir. As regressões terminavam com sucesso e a aplicação falhava com FileNotFoundError, antes da ativação. O teste anterior preparava essa pasta por engano; o teste corrigido a remove antes de executar o instalador.

O payload de interface, seus hashes e o ativador V38 são idênticos. Brain, modelo, memória, aprendizado, dados e histórico não recebem alteração adicional. Não é necessário criar a pasta manualmente. R2 cria os diretórios de código ausentes e revalida o caminho antes de gravar, preservando a recusa de symlinks e de divergência de baseline. Backups anteriores permanecem preservados. Se os hashes do rollback local não corresponderem ao estado esperado, recusa aplicação em vez de substituir código divergente.

## Verificação

Reproduzida a falha original com static/crypto-icons ausente. Após a falha, todos os hashes dos arquivos foram conferidos com o baseline e arquivos novos continuaram ausentes. Em seguida, R2 aplicada e repetida na mesma cópia: 1.107 testes Python e 197 verificações JavaScript por validação, repetição idempotente, um backup de aplicação bem-sucedida além do backup da falha reproduzida e dados/CSV/config preservados. Divergência externa de baseline também recusada. Payload e ativador inalterados; verificações visuais anteriores continuam referentes à mesma UI.

Instalação com o novo nome R2 em Downloads evita conflito com o instalador antigo. Ativação continua controlada: preserva Bridge, recusa ciclo ocupado, sem SIGKILL ou segundo servidor. Após ativar, Command+Shift+R. Pacote público contém apenas código e logs de fixture, não o relatório privado do usuário.

SHA-256: `5016acddfe27528d860fd710243c9628c7f25fa3c18dcfc10e56e51e1248c4e5`.
