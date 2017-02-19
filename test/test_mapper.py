from unittest import TestCase
from mock import patch, Mock, call

from src.metadata import ResolutionException
from src.metadata.assigned import AssignedSubnet
from src.metadata.mapper import SubnetMapper
from src.metadata.orm import DataManager
from src.net.IPv4 import Address, Subnet

class test_Mapper(TestCase):

    def setUp(self):
        # We need to set up a patch for the SQLITE_PATH module-level var
        sqlite_path = patch('src.metadata.orm.SQLITE_PATH', ':memory:')
        sqlite_path.start()
        self.mock_data_mgr = DataManager()

        # We want to mock the actual resolver
        self._resolver_mock = Mock()
        self._resolve_mock = Mock()
        self._resolver_mock.resolve = self._resolve_mock

        self.resolver_patch = patch('src.metadata.mapper.DelegationResolver', Mock(return_value=self._resolver_mock))
        self.resolver_patch.start()
        self.mapper = SubnetMapper(self.mock_data_mgr)

    def test_contiguous_subnets(self):
        start_address = Address((10, 0, 0, 0))
        a = AssignedSubnet(Address("10.0.0.0"), 8, "alpha")
        b = AssignedSubnet(Address("11.0.0.0"), 24, "bravo")
        c = AssignedSubnet(Address("11.0.1.0"), 24, "charlie")

        self._resolve_mock.side_effect = [
            a, b, c, ResolutionException,
        ]
        self.mapper.scan_up(start_address)

        # Have we got the subnets we expect?
        self.assertEqual(
            [
                call(Subnet(Address("10.0.0.0"), 32)),
                call(Subnet(Address("11.0.0.0"), 32)),
                call(Subnet(Address("11.0.1.0"), 32)),
                call(Subnet(Address("11.0.2.0"), 32)),
            ],
            self._resolve_mock.mock_calls
        )

        # Are they saved to the DB?
        self.assertEqual(
            [a, b, c],
            [s for s in self.mock_data_mgr.all_records().order_by(AssignedSubnet.mapped_network)],
        )
