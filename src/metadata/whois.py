from . import ResolutionException
from ..net.IPv4 import Address
from ..tools.logger import ModuleLogger
from .assigned import AssignedSubnet

from collections import defaultdict
import re
from socket import socket, getaddrinfo, AF_INET, SOCK_STREAM


RPSL_ATTR_VALUE_RE = re.compile(r'^(\S+):\s+(.*)$')
RPSL_ATTR_NOVALUE_RE = re.compile(r'^(\S+):$')

log = ModuleLogger(__name__)

# TODO Use whois-specific exceptions!!!

# TODO Use whois:// URLs
class Whois_Resolver(object):

    def __init__(self, ipv4_resolver):
        self._resolver = ipv4_resolver

    def get_whois_entry(self, net_address, whois_host=None):
        whois_PDU = "-V Md5.1 {0}\n".format(net_address.floor())
        whois_PDU = whois_PDU.encode("ASCII")

        if not whois_host:
            network_slash_eight = net_address % 8
            slash_eight_delegation = self._resolver.\
                get_top_level_assignment(network_slash_eight)

            if not slash_eight_delegation.rdap_URLs:
                raise ResolutionException("No RDAP URL")

            whois_host = slash_eight_delegation.whois_host
            if not whois_host:
                raise ResolutionException

        sockinfo = getaddrinfo(
            whois_host,
            # Surprisingly, "whois" isn't always present in the "services" DB.
            # "nicname" appears to be the correct service name.
            "nicname",
            family=AF_INET
        )
        sockaddr = sockinfo[0][-1]
        log.debug("Resolved \"%s\" to %s", whois_host, sockaddr)
        output = bytes()
        with socket(family=AF_INET, type=SOCK_STREAM) as whois_socket:
            whois_socket.connect(sockaddr)
            whois_socket.send(whois_PDU)
            while True:
                data = whois_socket.recv(4096)
                # TODO Should we have some sort of timeout here?
                if not data:
                    break
                output += data

        log.info(
            "WHOIS query %s", whois_host
        )
        output = output.decode()
        return output

    def resolve(self, net_address, whois_host=None):
        entry = self.get_whois_entry(net_address, whois_host)
        entry_pairs = defaultdict(list)

        attribute = None
        for rpsl_line in entry.splitlines():
            rpsl_line.strip()
            if not rpsl_line or rpsl_line[0] in ('%', '#'):
                continue

            matches = RPSL_ATTR_VALUE_RE.match(rpsl_line)
            if not matches:
                if rpsl_line.startswith(16 * ' '):
                    rpsl_line.strip()
                    entry_pairs[attribute].append(rpsl_line)
                elif RPSL_ATTR_NOVALUE_RE.match(rpsl_line):
                    continue
                else:
                    raise ResolutionException(
                        "Malformed Whois entry: {0}".format(rpsl_line)
                    )
            else:
                attribute = matches.group(1) or None
                entry_pairs[attribute].append(matches.group(2))

        if not 1 == len(entry_pairs['inetnum']):
            raise ResolutionException("TODO")

        if not 1 == len(entry_pairs['netname']):
            raise ResolutionException("TODO")
        inet_range = entry_pairs['inetnum'].pop()
        start, end = [s.strip() for s in inet_range.split('-')]

        netname = entry_pairs['netname'].pop()

        assigned = AssignedSubnet(
            Address(start),
            Address(end),
            netname
        )
        return assigned
