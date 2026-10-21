Recuperação do pacote market_data em Applications

Restaura nove arquivos de código necessários aos endpoints de macro, radar e inteligência de renda fixa. Destino: /Applications/Bridge_Companion/porquinho_v33_web_foundation-2.

Cria backup dos arquivos substituídos; aceita somente arquivos ausentes, idênticos ou versões anteriores reconhecidas. Uma versão divergente cancela a aplicação antes das alterações. Não inicia serviços nem modifica dados financeiros, modelos ou histórico. O pacote existente pode atualizar seus caches durante o uso normal dos endpoints.

Os arquivos static/data/asset_registry_v365.json e static/data/portfolio_br_v365.json são dependências de dados legadas: o instalador informa se estão ausentes, sem criar conteúdo substituto.

Verificação local: instalação sobre pacote parcial, repetição idempotente, backup, preservação de sentinelas de dados/modelos, recusa de fonte divergente e importação dos provedores. Testes funcionais isolados usaram credenciais e provedores simulados, sem validar autenticação ou conexão real com os provedores.

SHA256 do instalador: 60c2beaa891b488cbd2fad3abeb599661551a1a9b9d7c930e457144ab0619ddf
