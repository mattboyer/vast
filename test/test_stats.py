from mock import patch, Mock, call
from unittest import TestCase

from src.net.IPv4 import Address, Subnet
from src.metadata.assigned import AssignedSubnet
from src.metadata.orm import DataManager
from src.metadata.stats import StatsManager

class test_stats_manager(TestCase):

    def setUp(self):
        # We need to set up a patch for the SQLITE_PATH module-level var
        sqlite_path = patch('src.metadata.orm.SQLITE_PATH', ':memory:')
        sqlite_path.start()
        self.mock_data_mgr = DataManager()
        self.stats_mgr = StatsManager(self.mock_data_mgr)

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
