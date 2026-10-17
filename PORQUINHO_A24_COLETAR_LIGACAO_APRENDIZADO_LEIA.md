# A24 — Fontes da ligação aprendizado → decisão

Coletor somente leitura de 24 caminhos explícitos de fontes Python do Brain e de
seus consumidores. Necessário para verificar a implementação de memória e
autoconhecimento do aplicativo local, ausente dos pacotes anteriores disponíveis
no ambiente de desenvolvimento. Não instala um substituto para o Brain.

O código disponível ainda contém chamadas às rotinas originais de aprendizagem.
O laboratório global reutiliza características/estimadores em experiências
isoladas, sem incorporar automaticamente o estado da memória anterior. Os limites
manuais do V23 não são o caminho obrigatório para a inteligência autônoma.
Estes fatos de código não comprovam funcionamento completo no Mac ou preservação
funcional de toda a cadeia; as fontes coletadas permitem investigar a integração.

O comando salva um ZIP em Downloads (ou PORQUINHO_REPORT_DIRECTORY), fora do
projeto. Inclui código-fonte privado e relatório de presença, hashes e contagens
de chamadas estáticas. Nenhum módulo do aplicativo é importado ou executado.

Não coleta bancos de memória, arquivos de modelos, snapshots, configurações,
ledger ou outros arquivos de dados financeiros. Não percorre diretórios de dados,
não reinicia serviços, não faz rede, não treina e não altera arquivos do projeto.
Os caminhos são fixos, com limites de tamanho e recusa de links simbólicos.
Arquivos com atribuições diretas de credenciais literais detectadas são omitidos;
essa checagem não é um detector completo de segredos em código.

O ZIP gerado contém fontes privadas: enviar somente na conversa, sem publicá-lo
no GitHub. Este pacote público contém apenas o coletor e testes sintéticos.

Validação: oito testes de preservação, escopo, não execução, saída externa,
credenciais literais, arquivos ausentes, limites e links; duas execuções completas
do `.command` com dados sintéticos, sem alterar bytes no projeto. Nenhuma
declaração de validação econômica, aprendizado funcional ou autoridade financeira
é produzida pelo coletor. Ausência no pacote anterior não prova ausência no Mac.
