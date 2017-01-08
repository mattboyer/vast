from unittest import TestCase, skip
from mock import patch, Mock, call

from src.metadata.IANA_IPv4_assignments import populate_IANA_IPv4_assignments
from src.metadata.IANA_IPv4_assignments import TopLevelDelegation
from src.metadata.assigned import AssignedSubnet
from src.net.IPv4 import Subnet, Address
from src.metadata.constants import reserved_networks

from src.metadata.resolver import (
    DelegationResolver,
    RDAPRedirectException,
    ResolutionException,
)

class test_AssignedSubnetResolver(TestCase):

    @patch('src.metadata.resolver.populate_IANA_IPv4_assignments')
    def setUp(self, mock_populate_IANA):
        # For our purposes, let's say that all tests use addresses within
        # 11.0.0.0/8
        eleven_dot = Subnet(Address('11.0.0.0'), 8)
        eleven_dot_delegation = TopLevelDelegation(11)
        eleven_dot_delegation.rdap_URLs = ['http://fake_rdap/']
        eleven_dot_delegation.whois_host = ['11.10.10.10']
        mock_populate_IANA.return_value = {eleven_dot: eleven_dot_delegation}
        self.resolver = DelegationResolver()

    def test_subnet_is_whole_address_space(self):
        whole_address_space = AssignedSubnet(Address('10.0.0.0'), 0)
        self.assertRaises(ResolutionException, self.resolver.validate_assignment, whole_address_space)

    def test_subnet_is_too_large(self):
        for prefix_len in range(1, 8):
            very_large_subnet = AssignedSubnet(Address('10.0.0.0'), prefix_len)
            self.assertRaises(ResolutionException, self.resolver.validate_assignment, very_large_subnet)

    def _reserved_subnets(self, subnet):
        self.resolver._rdap_resolver.resolve = Mock()
        resolved_assignment = self.resolver.resolve(subnet)
        self.assertTrue(resolved_assignment in reserved_networks)
        for reserved_net in reserved_networks:
            if reserved_net == resolved_assignment:
                break
        self.assertTrue(reserved_net is resolved_assignment)
        self.assertEquals([], self.resolver._rdap_resolver.resolve.mock_calls)

    def test_reserved_subnets_not_interactively_resolved(self):
        whole_ten_dot = Subnet(Address('10.0.0.0'), 8)
        self._reserved_subnets(whole_ten_dot)

        ten_dot_subset = Subnet(Address('10.11.12.0'), 24)
        self._reserved_subnets(ten_dot_subset)

    def test_RDAP_success_no_redirection(self):
        eleven_dot_unknown_size_subnet = Subnet(Address('11.12.13.0'), 32)
        eleven_dot_known_size_subnet = Subnet(Address('11.12.13.0'), 24)

        mock_reserved_resolver = Mock(return_value=None)
        self.resolver._resolve_reserved_networks = mock_reserved_resolver

        mock_rdap_resolver = Mock()
        mock_rdap_resolver.resolve = Mock(return_value=eleven_dot_known_size_subnet)
        self.resolver._rdap_resolver = mock_rdap_resolver

        resolved_assignment = self.resolver.resolve(eleven_dot_unknown_size_subnet)
        # The reserved subnet resovler is called once
        self.assertEquals(
            [call(eleven_dot_unknown_size_subnet)],
            mock_reserved_resolver.mock_calls
        )
        # The RDAP resolver is called once
        self.assertEquals(
            [call(eleven_dot_unknown_size_subnet)],
            mock_rdap_resolver.resolve.mock_calls
        )

    def test_RDAP_success_but_invalid_subnet(self):
        eleven_dot_unknown_size_subnet = Subnet(Address('11.12.13.0'), 32)
        eleven_dot_invalid_subnet = Subnet(Address('11.12.13.0'), 4)
        eleven_dot_valid_subnet = Subnet(Address('11.12.13.0'), 24)

        mock_reserved_resolver = Mock(return_value=None)
        self.resolver._resolve_reserved_networks = mock_reserved_resolver

        mock_rdap_resolver = Mock()
        mock_rdap_resolver.resolve = Mock(return_value=eleven_dot_invalid_subnet)
        self.resolver._rdap_resolver = mock_rdap_resolver

        mock_whois_resolver = Mock()
        mock_whois_resolver.resolve = Mock(return_value=eleven_dot_valid_subnet)
        self.resolver._whois_resolver = mock_whois_resolver

        resolved_assignment = self.resolver.resolve(eleven_dot_unknown_size_subnet)
        # The reserved subnet resovler is called once
        self.assertEquals(
            [call(eleven_dot_unknown_size_subnet)],
            mock_reserved_resolver.mock_calls
        )

        # The RDAP resolver is called once
        self.assertEquals(
            [call(eleven_dot_unknown_size_subnet)],
            mock_rdap_resolver.resolve.mock_calls
        )

        # The whois resolver is called once
        self.assertEquals(
            [call(eleven_dot_unknown_size_subnet, whois_host=None)],
            mock_whois_resolver.resolve.mock_calls
        )

        self.assertEquals(resolved_assignment, eleven_dot_valid_subnet)

    def test_RDAP_redirect_then_success(self):
        eleven_dot_unknown_size_subnet = Subnet(Address('11.12.13.0'), 32)
        eleven_dot_valid_subnet = Subnet(Address('11.12.13.0'), 24)

        mock_reserved_resolver = Mock(return_value=None)
        self.resolver._resolve_reserved_networks = mock_reserved_resolver

        # No provisional assignment can be resolved on the first call
        outcomes = [
            RDAPRedirectException(
                "The princess is in another castle",
                redir_url='http://other_fake_rdap/ip/11.12.13.0'
            ),
            eleven_dot_valid_subnet
        ]

        mock_rdap_resolve_from_url = Mock()
        mock_rdap_resolve_from_url.side_effect = outcomes
        self.resolver._rdap_resolver.resolve_from_url = mock_rdap_resolve_from_url

        mock_whois_resolver = Mock()
        mock_whois_resolver.resolve = Mock(return_value=eleven_dot_valid_subnet)
        self.resolver._whois_resolver = mock_whois_resolver

        resolved_assignment = self.resolver.resolve(eleven_dot_unknown_size_subnet)

        # The reserved subnet resolver is called once
        self.assertEquals(
            [call(eleven_dot_unknown_size_subnet)],
            mock_reserved_resolver.mock_calls
        )

        # The RDAP resolver is called twice
        self.assertEquals(
            [
                call('http://fake_rdap/ip/11.12.13.0'),
                call('http://other_fake_rdap/ip/11.12.13.0'),
            ],
            mock_rdap_resolve_from_url.mock_calls
        )

        # The whois resolver is never called
        self.assertEquals(
            [],
            mock_whois_resolver.resolve.mock_calls
        )

        self.assertEquals(resolved_assignment, eleven_dot_valid_subnet)
