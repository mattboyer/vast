from . import (
    RDAPResolutionException, RateLimitationException,
    RDAPRedirectException, RDAPRedirectionDetected
)
from ..net.IPv4 import Address
from ..tools.logger import ModuleLogger
from .assigned import AssignedSubnet

import pprint
import requests
import time

# TODO Do we ever get a 'name' attribute from afrinic?
log = ModuleLogger(__name__)
json_printer = pprint.PrettyPrinter()


class RDAP_Resolver(object):
    GET_RETRIES = 10
    RATE_LIMITATION_RETRIES = 5
    RATE_LIMITATION_DELAY = 61

    def __init__(self, ipv4_resolver):
        # TODO Use some sort of deque here
        self._resolver = ipv4_resolver
        self._session = requests.Session()
        # TODO Global header and hook stuff here

    def _get_raw_RDAP_JSON(self, rdap_url):
        '''
        Attempts to get a raw JSON object for a given RDAP URL.
        This method is satisfied when a valid RDAP JSON object has been
        retrieved for rdap_url.
        This method doesn't follow redirection and is unaware of things
        like RDAP notices indicating rate limitation violations.
        '''

        redirect_url = None
        req_count = 0
        while req_count < self.GET_RETRIES:
            network_response = self._session.get(
                rdap_url,
                allow_redirects=False,
            )
            req_count += 1

            log.info(
                "RDAP query %s: %d", rdap_url, network_response.status_code
            )

            if network_response.is_redirect:
                redirect_url = network_response.headers.get('Location')
                if redirect_url:
                    log.debug('RDAP redirect to %s', redirect_url)
                    break
                else:
                    raise RDAPResolutionException('RDAP redirect with no URI')

            if network_response.status_code == requests.codes['OK']:
                break

            if network_response.status_code == requests.codes['NOT_FOUND']:
                raise RDAPResolutionException(
                    "RDAP resource not found: {0}",
                    rdap_url
                )

            # What codes exactly does this cover?
            if network_response.status_code == requests.codes['BAD_REQUEST']:
                raise RDAPResolutionException(
                    "RDAP request returned {0}",
                    network_response.status_code
                )
        else:
            raise RDAPResolutionException(
                "Out of retries for RDAP resource: {0}",
                rdap_url
            )

        raw_json = None
        try:
            raw_json = network_response.json()
        except Exception:  # pylint:disable=W0703
            if redirect_url:
                raise RDAPRedirectionDetected(redir_url=redirect_url)
            else:
                raise RDAPResolutionException("Malformed JSON in RDAP output")

        if redirect_url:
            raise RDAPRedirectionDetected(
                redir_url=redirect_url, redir_json=raw_json
            )
        return raw_json

    def resolve(self, network):
        # Discovers inetnums contained within network
        network_slash_eight = network % 8
        slash_eight_delegation = self._resolver.\
            get_top_level_assignment(network_slash_eight)

        if not slash_eight_delegation.rdap_URLs:
            raise RDAPResolutionException("No RDAP URL for {0}", network)

        rdap_base_url = None
        for rdap_base_url in slash_eight_delegation.rdap_URLs:
            if rdap_base_url.startswith('http:'):
                break

        # We want to avoid double slashes
        if rdap_base_url.endswith('/'):
            rdap_base_url = rdap_base_url[:-1]
        rdap_url = rdap_base_url + '/ip/' + str(network.floor())
        return self.resolve_from_url(rdap_url)

    def resolve_from_url(self, rdap_url):
        '''
        Attempts to get return an AssignedSubnet object built using the RDAP
        JSON output retrieved for a given RDAP URL.
        This method doesn't follow redirection but is aware of rate limitation
        violations.
        '''

        rate_limitation_retries = 0
        rdap_json = redirect = None

        while rate_limitation_retries < self.RATE_LIMITATION_RETRIES:

            try:
                rdap_json = self._get_raw_RDAP_JSON(rdap_url)
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
                time.sleep(self.RATE_LIMITATION_DELAY)

            except RDAPRedirectionDetected as redir:
                # We got an HTTP redirection. If we didn't get a RDAP JSON
                # body, then we can raise a RDAPRedirectException to that
                # effect.
                if not redir.redir_json:
                    raise RDAPRedirectException(
                        'Redirection to {0}. No provisional assignment',
                        redir.redir_url,
                        rdap_url,
                        redir_url=redir.redir_url,
                    )

                # If however a RDAP JSON body was retrieved, then we should try
                # and build an AssignedSubnet out of it before we raise a
                # RDAPRedirectException to the caller.
                else:
                    redirect = redir.redir_url
                    rdap_json = redir.redir_json
                    break

            except RDAPResolutionException as ex:
                # We couldn't get meaningful JSON out of that URL
                log.error(
                    'Failed to get a valid RDAP response for: %s',
                    rdap_url
                )
                raise ex
            else:
                break

        else:
            raise RDAPResolutionException(
                "Couldn't get around rate limitation for {0}", rdap_url
            )

        # We now have a valid RDAP JSON object and maybe a redirect URL
        return self._assigned_subnet_from_RDAP(rdap_json, redirect=redirect)

    def _assigned_subnet_from_RDAP(self, rdap_json, redirect=None):
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
            log.debug("Malformed RDAP: %s", json_printer.pformat(rdap_json))
            raise RDAPResolutionException(
                "Malformed RDAP. Missing attribute {0}",
                str(ke),
                whois_host=whois_host
            )
