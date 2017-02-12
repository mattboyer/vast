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
        self._print_stats()

    @staticmethod
    def enumerate_contiguous_subnets(contiguous_subnets, next_subnet_up):
        # contiguous_subnets is a list of 2-tuples, with each comprising a
        # count of contiguous AssignedSubnet objects and the corresponding list
        # of contiguous AssignedSubnet instances

        # If we have an empty list, then this is easy enough
        if not contiguous_subnets:
            contiguous_subnets.append([next_subnet_up])
            return contiguous_subnets

        # We have a non-empty list
        contiguous_list = contiguous_subnets[-1]
        if int(next_subnet_up.floor()) == \
                1 + int(contiguous_list[-1].ceiling()):

            contiguous_list.append(next_subnet_up)
            contiguous_subnets[-1] = contiguous_list
        else:
            contiguous_subnets.append([next_subnet_up])
        return contiguous_subnets

    def _print_stats(self):
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

        assigned_subnet_iter = self.data_mgr.query(
            AssignedSubnet,
        ).having(
            func.max(AssignedSubnet.mapped_prefix_length)
        ).group_by(
            AssignedSubnet.mapped_network
        )

        contiguous_coverage = reduce(
            self.enumerate_contiguous_subnets,
            assigned_subnet_iter,
            []
        )

        whole_unicast_address_space = int(Address("225.255.255.255")) + 1
        total_unicast_coverage = 0

        for sub in contiguous_coverage:
            contig_start = sub[0].floor()
            contig_end = sub[-1].ceiling()
            contig_length = sum(len(s) for s in sub)
            total_unicast_coverage += contig_length
            log.debug("%r → %r: %r", contig_start, contig_end, contig_length)

        log.info("Total coverage: %d", total_unicast_coverage)
        coverage = 100 * (Decimal(total_unicast_coverage) /
                          Decimal(whole_unicast_address_space))
        log.info("Coverage: %s %%", coverage)
