# A24 — Intraday, Dashboard e acesso privado remoto (V40)

Corrige uma incompatibilidade entre o formato sem coluna source gravado pelo produtor normal e o leitor que só reconhecia o coletor histórico. O produtor normal precisa corresponder ao hash conhecido. Referências legadas EUR permanecem isoladas e não certificadas historicamente; moeda não é inferida pelo sufixo sozinho. Linhas ambíguas, futuras ou sem contexto permanecem excluídas, com contadores por motivo. Não reescreve ou reconstrói arquivos históricos.

Dashboard passa a ter esse nome e recebe intraday junto com Mercado Global, janelas 30/60 minutos, 6/24 horas, base100, fonte em popup e leitura da tela a cada 60 segundos enquanto visível. Horários efetivos das observações são preservados. A fonte existente pode gravar a cada10 minutos; atualizar a tela não cria novas cotações. Dados atrasados são identificados. Sem dados elegíveis não se inventa curva.

Cartão P/L10 minutos: diferença do P/L total armazenado em dois snapshots compatíveis, intervalo10min com tolerância2min. Exige último snapshot recente (até15min). Separa moeda/conta/escopo, não usa variação de patrimônio como lucro nem quantidades atuais para recalcular o passado. Sem amostras, informa indisponibilidade. Essa medida não é retorno ajustado por fluxos.

Campos, seletores, botões e painéis recebem o fundo azul mantendo a identidade visual. Brain, lógica financeira, modelos, memória, snapshots e journals não são alterados.

## Instalação

Requer V39 aplicado, Python3.10+, Node e dependências já utilizadas pelo projeto. O instalador verifica hashes, valida em cópia temporária de fontes, faz backup, aplica com rollback e confirma integridade. SHA256 deste instalador: `fad64a6166e31301543cc019b789cd00b269a3cc6e64fbd66b9896d5385ab3b3`.

Ativação controlada preserva Bridge8787 e recusa trabalhos ativos. Caso esteja ocupado, repita apenas `~/Downloads/PORQUINHO_A24_ATIVAR_CONSOLIDACAO_V40.command` após o ciclo normal. Atualize o navegador com Cmd+Shift+R. O relatório inclui contadores de descarte intraday; não exporta preços ou P/L individual.

## iPhone de qualquer rede

O instalador copia e abre o assistente `PORQUINHO_A24_PREPARAR_IPHONE_V40.command`. O guia privado detecta apenas o IP deste Mac e mantém as informações localmente. Instale/autentique Tailscale no Mac e iPhone na mesma rede privada; habilite Acesso Remoto do macOS para o usuário autorizado. Configure um cliente SSH iOS com encaminhamento local 127.0.0.1:8765 → Mac127.0.0.1:8765 usando o IP privado Tailscale do Mac como servidor SSH. Abra o loopback encaminhado no Safari. Não é necessário abrir portas no roteador. Não altera Host/Origin, sessão ou guards; não usa Funnel/Serve público. Mac deve ficar ligado, conectado e acordado. Cliente iOS deve manter o túnel ativo em segundo plano. Teste primeiro somente leitura usando dados móveis. Nenhuma conexão real do iPhone é certificada pelo assistente; a instalação/autenticação nos aparelhos depende do usuário.

## Validação

1126 testes Python +217 verificações JavaScript;38 testes simulados do ativador;Chromium com gráfico e P/L sintéticos, seletores, fundo azul, viewport390 sem overflow;instalador aplicado/repetido, backup único, divergência de baseline recusada e sentinelas de dados/resultados/modelos intactas. A ativação e os registros reais do Mac ainda precisam ser conferidos após execução. Não foi feita nova coleta, treino, refresh financeiro ou operação financeira pelos testes.
