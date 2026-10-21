# V53R2 — compatibilidade com leitor recuperado

Mantém os dois arquivos finais e o comportamento do V53. Amplia somente as bases explicitamente reconhecidas do instalador: leitor anterior `9196731f...d95183` e leitor de release `9155e717...24b9c6`. A versão anterior omitia institution_id, account_type, management_mode e owner_profile na projeção de contas. A atualização recupera esses metadados de leitura; não altera os cadastros.

Monitor-base exigido: `0401db215adb9a66913fbd827917e228f4f3cbca26e7b0b4a098a1f553653371`. Arquivos divergentes desconhecidos continuam recusados antes das alterações. Backup, repetição idempotente e ausência de alterações em dados/modelos mantidos. Sem reinício automático.

Teste do instalador nas duas bases reconhecidas: aplicação, igualdade dos dois arquivos finais com V53, repetição, backup exato, sentinelas de contas/modelos preservadas e rejeição de entrada desconhecida antes das edições. Código final já validado pela suíte de release V53 (1358 Python, 290 JS); nenhuma mudança nesse código na revisão R2. As falhas da bateria legada ampliada e os limites de avaliação de pesquisa permanecem descritos na entrega V53.
