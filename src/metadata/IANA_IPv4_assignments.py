from ..net.IPv4 import Subnet, Address
from . import constants

import requests
import xml.etree.ElementTree as ET


class TopLevelDelegation(object):
    def __init__(self, top_byte):
        # TODO ideally, we'd be dealing with objects that represent blocks of
        # contiguous IPv4 addresses here.

        start_address = Address(top_byte << 24)
        self.delegation_subnet = Subnet(start_address, 8)

        self.rdap_URLs = set([])
        self.whois_host = None

    def __repr__(self):
        return "<{klass} {top_byte}: {url}>".format(
            klass=self.__class__.__name__,
            top_byte=self.delegation_subnet,
            url=self.rdap_URLs
        )


def populate_IANA_IPv4_assignments():
    slash_eights = {}

    iana_xml = requests.get(constants.IANA_TOP_LEVEL_ALLOCATION_URL)
    if not iana_xml.ok:
        raise iana_xml.raise_for_status()

    registry_DOM = ET.fromstringlist(iana_xml.iter_lines())
    for iana_record_element in registry_DOM.findall(
            'assignments:record', constants.IANA_TOP_LEVEL_ALLOCATION_NS):
        prefix_element = iana_record_element.find(
                'assignments:prefix', constants.IANA_TOP_LEVEL_ALLOCATION_NS)
        if prefix_element is None:
            raise Exception()

        slash_eight = prefix_element.text
        if not isinstance(slash_eight, str):
            raise ValueError()
        if not slash_eight.endswith('/8'):
            raise ValueError()

        top_byte = int(slash_eight[:-2])
        delegation_cidr = Subnet(Address((top_byte, 0, 0, 0)), 8)

        tld = TopLevelDelegation(top_byte)
        rdap_element = iana_record_element.find(
                'assignments:rdap', constants.IANA_TOP_LEVEL_ALLOCATION_NS)

        if rdap_element:
            for rdap_server_element in rdap_element.findall(
                        'assignments:server',
                        constants.IANA_TOP_LEVEL_ALLOCATION_NS
                    ):
                tld.rdap_URLs.add(rdap_server_element.text.rstrip('/'))

        whois_element = iana_record_element.find(
                'assignments:whois', constants.IANA_TOP_LEVEL_ALLOCATION_NS)

        if whois_element is not None:
            tld.whois_host = whois_element.text
            tld.whois_host.strip()

        slash_eights[delegation_cidr] = tld

    return slash_eights
