# V53 — avaliação por referência explicitamente reconciliada

O cockpit agora pode valorar uma posição registrada quando existe uma cadeia revisada e válida entre sua identidade financeira e a fonte de pesquisa. A conta, moeda, identidade financeira, identidade de pesquisa, provedor e ID do provedor devem corresponder. Não há associação por ticker, banco ou moeda padrão.

O monitor usa o carregador existente que valida as confirmações de identidade, os vínculos de fonte e o registro atual de contas/portfólios. Sem essa evidência, a posição continua indisponível. Múltiplas fontes, cotações duplicadas, referências futuras e cotações anteriores à vigência não são selecionadas. A identidade financeira original permanece intacta, com a cadeia de referência separada no resultado.

Esses valores são referências de pesquisa, não preços de execução ou recomendações finais. O patch não escolhe um valor de realocação, não fabrica patrimônio histórico e não antecipa maturação. Patrimônio histórico e avaliação de referência atual continuam distintos.

## Instalação

Destino: `/Applications/Bridge_Companion/porquinho_v33_web_foundation-2`.

São alterados apenas `universal_portfolio/universal_cockpit_a24.py` e `universal_portfolio/monitor_consolidation_a24.py`. O instalador verifica as bases esperadas antes das alterações, preserva backup e recusa bases divergentes. Não reinicia serviços, solicita atualização de mercado, instala dependências ou altera dados/modelos/histórico. Repetir com os arquivos já aplicados é idempotente.

Após aplicar, aguarde o ciclo corrente terminar e reinicie apenas o Porquinho pelo inicializador em Applications. O Bridge não precisa ser reiniciado. A confirmação em dados reais do Mac é posterior à instalação.

## Validação no ambiente de desenvolvimento

- Suíte de release: 1.358 testes Python, sem falhas ou skips; 290 verificações JavaScript.
- 14 testes novos com identidades/moedas fictícias: referência explícita, separação de conta/moeda/provedor/instrumento, ambiguidade, vigência/timestamp, preservação de identidade e ausência de mutações/autoridade financeira.
- Instalador: aplicação, repetição, backup exato, preservação de sentinelas de histórico/modelo e recusa de base divergente antes de editar qualquer arquivo.
- Descoberta ampliada de testes legados: 4.092 testes após a mudança versus 4.078 antes; ambas registraram as mesmas 53 falhas e 259 erros. Os conjuntos de testes com erro/falha foram idênticos. A bateria ampliada não está integralmente verde; não há nova falha nesse comparativo.

A entrega contém apenas código e testes sintéticos, sem diagnósticos, contas ou registros financeiros do usuário.
