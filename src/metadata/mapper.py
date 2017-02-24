from ..net.IPv4 import Subnet
from ..metadata.resolver import DelegationResolver
from ..metadata import ResolutionException
from ..tools.logger import ModuleLogger


log = ModuleLogger(__name__)


class SubnetMapper(object):

    def __init__(self, data_mgr):
        self.data_mgr = data_mgr
        self.resolver = DelegationResolver()

    def scan_up(self, sub_first_address):
        while True:
            try:
                assigned_subnet = self.resolver.resolve(
                    Subnet(sub_first_address, 32)
                )
                if sub_first_address not in assigned_subnet:
                    raise ResolutionException

                sub_first_address = assigned_subnet.ceiling() + 1
                log.info("Found %r", assigned_subnet)
                self.data_mgr.update_record(assigned_subnet)

            except ResolutionException:
                log.warning("Couldn't resolve %s", sub_first_address)
                # sub_first_address += 4
                break
