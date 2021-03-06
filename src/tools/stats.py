from . import Command, CLI_subcmd
from ..metadata.orm import DataManager
from ..metadata.stats import StatsProcessor


@CLI_subcmd('stats')
class StatsCmd(Command):
    '''
    Displays coverage stats
    '''

    def __init__(self):
        self.stats = None
        self.data_mgr = None

    def run(self, arg_ns):
        self.data_mgr = DataManager()
        self.stats = StatsProcessor(self.data_mgr)

        self._print_length_stats()
        self._print_coverage_stats()

    def _print_length_stats(self):
        subnet_count, prefix_lengths = self.stats.distribution()
        print("{0} assigned subnets\n".format(subnet_count))

        length_distribution = sorted(prefix_lengths.keys(), reverse=True)
        for length in length_distribution:
            print("/{0} count:       {1}".format(
                length, prefix_lengths[length])
            )

    def _print_coverage_stats(self):
        total_unicast_coverage, coverage = self.stats.coverage()
        print("\nTotal coverage {0} IPv4 addresses".format(
            total_unicast_coverage
        ))
        print("Coverage: {0}% of IPv4 addresses".format(coverage))
