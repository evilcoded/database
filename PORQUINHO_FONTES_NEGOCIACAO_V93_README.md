# Correção da coleta de tarifas — V93

O V92 recusava toda URL com query, inclusive o endereço público CMS que a B3 usa para a tabela de Ações e Fundos de Investimento. Também pontuava a expressão a-vista nos caminhos ancestrais compartilhados por páginas de derivativos, priorizando produtos errados. O ZIP recebido trouxe sobretudo HFT e derivativos; suas tarifas não devem ser aplicadas a uma carteira comum de ações.

V93 preserva parâmetros públicos de navegação, rejeita credenciais e parâmetros aparentes de autenticação e usa principalmente o texto do link para identificar o produto. Exclui da descoberta páginas explicitamente de programas de incentivo, HFT, futuros/opções e balcão; trata-se do escopo desta coleta, não de uma restrição do universo do Porquinho. URLs exatas podem ser fornecidas como sementes sem dependência da pontuação.

Teste cobre links CMS, preservação da query, recusa de credenciais, prioridade de ações/fundos, exclusão de HFT/derivativos e descoberta de regras de cálculo. Mantém os limites de aquisição do V92 e não altera arquivos do Porquinho, Brain, modelos ou histórico, não extrai/aplica taxas e não exige reinício.
