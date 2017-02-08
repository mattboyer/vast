from ..metadata.assigned import AssignedSubnet
from ..tools.logger import ModuleLogger

from functools import reduce
from sqlalchemy import func, null

log = ModuleLogger(__name__)


class SubnetLinker(object):
    '''
    Creates relationships between assigned subnets
    '''

    def __init__(self, data_mgr):
        self.data_mgr = data_mgr

    @staticmethod
    def group_contiguous_subnets(contiguous_subnets, next_subnet_up):
        # contiguous_subnets is a list of 2-tuples, with each comprising a
        # count of contiguous AssignedSubnet objects and the corresponding list
        # of contiguous AssignedSubnet instances

        # If we have an empty list, then this is easy enough
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
        # When there are mulitple assigned subnets with the same network
        # address, we'll want the smallest, (i.e. the one with the longest
        # prefix length)
        assigned_subnet_iter = self.data_mgr.query(
            AssignedSubnet,
        ).having(
            func.max(AssignedSubnet.mapped_prefix_length)
        ).group_by(
            AssignedSubnet.mapped_network
        )

        contiguous_batches = reduce(
            SubnetLinker.group_contiguous_subnets,
            assigned_subnet_iter,
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

        # Let's inspect the subnets that have neither a next nor a prev, ie.
        # those subnets that weren't the smallest for their network address
        container_subnet_iter = self.data_mgr.query(
            AssignedSubnet,
        ).filter(
            AssignedSubnet.next_subnet_id == null(),
            AssignedSubnet.previous_subnet_id == null(),
        ).order_by(
            AssignedSubnet.mapped_prefix_length
        )

        child_subnets = []
        for cs in container_subnet_iter:
            log.info("Finding subnets nested under %r", cs)
            children_subnet_iter = self.data_mgr.query(
                AssignedSubnet
            ).filter(
                AssignedSubnet.mapped_network >= cs.floor(),
                AssignedSubnet.mapped_network <= cs.ceiling(),
                AssignedSubnet.mapped_prefix_length > cs.prefix_length
            )
            for nested_subnet in children_subnet_iter:
                log.info("Found %r", nested_subnet)
                nested_subnet.parent = cs
                child_subnets.append(nested_subnet)

        self.data_mgr.update_records(child_subnets)
