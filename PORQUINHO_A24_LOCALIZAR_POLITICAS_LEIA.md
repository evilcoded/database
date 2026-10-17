# A24 — Localizar configurações existentes de políticas

Preflight somente leitura para localizar campos reutilizáveis antes de conectar
políticas econômicas ao V22. Não é um novo instalador nem uma ativação.

Os contratos atuais dos planos fornecem orçamento, conta, moeda, estratégia e
classes, mas não limites numéricos de risco, liquidez e concentração.
O armazenamento de autorização delegada contém limites de execução distintos.
Este preflight verifica quais estruturas estão efetivamente persistidas no Mac,
sem importar módulos da aplicação ou interpretar limites de execução como risco.

Inspeciona arquivos conhecidos e candidatos JSON no primeiro nível de `config`,
`settings` e `data`, com limites de tamanho, população e profundidade lógica.
Não percorre histórico de snapshots, ledger, modelos ou memória. Recusa links
simbólicos e fontes instáveis. Fontes ausentes ou não inspecionadas são explícitas.
A ausência nos caminhos pesquisados não prova ausência em todo o projeto.

O relatório contém apenas contagens de nomes de campos de uma lista permitida,
contagens de estruturas candidatas e estados da leitura. Não exporta valores de
políticas, saldos, transações, contas, instrumentos, estratégias ou credenciais.
Nomes de arquivos adicionais são substituídos por um identificador hash do caminho.
A presença de campos não comprova validade, vigência ou aprovação da política.

Execute o `.command` com Bash. A raiz padrão é
`~/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2`; `PORQUINHO_ROOT`
permite apontar outra cópia. O relatório JSON exclusivo, com permissão 600, é
gravado em Downloads. O diretório precisa existir e estar fora do projeto.
`PORQUINHO_REPORT_DIRECTORY` permite indicar outro diretório externo existente.

Não altera código, configurações, dados, modelos ou histórico. Não faz requisições
de rede, reinicia serviços, treina modelos ou concede autoridade financeira.

Validação: 12 testes de privacidade, escopo, integridade e recusa de fontes
inadequadas; duas execuções completas do comando em projeto temporário, com
preservação dos bytes dos arquivos e relatórios distintos. Os testes usam dados
sintéticos. Este pacote não contém relatórios reais do usuário.
