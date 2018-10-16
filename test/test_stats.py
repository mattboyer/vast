from unittest.mock import patch, Mock, call
from unittest import TestCase

from src.net.IPv4 import Address, Subnet
from src.metadata.assigned import AssignedSubnet
from src.metadata.orm import DataManager
from src.metadata.stats import StatsProcessor

class test_stats_processor(TestCase):

    def setUp(self):
        # We need to set up a patch for the SQLITE_PATH module-level var
        sqlite_path = patch('src.metadata.orm.SQLITE_PATH', ':memory:')
        sqlite_path.start()
        self.mock_data_mgr = DataManager()
        self.stats_mgr = StatsProcessor(self.mock_data_mgr)

    def test_distrib(self):
        a = AssignedSubnet(Address('10.11.12.0'), 24, "foo")
        b = AssignedSubnet(Address('10.11.13.0'), 24, "foo")
        c = AssignedSubnet(Address('10.11.13.0'), 28, "foo")
        d = AssignedSubnet(Address('10.11.13.0'), 10, "foo")
        self.mock_data_mgr.update_records((a, b, c, d))

        count, lengths = self.stats_mgr.distribution()
        expected_distrib = {
            10: 1,
            28: 1,
            24: 2,
        }

        self.assertEquals(4, count)
        self.assertEquals(expected_distrib, lengths)

    def test_coverage(self):
        a = AssignedSubnet(Address('10.0.0.0'), 8, "foo")
        b = AssignedSubnet(Address('11.0.0.0'), 9, "foo")
        c = AssignedSubnet(Address('11.128.0.0'), 9, "foo")

        self.mock_data_mgr.update_records((a, b, c))

        total_coverage, coverage = self.stats_mgr.coverage()
        self.assertEquals(33554432, total_coverage)
        self.assertEquals('0.781', str(coverage))
