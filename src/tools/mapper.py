from . import Command, CLI_subcmd
from ..metadata.orm import DataManager
from ..metadata.mapper import SubnetMapper
from ..net.IPv4 import Address


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

    def __init__(self):
        self.data_mgr = None
        self.mapper = None

    def run(self, arg_ns):
        self.data_mgr = DataManager()
        self.mapper = SubnetMapper(self.data_mgr)

        start_address = Address(arg_ns.start)
        self.mapper.scan_up(start_address)
