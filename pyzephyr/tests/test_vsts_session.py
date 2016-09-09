import json
import time

import requests
import unittest
from unittest.mock import patch, MagicMock
import httpretty


from pyzephyr.session.zephyr_session import ZephyrSession
from pyzephyr.config.config import ZephyrConfig

fake_time = time.time()


class VSTSSessionTest(unittest.TestCase):
    def setUp(self):
        self.fake_creds = json.loads(' \
            { \
                "zephyr2": \
                    { \
                        "client_id": "fakeid", \
                        "client_secret": "password" \
                    } \
                }'
            )

        self.fake_endpoint = json.loads(' \
            { \
                "scheme": "https", \
                "netloc": "fake_it.com", \
                "odata": "/DefaultCollection/_odata" \
                }'
            )

    def test_create_new(self):
        zephyr_session = ZephyrSession(endpoint=self.fake_endpoint, creds=self.fake_creds)
        self.assertIsInstance(zephyr_session, ZephyrSession)

    def test_create_from_serialized(self):
        serializable = {'creds':self.fake_creds, 'endpoint':self.fake_endpoint}
        from_serialized = ZephyrSession(**serializable)
        self.assertIsInstance(from_serialized, ZephyrSession)

    def test_serialized(self):
        zephyr_session = ZephyrSession(endpoint=self.fake_endpoint, creds=self.fake_creds)
        serialized = zephyr_session.serialize()
        from_serialized = ZephyrSession(**serialized)

        self.assertIsInstance(from_serialized, ZephyrSession)
        self.assertEqual(zephyr_session.__repr__(), from_serialized.__repr__())

    # @httpretty.activate
    # def test_request_returning_ok(self):
    #
    #     httpretty.register_uri(httpretty.GET,'https://tfs-glo-lexisadvance.analytics.visualstudio.com/')
    #
    #     lexis = ZephyrSession(client_id=self.client_id, zephyr_session=self.fake_endpoint, redirect_url=self.redirect_url)
    #
    #     #mock the superordinate request function
    #     with patch('pylexis.session.lexis_session.requests.Session.request') as m:
    #         m.configure_mock(return_value=expected_response)
    #         lexis.request('GET', self.token_url, data=fake_body, headers=fake_headers)
    #
    #     m.assert_called_once_with('GET',
    #                               self.token_url,
    #                               data=fake_body,
    #                               headers=fake_headers)
