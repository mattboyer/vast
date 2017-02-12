from . import Command, CLI_subcmd
from ..metadata import ResolutionException
from ..metadata.orm import DataManager
from ..metadata.resolver import DelegationResolver
from ..net.IPv4 import Subnet, Address
from ..tools.logger import ModuleLogger


log = ModuleLogger(__name__)


@CLI_subcmd('map')
class MapCmd(Command):
    '''
    Populates the IPv4 address-space database
    '''

    @classmethod
    def configure_parser(clazz, parser):
        parser.add_argument(
            'start',
            type=str,
            help='Start scanning from this IPv4 address',
        )

    def _scan_up(self, sub_first_address, data_mgr):

        resolver = DelegationResolver()
        while True:
            try:
                assigned_subnet = resolver.resolve(
                    Subnet(sub_first_address, 32)
                )
                sub_first_address = assigned_subnet.ceiling() + 1
                log.info("Found %r", assigned_subnet)
                data_mgr.update_record(assigned_subnet)

            except ResolutionException:
                log.warning("Couldn't resolve %s", sub_first_address)
                sub_first_address += 4

    def run(self, arg_ns):
        data_mgr = DataManager()

        start_address = Address(arg_ns.start)
        self._scan_up(start_address, data_mgr)
