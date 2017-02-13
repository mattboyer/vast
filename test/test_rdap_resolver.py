from mock import patch, Mock, call
from unittest import TestCase

from src.net.IPv4 import Address, Subnet
from src.metadata.RDAP import RDAP_Resolver, RDAPResolutionException

class test_RDAP_resolver(TestCase):
    TEST_URI = 'http://example.org/foo'

    def setUp(self):
        self._delegation_rslvr = Mock()
        self._delegation_rslvr.get_top_level_assignment = Mock(return_value=23)
        self.rslvr = RDAP_Resolver(self._delegation_rslvr)

    def test_raw_JSON_getter_success_on_first_try(self):
        response = Mock(status_code=200, is_redirect=False)
        response.json = Mock(return_value='{}')

        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(return_value=response)
        redir_url, json = self.rslvr._get_raw_RDAP_JSON(self.TEST_URI)

        self.assertIsNone(redir_url)
        self.assertEquals(json, '{}')

        # We only called requests' get() the once
        self.assertEquals(
            # We never allow requests to handle redirects
            [call(self.TEST_URI, allow_redirects=False)],
            self.rslvr._session.get.mock_calls
        )

    def test_raw_JSON_getter_404_on_first_try(self):
        response = Mock(status_code=404, is_redirect=False)

        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(return_value=response)
        with self.assertRaises(RDAPResolutionException) as ex:
            self.rslvr._get_raw_RDAP_JSON(self.TEST_URI)
        self.assertEquals(
            "RDAP resource not found: " + self.TEST_URI,
            str(ex.exception)
        )

        # We only called requests' get() the once
        self.assertEquals(
            # We never allow requests to handle redirects
            [call(self.TEST_URI, allow_redirects=False)],
            self.rslvr._session.get.mock_calls
        )

    def test_raw_JSON_getter_400_on_first_try(self):
        response = Mock(status_code=400, is_redirect=False)

        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(return_value=response)
        with self.assertRaises(RDAPResolutionException) as ex:
            self.rslvr._get_raw_RDAP_JSON(self.TEST_URI)
        self.assertEquals(
            "RDAP request returned 400",
            str(ex.exception)
        )

        # We only called requests' get() the once
        self.assertEquals(
            # We never allow requests to handle redirects
            [call(self.TEST_URI, allow_redirects=False)],
            self.rslvr._session.get.mock_calls
        )

    def test_raw_JSON_getter_malformed_JSON_on_first_try(self):
        response = Mock(status_code=200, is_redirect=False)
        response.json = Mock(side_effect=ValueError)

        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(return_value=response)
        with self.assertRaises(RDAPResolutionException) as ex:
            self.rslvr._get_raw_RDAP_JSON(self.TEST_URI)
        self.assertEquals(
            "Malformed JSON in RDAP output",
            str(ex.exception)
        )

        # We only called requests' get() the once
        self.assertEquals(
            # We never allow requests to handle redirects
            [call(self.TEST_URI, allow_redirects=False)],
            self.rslvr._session.get.mock_calls
        )

    def test_raw_JSON_getter_success_on_second_try(self):
        first_response = Mock(status_code=500, is_redirect=False)
        first_response.json = Mock(return_value='WTF')

        second_response = Mock(status_code=200, is_redirect=False)
        second_response.json = Mock(return_value='{}')

        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(
            side_effect=[first_response, second_response]
        )
        redir_url, json = self.rslvr._get_raw_RDAP_JSON(self.TEST_URI)

        self.assertIsNone(redir_url)
        self.assertEquals(json, '{}')

        # We only called requests' get() twice
        self.assertEquals(
            # We never allow requests to handle redirects
            [
                call(self.TEST_URI, allow_redirects=False),
                call(self.TEST_URI, allow_redirects=False),
            ],
            self.rslvr._session.get.mock_calls
        )

    def test_raw_JSON_getter_out_of_retries(self):
        bad_response = Mock(status_code=500, is_redirect=False)
        # What if we accidentally have valid JSON in the 500 response body?
        bad_response.json = Mock(side_effect=RDAPResolutionException)

        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(
            side_effect=10 * [bad_response]
        )

        with self.assertRaises(RDAPResolutionException) as ex:
            redir_url, json = self.rslvr._get_raw_RDAP_JSON(self.TEST_URI)
        self.assertEquals(
                "Out of retries for RDAP resource: " + self.TEST_URI,
            str(ex.exception)
        )

        self.assertEquals(
            # We never allow requests to handle redirects
            10 * [call(self.TEST_URI, allow_redirects=False),],
            self.rslvr._session.get.mock_calls
        )

    def test_raw_JSON_getter_out_of_retries_accidental_valid_JSON(self):
        bad_response = Mock(status_code=500, is_redirect=False)
        # What if we accidentally have valid JSON in the 500 response body?
        bad_response.json = Mock(return_value='{}')

        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(
            side_effect=10 * [bad_response]
        )

        with self.assertRaises(RDAPResolutionException) as ex:
            redir_url, json = self.rslvr._get_raw_RDAP_JSON(self.TEST_URI)
        self.assertEquals(
            "Out of retries for RDAP resource: " + self.TEST_URI,
            str(ex.exception)
        )

        self.assertEquals(
            # We never allow requests to handle redirects
            10 * [call(self.TEST_URI, allow_redirects=False),],
            self.rslvr._session.get.mock_calls
        )
