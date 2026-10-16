# A24 — pistas observadas para revisão e aplicação explícita de vínculos

Este patch melhora a ficha offline e acrescenta `apply-reviewed` ao fluxo existente. Não cria vínculos durante a instalação e não altera posições, snapshots, aprendizado, modelos, previsões ou dados maturados. Não precisa reiniciar o Porquinho para abrir a ficha ou registrar a revisão. O coletor ativo relê o registro nos ciclos normais.

## Pistas de fonte

A ficha inclui IDs de provedor já presentes nos metadados dos candidatos observados, usando somente igualdade exata do `instrument_id` já existente no candidato e na demanda. Não associa por símbolo, não reformata IDs e não transfere a moeda do candidato para a moeda solicitada. Vários IDs observados permanecem como múltiplas alegações, sem escolher uma fonte. O provedor pode estar ausente: não é inventado. A origem `DOMAIN_METADATA_PLUS_PROVIDER_SYMBOL`, quando presente, é exibida para deixar claro que a identidade observacional não equivale a um vínculo confirmado.

O botão copia apenas o ID observado para um campo vazio. Não sobrescreve edição manual, não preenche evidência, não marca confirmação e não verifica a moeda ou a identidade. A revisão continua exigindo conferir instrumento, provedor, ID e moeda na fonte. A pista local não é um atestado independente, evidência de compra numa corretora ou autorização financeira.

Os casos com identidade ausente no catálogo continuam bloqueados. O patch não registra automaticamente as 44 combinações pendentes nem altera classificações de BDR/ETF. A revisão dos seis criptoativos conhecidos pode avançar para os pares em BRL/EUR existentes na demanda, preservando posições antigas e seus IDs originais. Outras moedas são aceitas quando solicitadas pelo contexto financiado: não há lista fixa de moedas.

## Uso

O instalador gera uma nova pasta em Downloads com `REVISAO.html` e `FILA.json`, sem sobrescrever as anteriores. Abra o HTML, confira os casos e exporte `PORQUINHO_A24_CASOS_REVISADOS.json`. Selecionar uma confirmação é uma declaração local do revisor; a exportação não aplica nada. A nova ficha tem digest próprio: arquivos de revisão anteriores devem ser refeitos, não alterados para contornar a verificação.

Para preparar sem aplicar, continua disponível `prepare --review ARQUIVO --output ARQUIVO_NOVO_FORA_DO_PROJETO`.

Para aplicar os casos do arquivo que você conferiu e confirmou:

```bash
root="$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2"
"$root/.venv/bin/python" -I -B "$root/tools/review_funded_bindings_a24.py" --root "$root" apply-reviewed \
  --review "$HOME/Downloads/PORQUINHO_A24_CASOS_REVISADOS.json"
```

O comando acima grava vínculos de pesquisa, portanto só deve ser executado com os casos efetivamente revisados. Recalcula a fila atual, valida o digest da revisão e do registro, exige confirmação do dia em UTC e proíbe retroagir a vigência. O importador anterior verifica novamente o registro sob trava exclusiva, preserva todos os vínculos existentes, cria backup do arquivo anterior e substitui o registro atomicamente. Casos não selecionados não são aplicados. Alterações de registro ou fila impedem aplicar uma revisão antiga; a repetição do mesmo arquivo não cria duplicados e pode exigir uma nova ficha após uma aplicação bem-sucedida.

A aplicação não modifica observações históricas, não atribui retrospectivamente identidade às previsões, não consulta a rede e não autoriza execução. A capacidade real de coletar depende do adaptador e da moeda oferecida pelo provedor; o adaptador atualmente implementado é CoinGecko. O journal de novas cotações ainda não entra automaticamente no treinamento do laboratório. Vínculos de pesquisa não resolvem alias de identidades antigas da carteira nem certificam os modelos.

## Validação

405 testes Python aprovados com pandas 2.2.3 e 3.0.3; aplicação e repetição do instalador, baseline divergente recusado e sentinela de dados preservada. Testes novos cobrem IDs exatos em vez de símbolos, moedas solicitadas preservadas, múltiplas alegações, nenhuma fabricação de provider_id, caso não confirmado recusado, catálogo ausente bloqueado, aplicação de um caso, backup/preservação de vínculos anteriores e revisão obsoleta recusada. A ficha foi exercitada com JavaScript em Node/DOM simulado: copiar só altera ID vazio, edição manual e confirmação permanecem intactas, seleção vazia não exporta, e JSON confirmado retorna ao validador Python. Não substitui validação num navegador macOS ou de uma fonte real.

Nenhum dado privado integra a entrega pública. O relatório do instalador é de preparação da ficha, não de vínculos criados ou coleta bem-sucedida.
