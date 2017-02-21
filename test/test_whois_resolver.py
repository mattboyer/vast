from mock import patch, Mock, call
from unittest import TestCase

from src.net.IPv4 import Address, Subnet
from src.metadata.assigned import AssignedSubnet
from src.metadata.whois import Whois_Resolver
from src.metadata import ResolutionException

class test_whois_resolver(TestCase):
    WHOIS_HOST = 'whois.example.org'

    def setUp(self):
        self._delegation_rslvr = Mock()
        self._delegation_rslvr.get_top_level_assignment = Mock(
            return_value=Mock(whois_host=self.WHOIS_HOST),
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

    def test_get_whois_entry_no_whois_supplied_no_whois_on_TLD(self):
        self._delegation_rslvr.get_top_level_assignment = Mock(
            return_value=Mock(whois_host=None),
        )

        addr = Subnet(Address("10.11.12.0"), 24)
        with self.assertRaises(ResolutionException) as ex:
            self.rslvr.get_whois_entry(addr)
        self.assertEqual("No whois host set on the top-level delegation", str(ex.exception))

    @patch('src.metadata.whois.Whois_Resolver.get_whois_entry')
    def test_resolve_malformed_whois(self, mock_get_entry):
        addr = Subnet(Address("10.0.0.0"), 8)
        mock_get_entry.return_value = 'foo'

        with self.assertRaises(ResolutionException) as ex:
            self.rslvr.resolve(addr, self.WHOIS_HOST)
        self.assertEqual("Malformed Whois entry: foo", str(ex.exception))

    @patch('src.metadata.whois.Whois_Resolver.get_whois_entry')
    def test_resolve_well_formed_whois(self, mock_get_entry):
        addr = Subnet(Address("45.0.0.0"), 8)
        mock_get_entry.return_value = '''
% This is the RIPE Database query service.
% The objects are in RPSL format.
%
% The RIPE Database is subject to Terms and Conditions.
% See http://www.ripe.net/db/support/db-terms-conditions.pdf

% Note: this output has been filtered.
%       To receive output for a database update, use the "-B" flag.

% Information related to '45.0.0.0 - 45.255.255.255'

% No abuse contact registered for 45.0.0.0 - 45.255.255.255

inetnum:        45.0.0.0 - 45.255.255.255
netname:        EU-ZZ-45
descr:          To determine the registration information for a more
descr:          specific range, please try a more specific query.
descr:          If you see this object as a result of a single IP query,
descr:          it means the IP address is currently in the free pool of
descr:          address space managed by the RIPE NCC.
                Bullshit continuation
country:        EU # Country is in fact world wide
admin-c:        IANA1-RIPE
tech-c:         IANA1-RIPE
status:         ALLOCATED UNSPECIFIED
mnt-by:         RIPE-NCC-HM-MNT
created:        2014-05-21T08:19:20Z
last-modified:  2015-09-23T13:18:33Z
source:         RIPE
        '''.strip()



        assigned = self.rslvr.resolve(addr, self.WHOIS_HOST)
        self.assertTrue(isinstance(assigned, AssignedSubnet))
        self.assertEqual(
            Address("45.0.0.0"),
            assigned._network
        )
        self.assertEqual(
            8,
            assigned._prefix_length
        )
        self.assertEqual(
            'EU-ZZ-45',
            assigned._name
        )

    @patch('src.metadata.whois.Whois_Resolver.get_whois_entry')
    def test_resolve_no_inetnum(self, mock_get_entry):
        addr = Subnet(Address("45.0.0.0"), 8)
        mock_get_entry.return_value = '''
netname:        EU-ZZ-45
descr:          To determine the registration information for a more
descr:          specific range, please try a more specific query.
descr:          If you see this object as a result of a single IP query,
descr:          it means the IP address is currently in the free pool of
descr:          address space managed by the RIPE NCC.
                Bullshit continuation
source:         RIPE
        '''.strip()

        with self.assertRaises(ResolutionException) as ex:
            self.rslvr.resolve(addr, self.WHOIS_HOST)
        self.assertEqual("No inetnum in whois record", str(ex.exception))

    @patch('src.metadata.whois.Whois_Resolver.get_whois_entry')
    def test_resolve_no_netname(self, mock_get_entry):
        addr = Subnet(Address("45.0.0.0"), 8)
        mock_get_entry.return_value = '''
inetnum:        45.0.0.0 - 45.255.255.255
descr:          To determine the registration information for a more
descr:          specific range, please try a more specific query.
descr:          If you see this object as a result of a single IP query,
descr:          it means the IP address is currently in the free pool of
descr:          address space managed by the RIPE NCC.
                Bullshit continuation
source:         RIPE
        '''.strip()

        with self.assertRaises(ResolutionException) as ex:
            self.rslvr.resolve(addr, self.WHOIS_HOST)
        self.assertEqual("No netname in whois record", str(ex.exception))
