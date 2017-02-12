from . import Command, CLI_subcmd
from ..metadata.orm import DataManager
from ..metadata.linker import SubnetLinker
from ..tools.logger import ModuleLogger

log = ModuleLogger(__name__)


@CLI_subcmd('link')
class LinkCmd(Command):
    '''
    Triggers the assigned subnet linker
    '''

    def __init__(self):
        self.data_mgr = None

    def run(self, arg_ns):
        self.data_mgr = DataManager()
        linker = SubnetLinker(self.data_mgr)
        # TODO We need to find the gaps between contiguous subnets!
        linker.link()
