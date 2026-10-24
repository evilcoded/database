# Validação integrada global V121

Coletor de auditoria, **não é patch de aplicação**. Não instala arquivos, não solicita ciclo, mercado ou treinamento. Somente GETs locais do estado, monitor de pesquisa e publicação manual. Registra snapshots antes/depois para detectar ciclo concorrente, hashes do código instalado, thresholds existentes, leituras recentes do diário de observabilidade e os diagnósticos econômicos já produzidos pelo aplicativo.

Objetivo: conferir o estado ativo depois das correções V118–V120 antes de alterar novamente recomendações/avaliação. Os bloqueios anteriores de validação não são removidos pelo coletor. A inexistência de modelo ou aprovação não é convertida em recomendação. Não importa módulos do app nem executa seu ciclo.

Grava exclusivamente um ZIP novo em Downloads, com `validation.json`. Contém valores/identidades financeiras necessários à auditoria, por conta e moeda, que o usuário pode revisar antes de compartilhar. Configuração exportada limitada a action_rules; não exporta fontes, modelos, Keychain ou arquivos de credenciais. Chaves e parâmetros de URL de credenciais são suprimidos no relatório. APIs indisponíveis aparecem como erro, não como sucesso vazio.

Executar `PORQUINHO_VALIDACAO_GLOBAL_V121.command` com o servidor ativo. Não reiniciar. O monitor pode levar até dois minutos; limite de 64 MB por resposta. Depois compartilhar o ZIP indicado em ENVIAR.

Testes sintéticos: somente as quatro chamadas GET previstas, nenhuma modificação nos arquivos do aplicativo, supressão de credenciais, mudança concorrente de snapshot e falha de leitura explícita.
