"""Public CMS URLs are data, not credentials; product label must guide discovery."""
from pathlib import Path
import unittest,sys
SOURCE=Path(__file__).with_name('PORQUINHO_FONTES_NEGOCIACAO_V93.command').read_text().split("<<'PY'\n",1)[1].rsplit('\nPY',1)[0]
import ast
parsed=ast.parse(SOURCE)
keep=[n for n in parsed.body if isinstance(n,(ast.Import,ast.ImportFrom)) or isinstance(n,ast.FunctionDef) and n.name in ('clean','priority')]
namespace={};exec(compile(ast.Module(body=keep,type_ignores=[]),'collector-functions','exec'),namespace)
class Discovery(unittest.TestCase):
 def test_public_cms_query_preserved(self):
  url='https://example.test/main.jsp?lumPageId=PUBLIC_PAGE&lumChannelId=PUBLIC_CHANNEL';self.assertEqual(namespace['clean'](url),url)
 def test_credentials_and_tokens_refused(self):
  for url in ('https://user:password@example.test/','https://example.test/?token=secret','https://example.test/?api_key=secret','http://example.test/'):
   self.assertIsNone(namespace['clean'](url))
 def test_product_label_not_ancestor_path(self):
  score=namespace['priority']('https://example.test/main.jsp?lumPageId=public','Ações e Fundos de Investimento');self.assertGreater(score,0)
  self.assertEqual(namespace['priority']('https://example.test/tarifas/listados-a-vista-e-derivativos/renda-variavel/futuro-merval/','Índice Merval'),0)
  self.assertEqual(namespace['priority']('https://example.test/programas-de-incentivo/hft/','Programa HFT de Mercado a Vista de Renda Variável'),0)
 def test_calculation_rules_can_follow(self):self.assertGreater(namespace['priority']('https://example.test/main.jsp?id=public','Regras de Cálculo'),0)
 def test_rejecting_query_does_not_strip_it_and_fetch_wrong_page(self):self.assertIsNone(namespace['clean']('https://example.test/page?session=secret'))
if __name__=='__main__':unittest.main()
