from ..net.IPv4 import Address

from collections import defaultdict
from decimal import Decimal

from ..tools.logger import ModuleLogger

log = ModuleLogger(__name__)


# Technically, this is more of a processor
class StatsManager(object):

    def __init__(self, data_mgr):
        self.data_mgr = data_mgr

    def distribution(self):
        prefix_lengths = defaultdict(int)
        subnet_count = 0

        for sub in self.data_mgr.all_records():
            prefix_lengths[sub.prefix_length] += 1
            subnet_count += 1

        return (subnet_count, prefix_lengths)

    def coverage(self):
        contiguous_coverage = self.data_mgr.group_contiguous_subnets()

        whole_unicast_address_space = int(Address("225.255.255.255")) + 1
        total_unicast_coverage = 0

        for contig_block in contiguous_coverage:
            contig_start = contig_block[0].floor()
            contig_end = contig_block[-1].ceiling()
            contig_length = sum(len(subnet) for subnet in contig_block)
            total_unicast_coverage += contig_length

            log.debug("%r → %r: %r", contig_start, contig_end, contig_length)

        coverage = round(100 * (Decimal(total_unicast_coverage) /
                                Decimal(whole_unicast_address_space)), 3)
        return total_unicast_coverage, coverage
