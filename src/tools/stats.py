from . import Command, CLI_subcmd
from ..metadata.orm import DataManager
from ..metadata.assigned import AssignedSubnet
from ..net.IPv4 import Address, Subnet
from ..tools.logger import ModuleLogger

from collections import defaultdict
from decimal import Decimal
from functools import reduce

from sqlalchemy import func

log = ModuleLogger(__name__)


@CLI_subcmd('stats')
class StatsCmd(Command):
    '''
    Produces coverage stats
    '''

    def __init__(self):
        self.data_mgr = None

    def run(self, arg_ns):
        self.data_mgr = DataManager()
        self._length_stats()
        self._coverage_stats()

    def _length_stats(self):
        prefix_lengths = defaultdict(int)
        all_subs = self.data_mgr.all_records()
        subnet_count = 0
        for sub in all_subs:
            prefix_lengths[sub.prefix_length] += 1
            subnet_count += 1

        log.info("%d assigned subnets", subnet_count)

        length_distribution = sorted(prefix_lengths.keys(), reverse=True)
        for length in length_distribution:
            log.info("/%d count:	%d", length, prefix_lengths[length])

    def _coverage_stats(self):
        # TODO We need to find the gaps between contiguous subnets!
        assigned_subnet_iter = self.data_mgr.query(
            AssignedSubnet,
        ).having(
            func.max(AssignedSubnet.mapped_prefix_length)
        ).group_by(
            AssignedSubnet.mapped_network
        )

        contiguous_coverage = reduce(
            DataManager.reduce_contiguous_subnets,
            assigned_subnet_iter,
            []
        )

        whole_unicast_address_space = int(Address("225.255.255.255")) + 1
        total_unicast_coverage = 0

        for contig_block in contiguous_coverage:
            contig_start = contig_block[0].floor()
            contig_end = contig_block[-1].ceiling()
            contig_length = sum(len(subnet) for subnet in contig_block)
            total_unicast_coverage += contig_length
            log.debug("%r → %r: %r", contig_start, contig_end, contig_length)

        log.info("Total coverage: %d", total_unicast_coverage)
        coverage = round(100 * (Decimal(total_unicast_coverage) /
                                Decimal(whole_unicast_address_space)), 3)
        log.info("Coverage: %s %%", coverage)
