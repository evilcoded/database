# Visibilidade do painel de análises — V81

O painel V80 havia sido incluído no dashboard V37, mas o dashboard V38 carregado depois substituía esse layout. Esta correção inclui o painel no layout efetivamente usado, preservado pelas extensões V40 e V41.

Quando a projeção não está disponível, o painel apresenta essa condição explicitamente. Ausência de dados não confirma ausência de oportunidades.

O instalador altera somente static/blue_experience_v38.js e static/experience_panels_v37.js, com verificação de base, backup e verificação dos arquivos finais. Não altera dados, modelos ou critérios do Brain. Após instalar, recarregue o navegador com Command+Shift+R; não é necessário reiniciar o servidor para esta correção JavaScript.

Validação: renderização da sequência completa V37–V41, painel único, estado indisponível, testes de escopo e regressões da interface; instalação repetida verificada.
