from mock import patch, Mock, call
from unittest import TestCase

from src.net.IPv4 import Address, Subnet
from src.metadata.assigned import AssignedSubnet
from src.metadata.whois import Whois_Resolver

class test_whois_resolver(TestCase):
    WHOIS_HOST = 'whois.example.org'

    def setUp(self):
        self._delegation_rslvr = Mock()
        self._delegation_rslvr.get_top_level_assignment = Mock(
            return_value=Mock(rdap_URLs={self.WHOIS_HOST}),
        )
        self.rslvr = Whois_Resolver(self._delegation_rslvr)
        self._name_resolution_patch = patch(
            'src.metadata.whois.getaddrinfo',
            return_value=[
                (None, None, None, None, ('192.168.42.42', 43)),
            ]
        )
        self._name_resolution_patch.start()
        #
        self._mock_socket_object = Mock()
        # TODO test exception raised by call to connect()
        #
        mock_socket_ctx_mgr = Mock()
        mock_socket_ctx_mgr.__enter__ = Mock(return_value=self._mock_socket_object)
        mock_socket_ctx_mgr.__exit__ = Mock()
        self._socket_context_patch = patch(
            'src.metadata.whois.socket',
            return_value=mock_socket_ctx_mgr,
        )
        # mock_tmp.return_value.__enter__.return_value.name = mytmpname
        self._socket_context_patch.start()

    def test_get_whois_entry_whois_supplied(self):
        addr = Subnet(Address("10.0.0.0"), 8)
        self._mock_socket_object.recv = Mock(side_effect=[b'raw_whois', b''])
        whois_response = self.rslvr.get_whois_entry(addr, self.WHOIS_HOST)

        self.assertTrue(isinstance(whois_response, str))
        self.assertEqual('raw_whois', whois_response)

    def test_get_whois_entry_multiple_reads(self):
        addr = Subnet(Address("10.0.0.0"), 8)
        self._mock_socket_object.recv = Mock(side_effect=[b'raw_whois', b'more_whois', b''])
        whois_response = self.rslvr.get_whois_entry(addr, self.WHOIS_HOST)

        self.assertTrue(isinstance(whois_response, str))
        self.assertEqual('raw_whoismore_whois', whois_response)

    def test_get_whois_entry_no_whois_supplied(self):
        addr = Subnet(Address("10.11.12.0"), 24)
        self._mock_socket_object.recv = Mock(side_effect=[b'raw_whois', b''])
        whois_response = self.rslvr.get_whois_entry(addr)

        self.assertTrue(isinstance(whois_response, str))
        self.assertEqual('raw_whois', whois_response)

        self.assertEqual(
            [call(Subnet(Address("10.0.0.0"), 8))],
            self._delegation_rslvr.get_top_level_assignment.mock_calls
        )
