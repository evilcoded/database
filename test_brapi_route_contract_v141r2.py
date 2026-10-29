"""Independent literal wire expectations from BRAPI's SDK contract, not join parity."""
import unittest
from unittest.mock import patch
from market_data import global_quote_transport_a24 as transport

class RouteContract(unittest.TestCase):
    def test_documented_multi_ticker_route_is_literal_comma_separated(self):
        self.assertEqual(transport.brapi_quote_url(['PETR4','VALE3']),
                         'https://brapi.dev/api/quote/PETR4,VALE3')
    def test_identifier_delimiters_are_escaped_before_join(self):
        self.assertEqual(transport.brapi_quote_url(['A,B','C;D','E/F']),
                         'https://brapi.dev/api/quote/A%2CB,C%3BD,E%2FF')
    def test_direct_adapter_rejects_multi_asset_request_before_network(self):
        with patch.object(transport,'get_json') as get:
            with self.assertRaisesRegex(ValueError,'BRAPI_SINGLE_ASSET_REQUEST_REQUIRED'):
                transport.fetch('brapi','BRL',['PETR4','VALE3'])
        get.assert_not_called()
    def test_direct_adapter_preserves_auth_and_native_currency_for_one_asset(self):
        body={'results':[{'symbol':'PETR4','currency':'BRL','regularMarketPrice':30}]}
        with patch.object(transport,'get_json',return_value=body) as get:
            rows=transport.fetch('brapi','BRL',['PETR4'])
        get.assert_called_once_with('https://brapi.dev/api/quote/PETR4',
                                    token_env='BRAPI_TOKEN',provider_id='brapi',timeout=10)
        self.assertEqual(rows[0]['currency'],'BRL')

if __name__=='__main__':unittest.main()
