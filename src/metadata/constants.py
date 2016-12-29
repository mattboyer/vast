from ..net.IPv4 import Address
from .assigned import AssignedSubnet


IANA_TOP_LEVEL_ALLOCATION_URL = 'http://www.iana.org/assignments/'\
    'ipv4-address-space/ipv4-address-space.xml'

IANA_TOP_LEVEL_ALLOCATION_NS = {
    "assignments": "http://www.iana.org/assignments"
}

reserved_networks = (
    AssignedSubnet(
        Address((0, 0, 0, 0)), 8,
        "SPECIAL-IPV4-LOCAL-ID-IANA-RESERVED"
    ),
    AssignedSubnet(
        Address((10, 0, 0, 0)), 8,
        "PRIVATE-ADDRESS-ABLK-RFC1918-IANA-RESERVED"
    ),
    AssignedSubnet(
        Address((127, 0, 0, 0)), 8,
        "SPECIAL-IPV4-LOOPBACK-IANA-RESERVED"
    ),
    AssignedSubnet(
        Address((172, 16, 0, 0)), 12,
        "PRIVATE-ADDRESS-BBLK-RFC1918-IANA-RESERVED"
    ),
    AssignedSubnet(
        Address((192, 168, 0, 0)), 16,
        "PRIVATE-ADDRESS-CBLK-RFC1918-IANA-RESERVED"
    ),
    # Multicast
    AssignedSubnet(
        Address((224, 0, 0, 0)), 4,
        "MCAST-NET"
    ),
    # Future use
    AssignedSubnet(
        Address((240, 0, 0, 0)), 4,
        "SPECIAL-IPV4-FUTURE-USE-IANA-RESERVED"
    ),
)
