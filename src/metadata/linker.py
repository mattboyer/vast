from ..tools.logger import ModuleLogger

from collections import defaultdict
from functools import reduce

log = ModuleLogger(__name__)


class SubnetLinker(object):
    '''
    Creates relationships between assigned subnets
    '''

    def __init__(self, data_mgr):
        self.data_mgr = data_mgr

    @staticmethod
    def group_contiguous_subnets(contiguous_subnets, next_subnet_up):
        # a is a list of 2-tuples comprising a count of contiguous...things and
        # whether these are contiguous true or false values
        if not contiguous_subnets:
            contiguous_subnets.append((1, [next_subnet_up]))
            return contiguous_subnets

        # We have a non-empty list
        contiguous_count, contiguous_list = contiguous_subnets[-1]
        if int(next_subnet_up.floor()) == \
                1 + int(contiguous_list[-1].ceiling()):
            # Set adjacency relationships - the 'previous backref' is
            # populated automagically
            contiguous_list[-1].next = next_subnet_up
            next_subnet_up.previous = contiguous_list[-1]

            contiguous_list.append(next_subnet_up)
            contiguous_subnets[-1] = (contiguous_count + 1, contiguous_list)
        else:
            contiguous_subnets.append((1, [next_subnet_up]))
        return contiguous_subnets

    def link(self):
        prefix_lengths = defaultdict(int)
        all_subs = self.data_mgr.all_records()
        subnet_count = 0
        for sub in all_subs:
            prefix_lengths[sub.prefix_length] += 1
            subnet_count += 1

        log.info("%d assigned subnets", subnet_count)

        # FIXME Do we need this here?
        length_distribution = sorted(prefix_lengths.keys(), reverse=True)
        for length in length_distribution:
            log.info("/%d count:	%d", length, prefix_lengths[length])

        # TODO We need to find the gaps between contiguous subnets!
        contiguous_batches = reduce(
            SubnetLinker.group_contiguous_subnets,
            self.data_mgr.all_records(),
            []
        )
        for _, contiguous_sequence in contiguous_batches:
            # This is meant to update the prev/next fields
            self.data_mgr.update_records(contiguous_sequence)

        for batch in contiguous_batches:
            count, sequence = batch
            start = sequence[0].floor()
            end = sequence[-1].ceiling()
            log.info("%d contiguous subs: %s - %s", count, start, end)