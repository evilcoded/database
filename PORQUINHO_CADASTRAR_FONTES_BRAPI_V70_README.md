# Fontes BRAPI V70

Instala o verificador de rotas e um comando manual: `python tools/register_brapi_sources_v70.py --apply`. O instalador não consulta provedores nem modifica cadastros. O comando faz consultas à BRAPI e registra as rotas verificadas no cadastro existente, sem alterar vínculos anteriores.

A enumeração vem do catálogo global, sem tickers fixos. O adaptador BRAPI cobre o namespace B3 declarado; exige candidato único na listagem, classe declarada do provedor correspondente ao catálogo, mesmo símbolo na cotação, moeda explícita igual ao catálogo, preço positivo e data com fuso não futura e até sete dias. Sete dias é tolerância de verificação da rota (inclui mercado fechado), não certificação de preço atual. Não usa sufixo de ticker para classificar instrumentos, não corrige moeda ausente, não substitui tickers renomeados. O mapeamento stock/bdr/fund é contrato do adaptador, não política de investimento.

Esta é uma checagem automatizada local de rota, identificada assim no campo confirmed_by; não é atestação independente de emissor, ISIN, execução ou disponibilidade no banco. Preserva moedas, instrumentos e vínculos já existentes. Verifica novamente hashes dos cadastros, serializa alterações com lock, guarda evidência e backup e substitui o registro atomicamente. Idempotente. Tokens não entram no relatório. HTTP e erros operacionais são apresentados sem mensagens arbitrárias de exceção.

Não inicia treinamento, ordens, ciclos ou mudanças nos modelos e dados financeiros. O coletor de pesquisa financiada existente ainda aceita apenas CoinGecko; este patch registra fontes e habilita referências no radar, não resolve sozinho a integração das análises brasileiras nem publica recomendações. AAVE e renda fixa exigem os respectivos adaptadores.

Validação: 61 testes de checagem/registro de rotas, radar global, teste de conexão e vínculos explícitos. Rede simulada nos testes; a validação ao vivo ocorre no Mac, com sua credencial. O ZIP gerado em Downloads contém o resultado por instrumento e o número de vínculos efetivamente adicionados.
