from . import Command, CLI_subcmd
from ..metadata.orm import DataManager
from ..metadata.linker import SubnetManager
from ..tools.logger import ModuleLogger

from functools import reduce

log = ModuleLogger(__name__)


@CLI_subcmd('analyse')
class AnalyseCmd(Command):
    '''
    Produces coverage stats and triggers the linker
    '''

    def run(self, arg_ns):
        self.data_mgr = DataManager()
        linker = SubnetLinker(self.data_mgr)
        self._print_stats()
        linker.link()

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
