# A24 — revisão local dos vínculos por instrumento e moeda

O patch adiciona uma ficha HTML offline para revisar os pares realmente solicitados pelo módulo de pesquisa financiada. Não preenche vínculos por ticker, país, moeda de conta ou colunas legadas. Nenhum provedor é consultado pela ficha ou pelo instalador.

## Instalação e histórico

O instalador exige as versões verificadas dos patches anteriores, testa 351 casos numa cópia temporária de fontes e adiciona apenas três arquivos novos. Cria backup/manifesto e recusa divergências. Não modifica snapshots, journals, mercado legado, modelos, dados de aprendizagem ou resultados maturados. Não reinicia serviços. Ao final exporta uma nova pasta privada em Downloads, sem sobrescrever fichas anteriores.

## Revisão

Abra `REVISAO.html` no caminho mostrado pelo instalador. Cada caso apresenta o ID original completo e a moeda solicitada, com a quantidade de contextos financiados que compartilham esse par. Nenhum saldo, conta ou valor de previsão é exportado. A ficha inclui casos ainda ausentes do catálogo de vínculos, mas eles não podem ser confirmados por esta ferramenta: exigem revisão separada, sem reformatação de IDs. Vínculos existentes são preservados e fontes ambíguas exigem escolha separada.

Para cada caso conhecido, confira instrumento, ID exato do provedor e moeda de cotação na fonte. Preencha provedor, ID, referência da evidência e responsável. O botão de data/hora registra o momento atual em UTC; não marque casos que não conferiu. Selecione a confirmação explícita e exporte o JSON dos casos revisados. Nenhuma linha vem pré-confirmada e o HTML usa apenas recursos locais, sem rede. A evidência é uma confirmação local do revisor, não um atestado independente ou prova de negociabilidade numa corretora.

## Preparar sem aplicar

A ferramenta abaixo compara a revisão com a demanda atual e o digest do registro, exige confirmação do dia UTC sem retroagir, preserva todos os vínculos existentes e cria um documento novo fora do projeto. Casos vazios, duplicados, alterados ou conflitantes são recusados. Substitua os caminhos pelos seus arquivos; não execute sem revisar.

```bash
root="$HOME/Desktop/Bridge_Companion/porquinho_v33_web_foundation-2"
"$root/.venv/bin/python" -I -B "$root/tools/review_funded_bindings_a24.py" --root "$root" prepare \
  --review "$HOME/Downloads/PORQUINHO_A24_CASOS_REVISADOS.json" \
  --output "$HOME/Downloads/PORQUINHO_A24_VINCULOS_PREPARADOS.json"
```

Isso não aplica vínculos. O documento preparado é compatível com o importador anterior `tools/market_provider_bindings_a24.py`, que exige `validate` e `apply` com os digests explícitos. Revisões de outro dia devem ser reconfirmadas. Se a demanda ou o registro mudar, gere uma nova ficha. Mesmo após aplicar, aquisição real exige o adaptador ativo no ciclo normal, fonte suportada e a moeda oferecida pelo provedor. Atualmente o adaptador implementado é CoinGecko; outros provedores ficam pendentes. Não existe autorização de compra, treinamento automático, FX ou publicação canônica.

## Verificação

351 testes Python aprovados com pandas 2.2.3 e 3.0.3. Instalador: aplicação, repetição idempotente, recusa de baseline divergente e preservação de arquivo sentinela. JavaScript da ficha exercitado em Node com DOM simulado: nenhuma seleção não exporta; caso preenchido e confirmado exporta decisões aceitas pelo preparador Python. Exportação real HTML/JSON exercitada sob o mesmo audit hook do instalador. Não foi realizada validação num navegador macOS nem com fontes externas reais.

## Correção V2 de compatibilidade macOS

Os testes resolvem o caminho temporário de /var para /private/var antes de exportar. A proteção de produção contra links simbólicos não foi alterada. Dois testes adicionais verificam exportação após resolução e recusa do link não resolvido. A suíte completa também passou com TMPDIR apontando para um alias por link simbólico no Linux; isso não substitui a execução no Mac. O instalador anterior que falhou na validação não aplicou fontes. Use o arquivo V2, que tem nome próprio e preserva o download anterior.
