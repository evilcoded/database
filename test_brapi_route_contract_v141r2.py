"""Independent literal wire expectations from BRAPI's SDK contract, not join parity."""
import unittest
from unittest.mock import patch
from market_data import global_quote_transport_a24 as transport
from test_brapi_native_references_v141 import References

class RouteContract(unittest.TestCase):
    def test_documented_multi_ticker_route_is_literal_comma_separated(self):
        self.assertEqual(transport.brapi_quote_url(['PETR4','VALE3']),
                         'https://brapi.dev/api/quote/PETR4,VALE3')
    def test_identifier_delimiters_are_escaped_before_join(self):
        self.assertEqual(transport.brapi_quote_url(['A,B','C;D','E/F']),
                         'https://brapi.dev/api/quote/A%2CB,C%3BD,E%2FF')
    def test_radar_uses_documented_route_without_touching_auth_or_currency(self):
        body={'results':[{'symbol':'PETR4','currency':'BRL','regularMarketPrice':30}]}
        with patch.object(transport,'get_json',return_value=body) as get:
            rows=transport.fetch('brapi','BRL',['PETR4','VALE3'])
        get.assert_called_once_with('https://brapi.dev/api/quote/PETR4,VALE3',
                                    token_env='BRAPI_TOKEN',provider_id='brapi',timeout=10)
        self.assertEqual(rows[0]['currency'],'BRL')
    def test_old_separator_reproduces_404_and_real_collector_uses_correct_contract(self):
        fixture=References();fixture.setUp();self.addCleanup(fixture.doCleanups)
        def provider(url,**kw):
            # A literal protocol expectation, deliberately no split/join of
            # the implementation's delimiter to construct the expected URL.
            expected='https://brapi.dev/api/quote/T0,T1,T2,T3,T4,T5,T6,T7,T8'
            if url!=expected:raise RuntimeError('PROVIDER_HTTP_404')
            return {'results':[{'symbol':'T'+str(i),'currency':'BRL',
                    'regularMarketPrice':100,'regularMarketTime':int(fixture.NOW.timestamp())}
                    for i in range(9)]}
        # NOW lives in the module, not on the fixture instance.
        from test_brapi_native_references_v141 import NOW
        fixture.NOW=NOW
        with self.assertRaisesRegex(RuntimeError,'PROVIDER_HTTP_404'):
            provider('https://brapi.dev/api/quote/T0;T1;T2;T3;T4;T5;T6;T7;T8')
        result=fixture.collect(fetch=provider)
        self.assertEqual(result['current_references_refreshed'],9,result)
        self.assertEqual(result['network_requests'],1,result)

if __name__=='__main__':unittest.main()
