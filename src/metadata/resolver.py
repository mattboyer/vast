from ..tools.logger import ModuleLogger
from .IANA_IPv4_assignments import populate_IANA_IPv4_assignments
from .RDAP import RDAP_Resolver
from .whois import Whois_Resolver
from .constants import reserved_networks
from . import (
    ResolutionException, RDAPResolutionException, RDAPRedirectException
)

log = ModuleLogger(__name__)


class DelegationResolver(object):

    def __init__(self):
        self._iana_top_level = populate_IANA_IPv4_assignments()
        self._rdap_resolver = RDAP_Resolver(self)
        self._whois_resolver = Whois_Resolver(self)

    def validate_assignment(self, assignment):
        if 0 == assignment.prefix_length:
            raise ResolutionException("Whole address space!")
        if 8 > assignment.prefix_length:
            raise ResolutionException("Unreasonably large subnet")

    def _resolve_reserved_networks(self, network):
        for reserved_net in reserved_networks:
            if network in reserved_net:
                return reserved_net

    def resolve(self, network):
        # We need to keep track of potentially multiple candidates for the
        # given network and eventually return the best one of the bunch

        reserved_assignment = self._resolve_reserved_networks(network)
        if reserved_assignment:
            return reserved_assignment

        try:
            rdap_assignment = self._rdap_resolver.resolve(network)
            # TODO Do some sanity checking!
            self.validate_assignment(rdap_assignment)
            return rdap_assignment

        except RDAPRedirectException as redir_ex:
            provisional = redir_ex.provisional
            log.warning("Caught \"%s\".", redir_ex)
            try:
                redirected_assignment = self._rdap_resolver.resolve_from_url(
                    redir_ex.redir_url
                )
            except ResolutionException:
                return provisional
            else:
                return redirected_assignment

        except ResolutionException as rdap_ex:
            # Yes, but what if whois is even worse? We need to be able to fall
            # back on any partial information RDAP gave us in that case.
            log.warning("Caught \"%s\". Trying whois", rdap_ex)
            if isinstance(rdap_ex, RDAPResolutionException):
                whois = rdap_ex.whois_host  # pylint:disable=E1101
            else:
                # What if the RDAP query didn't include a port43 entry?
                whois = None

            try:
                whois_assignment = self._whois_resolver.resolve(
                    network,
                    whois_host=whois
                )
                self.validate_assignment(whois_assignment)
                return whois_assignment
            except ResolutionException as re:
                log.error(re)
                raise

    def get_top_level_assignment(self, slash_eight):
        try:
            return self._iana_top_level[slash_eight]
        except KeyError:
            raise ResolutionException(
                "Couldn't find top-level delegation for {0}".format(
                    slash_eight
                )
            )
