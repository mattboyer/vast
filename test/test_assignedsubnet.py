from unittest import TestCase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.metadata.assigned import AssignedSubnet
from src.net.IPv4 import Address, Subnet
from src.metadata.orm import get_dec_base

class test_assigned_subnet(TestCase):

    def setUp(self):
        # Let's initialise a SQLite in-memory engine
        self.engine = create_engine('sqlite:///:memory:')
        sa_base = get_dec_base()
        sa_base.metadata.create_all(self.engine)
        session_factory = sessionmaker(bind=self.engine)
        self.session = session_factory()
        self.session.commit()

    def test_polymorphism(self):
        start_address = Address('10.0.0.0')
        end_address = Address('10.255.255.255')
        su = Subnet(start_address, 8)
        # 1st call: AssignedSubnet.__new__
        ass = AssignedSubnet(start_address, end_address, 'IETF')
        self.assertEquals(AssignedSubnet, type(ass))
        self.assertTrue(isinstance(ass, AssignedSubnet))
        self.assertTrue(isinstance(ass, Subnet))

    def test_exception_on_empty_name(self):
        start_address = Address('10.0.0.0')
        end_address = Address('10.255.255.255')
        su = Subnet(start_address, 8)
        with self.assertRaises(ValueError) as ex:
            AssignedSubnet(start_address, end_address, '')

        self.assertEqual("AssignedSubnet name can't be empty", str(ex.exception))

    def test_relationships_next(self):

        subnet_a = AssignedSubnet(Address('10.0.0.0'), 8, "alpha")
        subnet_b = AssignedSubnet(Address('11.0.0.0'), 8, "beta")
        subnet_c = AssignedSubnet(Address('12.0.0.0'), 8, "gamma")
        all_subs = (subnet_a, subnet_b, subnet_c)

        self.session.add_all(all_subs)
        self.session.commit()

        # This should set both next on A and previous on B
        subnet_a.next = subnet_b
        self.session.add_all(all_subs)
        self.session.commit()

        self.assertEquals(subnet_a.next_subnet_id, 2)
        self.assertEquals(subnet_a.next, subnet_b)
        self.assertTrue(subnet_a.next is subnet_b)
        self.assertEquals(subnet_a.previous, None)

        self.assertEquals(subnet_b.next_subnet_id, None)
        self.assertEquals(subnet_b.next, None)
        self.assertEquals(subnet_b.previous, subnet_a)
        self.assertTrue(subnet_b.previous is subnet_a)

        self.assertEquals(subnet_c.next_subnet_id, None)
        self.assertEquals(subnet_c.next, None)
        self.assertEquals(subnet_c.previous, None)

        # TODO Set next directly
        subnet_b.next = subnet_c
        subnet_b.next = subnet_c
        self.session.add_all(all_subs)
        self.session.commit()

        # Nothing new here!
        self.assertEquals(subnet_a.next_subnet_id, 2)
        self.assertEquals(subnet_a.next, subnet_b)
        self.assertTrue(subnet_a.next is subnet_b)
        self.assertEquals(subnet_a.previous, None)

        # Subnet B knows who comes before it and who comes after it
        self.assertEquals(subnet_b.next_subnet_id, 3)
        self.assertEquals(subnet_b.next, subnet_c)
        self.assertTrue(subnet_b.next is subnet_c)
        self.assertEquals(subnet_b.previous, subnet_a)
        self.assertTrue(subnet_b.previous is subnet_a)

        self.assertEquals(subnet_c.next_subnet_id, None)
        self.assertEquals(subnet_c.next, None)
        self.assertEquals(subnet_c.previous, subnet_b)
        self.assertTrue(subnet_c.previous is subnet_b)

    def test_relationships_previous(self):

        subnet_a = AssignedSubnet(Address('10.0.0.0'), 8, "alpha")
        subnet_b = AssignedSubnet(Address('11.0.0.0'), 8, "beta")
        subnet_c = AssignedSubnet(Address('12.0.0.0'), 8, "gamma")
        all_subs = (subnet_a, subnet_b, subnet_c)

        self.session.add_all(all_subs)
        self.session.commit()

        # This should set both previous on B and next on A
        subnet_b.previous = subnet_a
        self.session.add_all(all_subs)
        self.session.commit()

        self.assertEquals(subnet_a.next_subnet_id, 2)
        self.assertEquals(subnet_a.next, subnet_b)
        self.assertTrue(subnet_a.next is subnet_b)
        self.assertEquals(subnet_a.previous, None)

        self.assertEquals(subnet_b.next_subnet_id, None)
        self.assertEquals(subnet_b.next, None)
        self.assertEquals(subnet_b.previous, subnet_a)
        self.assertTrue(subnet_b.previous is subnet_a)

        self.assertEquals(subnet_c.next_subnet_id, None)
        self.assertEquals(subnet_c.next, None)
        self.assertEquals(subnet_c.previous, None)

        subnet_c.previous = subnet_b
        self.session.add_all(all_subs)
        self.session.commit()

        # Nothing new here!
        self.assertEquals(subnet_a.next_subnet_id, 2)
        self.assertEquals(subnet_a.next, subnet_b)
        self.assertTrue(subnet_a.next is subnet_b)
        self.assertEquals(subnet_a.previous, None)

        # Subnet B knows who comes before it and who comes after it
        self.assertEquals(subnet_b.next_subnet_id, 3)
        self.assertEquals(subnet_b.next, subnet_c)
        self.assertTrue(subnet_b.next is subnet_c)
        self.assertEquals(subnet_b.previous, subnet_a)
        self.assertTrue(subnet_b.previous is subnet_a)

        self.assertEquals(subnet_c.next_subnet_id, None)
        self.assertEquals(subnet_c.next, None)
        self.assertEquals(subnet_c.previous, subnet_b)
        self.assertTrue(subnet_c.previous is subnet_b)

    def test_relationships_parent(self):

        subnet_a = AssignedSubnet(Address('10.0.0.0'), 8, "small")
        subnet_b = AssignedSubnet(Address('11.0.0.0'), 8, "small")
        subnet_c = AssignedSubnet(Address('10.0.0.0'), 7, "big")
        all_subs = (subnet_a, subnet_b, subnet_c)

        self.session.add_all(all_subs)
        self.session.commit()

        # This should set both next on A and previous on B
        subnet_a.parent = subnet_c
        self.session.add_all(all_subs)
        self.session.commit()

        self.assertEquals(subnet_a.parent_subnet_id, 3)
        self.assertEquals(subnet_a.parent, subnet_c)
        self.assertTrue(subnet_a.parent is subnet_c)

        self.assertTrue(subnet_a in subnet_c.children)
        self.assertEquals([subnet_a], subnet_c.children)

        subnet_c.children.append(subnet_b)
        self.session.add_all(all_subs)
        self.session.commit()

        self.assertEquals(subnet_b.parent_subnet_id, 3)
        self.assertEquals(subnet_b.parent, subnet_c)
        self.assertTrue(subnet_b.parent is subnet_c)

        self.assertTrue(subnet_a in subnet_c.children)
        self.assertEquals([subnet_a, subnet_b], subnet_c.children)
