from unittest import TestCase
from mock import patch

from src.metadata.assigned import AssignedSubnet
from src.metadata.mapper import SubnetMapper
from src.metadata.orm import DataManager
from src.net.IPv4 import Address

class test_Mapper(TestCase):

    def setUp(self):
        # We need to set up a patch for the SQLITE_PATH module-level var
        sqlite_path = patch('src.metadata.orm.SQLITE_PATH', ':memory:')
        sqlite_path.start()
        self.mock_data_mgr = DataManager()
        self.mapper = SubnetMapper(self.mock_data_mgr)

    def test_contiguous_subnets(self):
        pass
