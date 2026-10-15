# A24 — identidade, origem e cotação globais

Patch de continuidade, não encerramento da A24. Estado-base: fontes coletadas e preflight de 15/10/2026, após integração econômica e correção da captura prospectiva.

## Comportamento

- O laboratório preserva instrument_id somente quando informado, provider, provider_id, quote_currency e identity_source_ref. Símbolo não vira identidade canônica.
- Séries ficam separadas por identidade/origem/cotação; histórico sem vínculo continua separado, sem preenchimento retroativo. Referências transversais também ficam separadas por cotação e situação da unidade de preço.
- Aquisição diária aceita cotação explícita e valores neutros price/volume/market_cap. Cotação vem da requisição efetiva. Chamadas existentes mantêm o pedido EUR específico desse adaptador e aliases antigos; isso não define moeda-base global.
- Não configura provedores de outras classes, não muda a seleção automática do universo, não cria cadastro de identidades e não aciona o novo parâmetro global automaticamente. Integrações futuras devem fornecer os vínculos reais; não há dedução de instrumento por ticker.
- P35E e P35H preservam origem/cotação das novas previsões. quote_currency não preenche currency ou account_id. Chaves antigas e linhas antigas do journal permanecem intactas; chaves explícitas distinguem origem/cotação.
- O reconciliador legado ainda usa price_eur. Previsões com origem/cotação explícitas recebem BLOCKED_SOURCE_QUOTE_RECONCILIATION_REQUIRED, sem retorno realizado inventado. Próxima implementação deverá reconciliar pela mesma identidade, origem, cotação e observação.
- Tudo continua RESEARCH_ONLY, NOT_VALIDATED, sem atestado independente, promoção, sizing certificado ou execução financeira.

## Maturação

O alvo existente do laboratório significa 30 observações futuras; não equivale aos ciclos canônicos de 30/60/90 dias. A regra de maturação estritamente anterior ao instante da previsão foi preservada. Uma série com novo vínculo não herda o histórico sem vínculo; pode precisar acumular observações suficientes.

## Instalador e verificação

Antes de gravar, o instalador verifica hashes exatos e executa 206 testes offline em cópia temporária de fontes. Dependências: Python 3.10+, NumPy, pandas e scikit-learn já usados pelo laboratório; prefere .venv/bin/python. Não instala pacotes no Mac.

Verificados no cloud: 206 testes; paridade das características e alvos do caminho legado na amostra sintética; compilação das fontes; aplicação e repetição idempotente do instalador (206 testes em cada execução); recusa de baseline divergente antes da alteração; preservação de arquivo sentinela de dados.

Testes novos: 20 casos, inclusive aquisição simulada → características → Ridge real em memória → journal temporário → contexto de proveniência, separação de moedas, conflitos de vínculo e proteção contra reconciliação incorreta. Os demais 186 testes exercitam os contratos econômicos/captura e evidência existentes.

Não foram coletados dados reais nem treinados modelos reais. Nenhum teste foi executado no Mac pelo assistente. O instalador altera cinco fontes, adiciona um adaptador e um arquivo de testes; cria backup .porquinho_a24_global_backup_*. Não inicia/reinicia serviços. A aplicação em execução só carrega o código após ativação planejada. O ativador anterior não verifica estes novos hashes; não deve ser usado como comprovação da ativação global.

O pacote inclui fontes, manifesto, diff e log de verificação para revisão. Não contém dados privados, credenciais ou modelos.

## Correção V2

A V1 falhou em validação temporária no Mac, antes de gravar o patch. A fixture convertia o inteiro interno do pandas supondo nanossegundos; com datetime64[us], 210 observações caíam no mesmo dia. Reproduzido no cloud. A V2 calcula os milissegundos do provedor pela data civil, independentemente da precisão interna, e testa explicitamente ns e us.

206 testes passaram tanto com pandas 2.2.3 quanto com pandas 3.0.3 (este instalado em diretório temporário isolado). O instalador V2 passou aplicação e repetição com 206 testes por execução, recusou baseline divergente e preservou o sentinela de dados. As seis fontes de aplicação são byte a byte iguais às da V1; apenas o teste e o contador/empacotamento mudaram. Não foi removida a rejeição de duplicatas reais.
