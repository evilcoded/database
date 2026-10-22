import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from universal_portfolio.brapi_connectivity_probe_a24 import probe,request

class ProbeTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name)
  self.row={'instrument_id':'BR:B3:EQUITY:NEW3','market':'B3','symbol':'NEW3','currency':'BRL','asset_class':'EQUITY'}
  self.write([self.row])
 def write(self,rows):
  p=self.root/'data/universal_instrument_catalog.json';p.parent.mkdir(exist_ok=True);p.write_text(json.dumps({'instruments':rows}))
 def response(self,**kw):return {'results':[{'symbol':'NEW3','currency':'BRL','regularMarketPrice':10,**kw}]}
 def test_success_and_explicit_secret(self):
  calls=[]
  def get(i,s):calls.append((i,s));return self.response()
  self.assertEqual(probe(self.root,'SECRET',transport=get),('CONNECTED_SINGLE_QUOTE',True));self.assertEqual(calls,[('NEW3','SECRET')])
 def test_no_catalog_does_not_use_seed(self):
  self.write([])
  with patch('universal_portfolio.brapi_connectivity_probe_a24.request') as get:
   self.assertEqual(probe(self.root,'S')[0],'PROBE_INSTRUMENT_REQUIRED');get.assert_not_called()
 def test_currency_mismatch(self):self.assertEqual(probe(self.root,'S',transport=lambda *a:self.response(currency='USD'))[0],'PROVIDER_QUOTE_CURRENCY_MISMATCH')
 def test_bad_prices(self):
  for p in [None,True,float('nan'),-1,0]:self.assertFalse(probe(self.root,'S',transport=lambda *a:self.response(regularMarketPrice=p))[1])
 def test_duplicates(self):self.assertFalse(probe(self.root,'S',transport=lambda *a:{'results':self.response()['results']*2})[1])
 def test_error_classification(self):
  for code,want in [('401','PROVIDER_AUTH_OR_COVERAGE_REJECTED'),('403','PROVIDER_AUTH_OR_COVERAGE_REJECTED'),('429','RATE_LIMITED')]:
   def get(*a):raise RuntimeError('PROVIDER_HTTP_'+code)
   self.assertEqual(probe(self.root,'S',transport=get),(want,False))
 def test_exception_secret_not_exposed(self):
  def get(*a):raise RuntimeError('SECRET')
  self.assertEqual(probe(self.root,'SECRET',transport=get),('PROVIDER_RESPONSE_REJECTED',False))
 def test_no_writes(self):
  before={str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
  probe(self.root,'S',transport=lambda *a:self.response())
  self.assertEqual(before,{str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
 def test_request_header_no_query_secret(self):
  class Response:
   headers={'Content-Type':'application/json'}
   def __enter__(self):return self
   def __exit__(self,*a):pass
   def read(self,*a):return b'{"results":[]}'
  with patch('universal_portfolio.brapi_connectivity_probe_a24.build_opener') as make:
   make.return_value.open.return_value=Response();request('NEW3','SECRET')
   req=make.return_value.open.call_args.args[0]
   self.assertEqual(req.get_header('Authorization'),'Bearer SECRET');self.assertNotIn('SECRET',req.full_url)

class WiringTests(unittest.TestCase):
 def test_brapi_dispatch_and_root(self):
  import importlib.util,sys,types
  import universal_portfolio
  path=Path(universal_portfolio.__file__).parent/'provider_connectivity.py'
  stub=types.ModuleType('universal_portfolio.provider_credentials');stub.resolve_provider_secret=lambda *a,**kw:'SECRET'
  with patch.dict(sys.modules,{'universal_portfolio.provider_credentials':stub}):
   spec=importlib.util.spec_from_file_location('universal_portfolio._probe_test',path);m=importlib.util.module_from_spec(spec)
   with patch.dict(sys.modules,{spec.name:m}):spec.loader.exec_module(m)
  provider=types.SimpleNamespace(adapter='BRAPI',provider_id='brapi',auth_method='BEARER',env_fallback='BRAPI_TOKEN')
  with patch('universal_portfolio.brapi_connectivity_probe_a24.probe',return_value=('CONNECTED_SINGLE_QUOTE',True)) as probe_mock:
   result=m.test_provider(provider,root=Path('/tmp/fixture'))
   self.assertTrue(result.ok);probe_mock.assert_called_once_with(Path('/tmp/fixture'),'SECRET')
  m.resolve_provider_secret=lambda *a,**kw:''
  self.assertEqual(m.test_provider(provider).status,'CREDENTIAL_NOT_CONFIGURED')
  def fail(*a,**kw):raise RuntimeError('SECRET')
  m.resolve_provider_secret=fail
  self.assertEqual(m.test_provider(provider).status,'CREDENTIAL_READ_FAILED')
