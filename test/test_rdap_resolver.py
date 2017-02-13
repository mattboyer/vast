from mock import patch, Mock, call
from unittest import TestCase

from src.net.IPv4 import Address, Subnet
from src.metadata.RDAP import RDAP_Resolver
from src.metadata.resolver import DelegationResolver

class test_RDAP_resolver(TestCase):

    def setUp(self):
        self._delegation_rslvr = Mock()
        self._delegation_rslvr.get_top_level_assignment = Mock(return_value=23)
        self.rslvr = RDAP_Resolver(self._delegation_rslvr)

    def test_raw_JSON_getter_success_on_first_try(self):
        response = Mock(status_code=200, is_redirect=False)
        response.json = Mock(return_value='{}')

        self.rslvr._session = Mock()
        self.rslvr._session.get = Mock(return_value=response)
        self.rslvr._get_raw_RDAP_JSON('http://example.org/foo')
