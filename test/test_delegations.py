from unittest import TestCase
from mock import patch, Mock, call

from src.metadata.IANA_IPv4_assignments import TopLevelDelegation, populate_IANA_IPv4_assignments
from src.net.IPv4 import Subnet, Address

class test_Delegations(TestCase):

    address_space_xml = '''
<?xml version='1.0' encoding='UTF-8'?>
<?oxygen RNGSchema="ipv4-address-space.rng" type="xml"?>
<registry xmlns="http://www.iana.org/assignments" id="ipv4-address-space">
  <title>IANA IPv4 Address Space Registry</title>
  <category>Internet Protocol version 4 (IPv4) Address Space</category>
  <updated>2015-08-10</updated>
  <xref type="rfc" data="rfc7249"/>
  <registration_rule>Allocations to RIRs are made in line with the Global Policy published at <xref type="uri" data="http://www.icann.org/en/resources/policy/global-addressing"/>. 
All other assignments require IETF Review.</registration_rule>
  <description>The allocation of Internet Protocol version 4 (IPv4) address space to various registries is listed
here. Originally, all the IPv4 address spaces was managed directly by the IANA. Later parts of the
address space were allocated to various other registries to manage for particular purposes or
regional areas of the world. RFC 1466 <xref type="rfc" data="rfc1466"/> documents most of these allocations.</description>
  <record>
    <prefix>000/8</prefix>
    <designation>IANA - Local Identification</designation>
    <date>1981-09</date>
    <status>RESERVED</status>
    <xref type="note" data="2"/>
  </record>
  <record>
    <prefix>001/8</prefix>
    <designation>APNIC</designation>
    <date>2010-01</date>
    <whois>whois.apnic.net</whois>
    <rdap>
      <server>https://rdap.apnic.net/</server>
    </rdap>
    <status>ALLOCATED</status>
  </record>
  <record>
    <prefix>002/8</prefix>
    <designation>RIPE NCC</designation>
    <date>2009-09</date>
    <whois>whois.ripe.net</whois>
    <rdap>
      <server>https://rdap.db.ripe.net/</server>
    </rdap>
    <status>ALLOCATED</status>
  </record>
  <record>
    <prefix>003/8</prefix>
    <designation>General Electric Company</designation>
    <date>1994-05</date>
    <whois>whois.arin.net</whois>
    <rdap>
      <server>https://rdap.arin.net/registry</server>
      <server>http://rdap.arin.net/registry</server>
    </rdap>
    <status>LEGACY</status>
  </record>
</registry>
    '''.strip()

    def test_delegation_repr(self):
        deleg = TopLevelDelegation(10)
        deleg.rdap_URLs = ['http://example.org', 'https://example.com']

        s = Subnet(Address("10.0.0.0"), 8)
        self.assertEqual(
            "<TopLevelDelegation {0}: {1}>".format(repr(s), repr(deleg.rdap_URLs)),
            repr(deleg)
        )

    @patch('src.metadata.IANA_IPv4_assignments.requests.get')
    def test_populate_success(self, mock_get):
        response = Mock(ok=True)
        response.iter_lines = lambda: self.address_space_xml.splitlines()
        mock_get.return_value = response
        assignments = populate_IANA_IPv4_assignments()

        expected_subnets = set([
            Subnet(Address("0.0.0.0"), 8),
            Subnet(Address("1.0.0.0"), 8),
            Subnet(Address("2.0.0.0"), 8),
            Subnet(Address("3.0.0.0"), 8),
        ])

        self.assertTrue(isinstance(assignments, dict))
        self.assertEquals(4, len(assignments))
        self.assertEquals(expected_subnets, set(assignments.keys()))

        self.assertTrue(
            all(isinstance(assignments[tld], TopLevelDelegation) for tld in assignments)
        )

        self.assertEquals(set(), assignments[Subnet(Address("0.0.0.0"), 8)].rdap_URLs)
        self.assertIsNone(assignments[Subnet(Address("0.0.0.0"), 8)].whois_host)
        #
        self.assertEquals(
            # The trailing slash is trimmed here
            {"https://rdap.apnic.net",},
            assignments[Subnet(Address("1.0.0.0"), 8)].rdap_URLs
        )
        self.assertEquals(
            "whois.apnic.net",
            assignments[Subnet(Address("1.0.0.0"), 8)].whois_host
        )
        #
        self.assertEquals(
            # The trailing slash is trimmed here
            {"https://rdap.db.ripe.net",},
            assignments[Subnet(Address("2.0.0.0"), 8)].rdap_URLs
        )
        self.assertEquals(
            "whois.ripe.net",
            assignments[Subnet(Address("2.0.0.0"), 8)].whois_host
        )
        #
        self.assertEquals(
            {"https://rdap.arin.net/registry", "http://rdap.arin.net/registry"},
            assignments[Subnet(Address("3.0.0.0"), 8)].rdap_URLs
        )
        self.assertEquals(
            "whois.arin.net",
            assignments[Subnet(Address("3.0.0.0"), 8)].whois_host
        )
