from unittest import TestCase
from mock import patch

from src.metadata.assigned import AssignedSubnet
from src.metadata.linker import SubnetLinker
from src.metadata.orm import DataManager
from src.net.IPv4 import Address

class test_Linker(TestCase):

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

    def test_disjointed_contiguous_subnets(self):
        a = AssignedSubnet(Address('10.11.12.0'), 24, "foo")
        b = AssignedSubnet(Address('10.11.13.0'), 24, "foo")
        c = AssignedSubnet(Address('10.11.25.0'), 24, "foo")
        d = AssignedSubnet(Address('10.11.42.0'), 24, "foo")
        e = AssignedSubnet(Address('10.11.43.0'), 24, "foo")
        self.mock_data_mgr.update_records((a, b, c, d, e))

        self.assertIsNone(a.next)
        self.assertIsNone(a.previous)
        self.assertIsNone(a.parent)
        self.assertIsNone(b.next)
        self.assertIsNone(b.previous)
        self.assertIsNone(b.parent)
        self.assertIsNone(c.next)
        self.assertIsNone(c.previous)
        self.assertIsNone(c.parent)
        self.assertIsNone(d.next)
        self.assertIsNone(d.previous)
        self.assertIsNone(d.parent)
        self.assertIsNone(e.next)
        self.assertIsNone(e.previous)
        self.assertIsNone(e.parent)

        self.linker.link()

        self.assertEqual(a.next, b)
        self.assertEqual(b.previous, a)
        self.assertEqual(d.next, e)
        self.assertEqual(e.previous, d)
        # The rest is unchanged
        self.assertIsNone(a.previous)
        self.assertIsNone(a.parent)
        # In particular, we don't join disjointed sequences of subnets
        self.assertIsNone(b.next)
        self.assertIsNone(b.parent)
        self.assertIsNone(c.next)
        self.assertIsNone(c.previous)
        self.assertIsNone(c.parent)
        self.assertIsNone(d.previous)
        self.assertIsNone(d.parent)
        self.assertIsNone(e.next)
        self.assertIsNone(e.parent)

    def test_parent_subnets(self):
        a = AssignedSubnet(Address('10.11.12.0'), 24, "child")
        b = AssignedSubnet(Address('10.11.0.0'), 16, "parent")
        self.mock_data_mgr.update_records((a, b))

        self.assertIsNone(a.next)
        self.assertIsNone(a.previous)
        self.assertIsNone(a.parent)
        self.assertIsNone(b.next)
        self.assertIsNone(b.previous)
        self.assertIsNone(b.parent)

        self.linker.link()

        self.assertEqual(a.parent, b)
        # The rest is unchanged
        self.assertIsNone(a.next)
        self.assertIsNone(a.previous)
        self.assertIsNone(b.next)
        self.assertIsNone(b.previous)
        self.assertIsNone(b.parent)
