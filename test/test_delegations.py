from unittest import TestCase
from mock import patch, Mock, call

from src.metadata.IANA_IPv4_assignments import TopLevelDelegation
from src.net.IPv4 import Subnet, Address

class test_Delegations(TestCase):

    def test_delegation_repr(self):
        deleg = TopLevelDelegation(10)
        deleg.rdap_URLs = ['http://example.org', 'https://example.com']

        s = Subnet(Address("10.0.0.0"), 8)
        self.assertEqual(
            "<TopLevelDelegation {0}: {1}>".format(repr(s), repr(deleg.rdap_URLs)),
            repr(deleg)
        )
