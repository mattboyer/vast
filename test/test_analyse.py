from unittest import TestCase
from mock import patch, Mock, call

from src.metadata.assigned import AssignedSubnet
from src.metadata.linker import SubnetLinker
from src.metadata.orm import DataManager
from src.net.IPv4 import Address

class test_Analyser(TestCase):

    def setUp(self):
        # We need to set up a patch for the SQLITE_PATH module-level var
        sqlite_path = patch('src.metadata.orm.SQLITE_PATH', ':memory:')
        sqlite_path.start()
        self.mock_data_mgr = DataManager()
        self.linker = SubnetLinker(self.mock_data_mgr)

    def test_contiguous_subnets(self):
        a = AssignedSubnet(Address('10.11.12.0'), 24, "foo")
        b = AssignedSubnet(Address('10.11.13.0'), 24, "foo")
        self.mock_data_mgr.update_records((a, b))

        self.assertIsNone(a.next)
        self.assertIsNone(a.previous)
        self.assertIsNone(a.parent)
        self.assertIsNone(b.next)
        self.assertIsNone(b.previous)
        self.assertIsNone(b.parent)

        self.linker.link()

        self.assertEqual(a.next, b)
        self.assertEqual(b.previous, a)
        # The rest is unchanged
        self.assertIsNone(a.previous)
        self.assertIsNone(a.parent)
        self.assertIsNone(b.next)
        self.assertIsNone(b.parent)

    def test_contiguous_subnets_reverse_order(self):
        a = AssignedSubnet(Address('10.11.13.0'), 24, "foo")
        b = AssignedSubnet(Address('10.11.12.0'), 24, "foo")
        self.mock_data_mgr.update_records((a, b))

        self.assertIsNone(a.next)
        self.assertIsNone(a.previous)
        self.assertIsNone(a.parent)
        self.assertIsNone(b.next)
        self.assertIsNone(b.previous)
        self.assertIsNone(b.parent)

        self.linker.link()

        self.assertEqual(a.previous, b)
        self.assertEqual(b.next, a)
        # The rest is unchanged
        self.assertIsNone(a.next)
        self.assertIsNone(a.parent)
        self.assertIsNone(b.previous)
        self.assertIsNone(b.parent)
