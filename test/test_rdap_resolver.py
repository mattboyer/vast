from mock import patch, Mock, call
from unittest import TestCase

from src.net.IPv4 import Address, Subnet
from src.metadata.assigned import AssignedSubnet
from src.metadata.RDAP import RDAP_Resolver, RDAPResolutionException, RDAPRedirectException

class test_RDAP_resolver(TestCase):
    TEST_URI = 'http://example.org/foo'
    TEST_REDIR_URI = 'http://example.com/foo'

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

    def test_raw_JSON_getter_404_on_second_try(self):
        first_response = Mock(status_code=500, is_redirect=False)
        first_response.json = Mock(return_value='WTF')

        second_response = Mock(status_code=404, is_redirect=False)
        second_response.json = Mock(return_value='{}')

        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(
            side_effect=[first_response, second_response]
        )

        with self.assertRaises(RDAPResolutionException) as ex:
            self.rslvr._get_raw_RDAP_JSON(self.TEST_URI)
        self.assertEquals(
            "RDAP resource not found: " + self.TEST_URI,
            str(ex.exception)
        )

        # We only called requests' get() twice
        self.assertEquals(
            # We never allow requests to handle redirects
            [
                call(self.TEST_URI, allow_redirects=False),
                call(self.TEST_URI, allow_redirects=False),
            ],
            self.rslvr._session.get.mock_calls
        )

    def test_raw_JSON_getter_malformed_on_second_try(self):
        first_response = Mock(status_code=500, is_redirect=False)
        first_response.json = Mock(return_value='WTF')

        second_response = Mock(status_code=200, is_redirect=False)
        second_response.json = Mock(side_effect=ValueError)

        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(
            side_effect=[first_response, second_response]
        )

        with self.assertRaises(RDAPResolutionException) as ex:
            self.rslvr._get_raw_RDAP_JSON(self.TEST_URI)
        self.assertEquals(
            "Malformed JSON in RDAP output",
            str(ex.exception)
        )

        # We only called requests' get() twice
        self.assertEquals(
            # We never allow requests to handle redirects
            [
                call(self.TEST_URI, allow_redirects=False),
                call(self.TEST_URI, allow_redirects=False),
            ],
            self.rslvr._session.get.mock_calls
        )

    def test_raw_JSON_getter_bad_request_on_second_try(self):
        first_response = Mock(status_code=500, is_redirect=False)
        first_response.json = Mock(return_value='WTF')

        second_response = Mock(status_code=400, is_redirect=False)
        second_response.json = Mock(return_value='WTF')

        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(
            side_effect=[first_response, second_response]
        )

        with self.assertRaises(RDAPResolutionException) as ex:
            self.rslvr._get_raw_RDAP_JSON(self.TEST_URI)
        self.assertEquals(
            "RDAP request returned 400",
            str(ex.exception)
        )

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
            side_effect=self.rslvr.GET_RETRIES * [bad_response]
        )

        with self.assertRaises(RDAPResolutionException) as ex:
            redir_url, json = self.rslvr._get_raw_RDAP_JSON(self.TEST_URI)
        self.assertEquals(
                "Out of retries for RDAP resource: " + self.TEST_URI,
            str(ex.exception)
        )

        self.assertEquals(
            # We never allow requests to handle redirects
            self.rslvr.GET_RETRIES * [call(self.TEST_URI, allow_redirects=False),],
            self.rslvr._session.get.mock_calls
        )

    def test_raw_JSON_getter_out_of_retries_accidental_valid_JSON(self):
        bad_response = Mock(status_code=500, is_redirect=False)
        # What if we accidentally have valid JSON in the 500 response body?
        bad_response.json = Mock(return_value='{}')

        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(
            side_effect=self.rslvr.GET_RETRIES * [bad_response]
        )

        with self.assertRaises(RDAPResolutionException) as ex:
            redir_url, json = self.rslvr._get_raw_RDAP_JSON(self.TEST_URI)
        self.assertEquals(
            "Out of retries for RDAP resource: " + self.TEST_URI,
            str(ex.exception)
        )

        self.assertEquals(
            # We never allow requests to handle redirects
            self.rslvr.GET_RETRIES * [call(self.TEST_URI, allow_redirects=False),],
            self.rslvr._session.get.mock_calls
        )

    def test_raw_JSON_getter_redirect_on_first_try(self):
        response = Mock(status_code=200, is_redirect=True)
        response.headers = {'Location': self.TEST_REDIR_URI}
        response.json = Mock(return_value='{}')

        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(return_value=response)
        redir_url, json = self.rslvr._get_raw_RDAP_JSON(self.TEST_URI)

        self.assertEquals(self.TEST_REDIR_URI, redir_url)
        self.assertEquals(json, '{}')

        # We only called requests' get() the once
        self.assertEquals(
            # We never allow requests to handle redirects
            [call(self.TEST_URI, allow_redirects=False)],
            self.rslvr._session.get.mock_calls
        )

    def test_raw_JSON_getter_redirect_on_second_try(self):
        first_response = Mock(status_code=500, is_redirect=False)
        first_response.json = Mock(return_value='WTF')
        #
        second_response = Mock(status_code=200, is_redirect=True)
        second_response.headers = {'Location': self.TEST_REDIR_URI}
        second_response.json = Mock(return_value='{}')

        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(
            side_effect=[first_response, second_response]
        )

        redir_url, json = self.rslvr._get_raw_RDAP_JSON(self.TEST_URI)

        self.assertEquals(self.TEST_REDIR_URI, redir_url)
        self.assertEquals(json, '{}')

        # We only called requests' get() the once
        self.assertEquals(
            # We never allow requests to handle redirects, therefore there are
            # NO calls to the redirected URI
            [
                call(self.TEST_URI, allow_redirects=False),
                call(self.TEST_URI, allow_redirects=False),
            ],
            self.rslvr._session.get.mock_calls
        )

    ########

    def test_resolve_from_url_success_no_redirection(self):
        response = Mock(status_code=200, is_redirect=False)
        response.json = Mock(return_value={
            'startAddress': '10.0.0.0',
            'endAddress': '10.255.255.255',
            'name': 'foo',
        })
        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(return_value=response)

        assigned_subnet = self.rslvr.resolve_from_url(self.TEST_URI)
        self.assertTrue(isinstance(assigned_subnet, AssignedSubnet))
        self.assertEquals("foo", assigned_subnet.name)
        self.assertEquals(Address((10, 0, 0, 0)), assigned_subnet._network)
        self.assertEquals(8, assigned_subnet._prefix_length)

    def test_resolve_from_url_failure_no_redirection(self):
        response = Mock(status_code=500, is_redirect=False)
        response.json = Mock(side_effect=ValueError)
        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(return_value=response)

        with self.assertRaises(RDAPResolutionException) as ex:
            self.rslvr.resolve_from_url(self.TEST_URI)
        self.assertEquals(
            "Out of retries for RDAP resource: " + self.TEST_URI,
            str(ex.exception)
        )

    def test_resolve_from_url_empty_redirect_then_success(self):
        # Here we're the testing the case where the initial URL yields a
        # redirect URL and *no* valid RDAP JSON object for an assigned subnet
        # i.e. the easy case where there's no need to decide which of several
        # valid RDAP JSON objects is the one we want to trust.
        redir_response = Mock(status_code=301, is_redirect=True)
        redir_response.headers = {'Location': self.TEST_REDIR_URI}
        redir_response.json = Mock(side_effect=ValueError)
        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(return_value=redir_response)

        with self.assertRaises(RDAPRedirectException) as redir_ex:
            assigned_subnet = self.rslvr.resolve_from_url(self.TEST_URI)
        self.assertEquals(
            "Redirection to {0}. No provisional assignment for {1}".format(self.TEST_REDIR_URI, self.TEST_URI),
            str(redir_ex.exception)
        )

    def test_resolve_from_url_success_plus_redirect_then_success(self):
        # Here we're the ambiguous case where the initial URL yields a redirect
        # URL *as well as* a valid RDAP JSON object for an assigned subnet
        # In this case, the caller will have to Do The Right Thing
        redir_response = Mock(status_code=301, is_redirect=True)
        redir_response.headers = {'Location': self.TEST_REDIR_URI}
        redir_response.json = Mock(return_value={
            'startAddress': '10.0.0.0',
            'endAddress': '10.255.255.255',
            'name': 'foo',
        })
        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(return_value=redir_response)

        expected_provisional_assigned_subnet = AssignedSubnet(
            Address((10, 0, 0, 0)), 8, "foo"
        )
        with self.assertRaises(RDAPRedirectException) as redir_ex:
            assigned_subnet = self.rslvr.resolve_from_url(self.TEST_URI)

        self.assertEquals(
            expected_provisional_assigned_subnet,
            redir_ex.exception.provisional
        )
        self.assertEquals(
            "Redirection to {0}. Provisional assignment: {1}".format(self.TEST_REDIR_URI, repr(expected_provisional_assigned_subnet)),
            str(redir_ex.exception)
        )
