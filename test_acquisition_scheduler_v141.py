import ast,types,unittest,os
from pathlib import Path
from unittest.mock import Mock
ROOT=Path(os.environ.get('PORQUINHO_PROJECT','/workspace/porquinho-a24/project'))
class Scheduler(unittest.TestCase):
    def assignment(self):
        tree=ast.parse((ROOT/'webapp/server.py').read_text());refresh=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_refresh')
        node=next(n for n in ast.walk(refresh) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Subscript) and isinstance(t.value,ast.Name) and t.value.id=='universal_shadow' and isinstance(t.slice,ast.Constant) and t.slice.value=='funded_currency_acquisition' for t in n.targets))
        return compile(ast.Module(body=[node],type_ignores=[]),'scheduler','exec')
    def test_precollected_reference_results_are_reused_without_another_provider_call(self):
        collect=Mock();existing={'status':'REFERENCES_REFRESHED'};out={}
        exec(self.assignment(),{'ROOT':ROOT,'_a138_operational':{'quote_acquisition':existing},'universal_shadow':out,'_a24_collect_quotes':collect})
        collect.assert_not_called();self.assertIs(out['funded_currency_acquisition'],existing)
    def test_fallback_uses_the_existing_exact_demand(self):
        demand={'schema':'existing-demand'};collect=Mock(return_value={'status':'FALLBACK_COMPLETE'});out={}
        exec(self.assignment(),{'ROOT':ROOT,'_a138_operational':{},'universal_shadow':out,'_a24_collect_quotes':collect,'_a24_input_bridge':types.SimpleNamespace(intelligence={'funded_currency_research':demand})})
        collect.assert_called_once_with(ROOT,demand);self.assertEqual(out['funded_currency_acquisition']['status'],'FALLBACK_COMPLETE')
if __name__=='__main__':unittest.main()
