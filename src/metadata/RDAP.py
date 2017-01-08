from . import (
    RDAPResolutionException, RateLimitationException, RDAPRedirectException
)
from ..net.IPv4 import Address
from ..tools.logger import ModuleLogger
from .assigned import AssignedSubnet

import requests
import time

# TODO Do we ever get a 'name' attribute from afrinic?
log = ModuleLogger(__name__)


class RDAP_Resolver(object):
    def __init__(self, ipv4_resolver):
        # TODO Use some sort of deque here
        self._resolver = ipv4_resolver
        self._session = requests.Session()
        # TODO Global header and hook stuff here

    def _get_raw_RDAP_JSON(self, rdap_url):
        '''
        Attempts to get a raw JSON object for a given RDAP URL.
        '''
        # FIXME Redirection should not be handled here!!!

        redirect_url = None
        req_count = 0
        while req_count < 10:
            network_response = self._session.get(
                rdap_url,
                allow_redirects=False,
            )
            req_count += 1

            log.info(
                "RDAP query %s: %d", rdap_url, network_response.status_code
            )

            if network_response.is_redirect:
                # Maybe we should keep track of the end address if it is
                # present... just in case the redirection ends up being a wild
                # goose chase
                redirect_url = network_response.headers['Location']
                log.debug('RDAP redirect to %s', redirect_url)
                break

            if network_response.status_code == requests.codes['OK']:
                break

            if network_response.status_code == requests.codes['NOT_FOUND']:
                raise RDAPResolutionException(
                    "RDAP resource not found: {0}",
                    rdap_url
                )

            if network_response.status_code == requests.codes['BAD_REQUEST']:
                raise RDAPResolutionException(
                    "RDAP request returned {0}",
                    network_response.status_code
                )

        return redirect_url, network_response.json()

    def resolve(self, network):
        # Discovers inetnums contained within network
        network_slash_eight = network % 8
        slash_eight_delegation = self._resolver.\
            get_top_level_assignment(network_slash_eight)

        if not slash_eight_delegation.rdap_URLs:
            raise RDAPResolutionException("No RDAP URL")

        rdap_base_url = slash_eight_delegation.rdap_URLs[0]
        # We want to avoid double slashes
        if rdap_base_url.endswith('/'):
            rdap_base_url = rdap_base_url[:-1]
        rdap_url = rdap_base_url + '/ip/' + str(network.floor())
        return self.resolve_from_url(rdap_url)

    def resolve_from_url(self, rdap_url):
        rate_limitation_retries = 0
        while rate_limitation_retries < 10:

            try:
                redirect, rdap_json = self._get_raw_RDAP_JSON(rdap_url)
                rate_limitation_retries += 1

                try:
                    for notice_json in rdap_json['notices']:
                        if 'rate limit' in notice_json['title'].lower():
                            log.warning(
                                'Rate limitation complaint: %s',
                                str(notice_json)
                            )
                            raise RateLimitationException

                except KeyError:
                    # Notices are optional
                    pass

            except RateLimitationException:
                # Take five and try again
                time.sleep(61)
            else:
                break

        else:
            raise RDAPResolutionException(
                "Couldn't get around rate limitation for {0}", rdap_url
            )

        whois_host = None
        try:
            whois_host = rdap_json['port43']
        except KeyError:
            log.warning("RDAP response doesn't include a whois host")
        else:
            log.debug("port43 entry: %s", whois_host)

        try:
            start_address = rdap_json['startAddress']
            if start_address.endswith('/32'):
                start_address = start_address[:-3]
            start_address = Address(start_address)

            end_address = rdap_json['endAddress']
            if end_address.endswith('/32'):
                end_address = end_address[:-3]
            end_address = Address(end_address)

            assigned = AssignedSubnet(
                start_address,
                end_address,
                rdap_json['name']
            )
            if redirect is not None:
                raise RDAPRedirectException(
                    'Redirection to {0}. Provisional assignment: {1}',
                    redirect,
                    assigned,
                    provisional=assigned,
                    redir_url=redirect,
                )

            return assigned
        except KeyError as ke:
            import pprint
            log.info(pprint.pprint(rdap_json))
            raise RDAPResolutionException(
                "Malformed RDAP. Missing attribute {0}",
                str(ke),
                whois_host=whois_host
            )
