# Rota de histórico V74

Corrige uma lacuna na ampliação do planejador: desde V72, as rotas BRAPI podem ser planejadas para captura diária. O coletor histórico anterior tinha transporte apenas CoinGecko e consumia a mesma lista sem filtrar provedor. Agora ele filtra explicitamente as rotas e informa HISTORICAL_PROVIDER_ADAPTER_NOT_IMPLEMENTED para BRAPI, sem construir uma requisição /coins/ com um ID BRAPI. O construtor de pacotes históricos também recusa provedor incompatível. Captura diária BRAPI e CoinGecko preservadas. Nenhum arquivo histórico anterior é apagado ou reescrito.

A inclusão de uma cotação diária BRAPI já alcança research_economic_series_a24: a série mantém instrumento, provedor, moeda e contagem de observações. A rotina global_research_lab_a24, contudo, lê pacotes históricos separados, não essa série diária diretamente. Este patch explicita essa lacuna sem alterar horizontes, modelos, aprendizado, regras de seleção ou validação. Não cria histórico BRAPI nem impõe uma nova espera de 30 dias.

Inclui tools/trace_brapi_research_v74.py, auditoria sem rede ou execução de modelos, que resume séries BRAPI, plano de histórico e último diagnóstico de captura em um ZIP de Downloads. Não exporta credenciais nem modelos. Rastreio não cria recomendações ou ordens.

69 testes de guarda de provedor, histórico existente, séries econômicas e captura BRAPI, com dados simulados. Backup, compilação e idempotência verificados. Reiniciar Porquinho após concluir ciclos para carregar a correção no servidor.
