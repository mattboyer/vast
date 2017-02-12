from unittest import TestCase
from mock import patch, Mock, call

from src.metadata.assigned import AssignedSubnet
from src.net.IPv4 import Subnet, Address
from src.metadata.orm import get_dec_base, DataManager

class test_data_mgr(TestCase):

    def setUp(self):
        self._data_mgr_sqlite_patch = patch('src.metadata.orm.SQLITE_PATH', ':memory:')
        self._data_mgr_sqlite_patch.start()
        self.data_mgr = DataManager()

    def tearDown(self):
        self._data_mgr_sqlite_patch.stop()

    def test_all_subnets(self):
        subnet_b = AssignedSubnet(Address('11.0.0.0'), 8, "bravo")
        subnet_a = AssignedSubnet(Address('10.0.0.0'), 8, "alpha")
        subnet_c = AssignedSubnet(Address('10.0.0.0'), 7, "charlie")
        subnet_a.next = subnet_b
        subnet_b.previous = subnet_a
        subnet_a.parent = subnet_c
        subnet_b.parent = subnet_c

        all_subs = (subnet_a, subnet_b, subnet_c)
        self.data_mgr.update_records(all_subs)

        self.assertTrue(subnet_a in self.data_mgr.all_records())
        self.assertTrue(subnet_b in self.data_mgr.all_records())
        self.assertTrue(subnet_c in self.data_mgr.all_records())

    def test_fine_subnets(self):
        subnet_b = AssignedSubnet(Address('11.0.0.0'), 8, "bravo")
        subnet_a = AssignedSubnet(Address('10.0.0.0'), 8, "alpha")
        subnet_c = AssignedSubnet(Address('10.0.0.0'), 7, "charlie")

        all_subs = (subnet_b, subnet_a, subnet_c)
        self.data_mgr.update_records(all_subs)

        self.assertTrue(subnet_a in self.data_mgr.fine_subnet_iter())
        self.assertTrue(subnet_b in self.data_mgr.fine_subnet_iter())
        self.assertFalse(subnet_c in self.data_mgr.fine_subnet_iter())
        self.assertEquals([subnet_a, subnet_b], list(self.data_mgr.fine_subnet_iter()))

    def test_reduce_subnets(self):
        subnet_b = AssignedSubnet(Address('11.0.0.0'), 8, "bravo")
        subnet_a = AssignedSubnet(Address('10.0.0.0'), 8, "alpha")
        subnet_c = AssignedSubnet(Address('10.0.0.0'), 7, "charlie")

        subnet_d = AssignedSubnet(Address('13.0.0.0'), 8, "delta")

        subnet_e = AssignedSubnet(Address('15.0.0.0'), 8, "echo")
        subnet_f = AssignedSubnet(Address('16.0.0.0'), 8, "foxtrot")

        all_subs = (subnet_b, subnet_a, subnet_c, subnet_d, subnet_e, subnet_f)
        self.data_mgr.update_records(all_subs)

        contig = self.data_mgr.group_contiguous_subnets()
        self.assertEquals(
            [[subnet_a, subnet_b], [subnet_d], [subnet_e, subnet_f]],
            contig
        )
