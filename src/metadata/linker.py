from ..metadata.assigned import AssignedSubnet
from ..tools.logger import ModuleLogger

from functools import reduce
from sqlalchemy import null

log = ModuleLogger(__name__)


class SubnetLinker(object):
    '''
    Creates relationships between assigned subnets
    '''

    def __init__(self, data_mgr):
        self.data_mgr = data_mgr

    def link(self):
        contiguous_batches = reduce(
            self.data_mgr.reduce_contiguous_subnets,
            self.data_mgr.fine_subnet_iter(),
            []
        )
        for contiguous_sequence in contiguous_batches:
            # Set adjacency relationships - the 'previous backref' is
            # populated automagically
            for idx, sub in enumerate(contiguous_sequence):
                if 0 == idx:
                    continue
                sub.previous = contiguous_sequence[idx-1]
                contiguous_sequence[idx-1].next = sub
            # Update the prev/next fields
            self.data_mgr.update_records(contiguous_sequence)

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
