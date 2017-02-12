from . import Command, CLI_subcmd
from ..metadata.orm import DataManager
from ..tools.logger import ModuleLogger

from collections import defaultdict

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
