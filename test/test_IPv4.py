from unittest import TestCase

from src.net.IPv4 import Address, Subnet

class test_IPv4_Address(TestCase):

    unicast_str = '192.168.1.1'
    unicast_bytes = (192, 168, 1, 1)
    unicast_uint = 3232235777

    def test_no_argument(self):
        with self.assertRaises(TypeError):
            Address()

    def test_invalid_argument_type(self):
        with self.assertRaises(TypeError) as ex:
            Address(3.14)
        self.assertEqual(
            "Argument \"3.14\" of type \"float\" cannot be used to instantiate Address",str(ex.exception)
        )

    def test_valid_byte_tuple_in_constructor(self):
        a = Address(self.unicast_bytes)
        self.assertTrue(isinstance(a, Address))
        self.assertEqual("<IPv4 address: 192.168.1.1>", repr(a))
        self.assertEqual(self.unicast_uint, a._uint)

    def test_valid_byte_list_in_constructor(self):
        a = Address(list(self.unicast_bytes))
        self.assertTrue(isinstance(a, Address))
        self.assertEqual("<IPv4 address: 192.168.1.1>", repr(a))
        self.assertEqual(self.unicast_uint, a._uint)

    def test_valid_dotted_quad_str_in_constructor(self):
        a = Address(self.unicast_str)
        self.assertTrue(isinstance(a, Address))
        self.assertEqual("<IPv4 address: 192.168.1.1>", repr(a))
        self.assertEqual(self.unicast_uint, a._uint)

    def test_invalid_dotted_quad_str_in_constructor(self):
        with self.assertRaises(ValueError) as ex:
            Address("1.2.3.4.5")
        self.assertEqual("Invalid IPv4 address: \"1.2.3.4.5\"", str(ex.exception))

    def test_malformed_dotted_quad_str_in_constructor(self):
        with self.assertRaises(ValueError) as ex:
            Address("a.b.c.d")
        self.assertEqual("Invalid IPv4 address: \"a.b.c.d\"", str(ex.exception))

    def test_valid_uint_in_constructor(self):
        a = Address(self.unicast_uint)
        self.assertTrue(isinstance(a, Address))
        self.assertEqual("<IPv4 address: 192.168.1.1>", repr(a))
        self.assertEqual(self.unicast_uint, a._uint)

    def test_invalid_uint_in_constructor(self):
        with self.assertRaises(ValueError) as ex:
            Address(-42)
        self.assertEqual("Invalid IPv4 address uint32", str(ex.exception))

    def test_invalid_address_in_constructor(self):
        with self.assertRaises(ValueError):
            Address([192, 168, 1])
        with self.assertRaises(ValueError):
            Address([192, 168, 1, 1, 0])
        with self.assertRaises(ValueError):
            Address([292, 168, 1, 1])

    def test_equal(self):
        a=Address([0,0,0,0])
        b=Address(0)
        self.assertEqual(a, b)
        self.assertEqual(b, a)

    def test_not_equal(self):
        a=Address([10,0,0,0])
        b=Address(0)
        self.assertNotEqual(a, b)
        self.assertNotEqual(b, a)

    def test_invalid_comparisons(self):
        # Equality comparisons
        with self.assertRaises(TypeError):
            Address([192, 168, 1, 2]) != 'fdds'
        with self.assertRaises(TypeError):
            'foo' != Address([192, 168, 1, 2])
        with self.assertRaises(TypeError):
            Address([192, 168, 1, 2]) == 'fdds'
        with self.assertRaises(TypeError):
            'foo' == Address([192, 168, 1, 2])

        # Less-than comparisons
        with self.assertRaises(TypeError):
            Address([192, 168, 1, 2]) < 'fdds'
        with self.assertRaises(TypeError):
            'foo' < Address([192, 168, 1, 2])
        with self.assertRaises(TypeError):
            Address([192, 168, 1, 2]) <= 'fdds'
        with self.assertRaises(TypeError):
            'foo' <= Address([192, 168, 1, 2])

        # Greater-than comparisons
        with self.assertRaises(TypeError):
            Address([192, 168, 1, 2]) > 'fdds'
        with self.assertRaises(TypeError):
            'foo' > Address([192, 168, 1, 2])
        with self.assertRaises(TypeError):
            Address([192, 168, 1, 2]) >= 'fdds'
        with self.assertRaises(TypeError):
            'foo' >= Address([192, 168, 1, 2])

    def test_lt(self):
        self.assertLess(Address([10, 1, 1, 1]), Address([10, 1, 1, 2]))
        self.assertFalse(Address([10, 1, 1, 1]) < Address([10, 1, 1, 1]))
        self.assertLess(Address(0), Address([10, 1, 1, 2]))
        self.assertLess(Address(0), Address([255, 255, 255, 255]))

    def test_le(self):
        self.assertLessEqual(Address([10, 1, 1, 1]), Address([10, 1, 1, 2]))
        self.assertLessEqual(Address([10, 1, 1, 1]), Address([10, 1, 1, 1]))
        self.assertFalse(Address([1,2,3,4]) <= Address([1,2,3,3]))
        self.assertLessEqual(Address(0), Address([10, 1, 1, 2]))
        self.assertLessEqual(Address(0), Address([255, 255, 255, 255]))

    def test_gt(self):
        self.assertGreater(Address([10, 1, 1, 1]), Address([10, 1, 1, 0]))
        self.assertFalse(Address([0, 0, 0, 0]) > Address([10, 1, 1, 1]))
        self.assertGreater(Address([1, 1, 1, 1]), Address(0))
        self.assertGreater(Address([255, 255, 255, 255]), Address(0))

    def test_ge(self):
        self.assertGreaterEqual(Address([10, 1, 1, 3]), Address([10, 1, 1, 2]))
        self.assertGreaterEqual(Address([10, 1, 1, 1]), Address([10, 1, 1, 1]))
        self.assertFalse(Address([1,2,3,2]) >= Address([1,2,3,3]))
        self.assertGreaterEqual(Address([1, 1, 1, 1]), Address(0))
        self.assertGreaterEqual(Address([255, 255, 255, 255]), Address(0))

    def test_hashability(self):
        a = Address("10.0.0.0")
        b = Address("10.0.0.0")
        c = Address("11.0.0.0")
        self.assertEquals(hash(a), hash(b))
        self.assertFalse(a is b)
        s = set([a, b, c])

        self.assertEqual(2, len(s))
        self.assertEqual({a, c}, s)
        self.assertEqual({b, c}, s)

    def test_add_valid_increment(self):
        a = Address(self.unicast_str)
        a += 4
        self.assertEqual(Address("192.168.1.5"), a)

    def test_add_invalid_increment(self):
        a = Address(self.unicast_str)
        with self.assertRaises(TypeError) as ex:
            a += 4.5
        self.assertEqual(Address("192.168.1.1"), a)
        with self.assertRaises(TypeError) as ex:
            a += "hello"
        self.assertEqual(Address("192.168.1.1"), a)

        with self.assertRaises(ValueError) as ex:
            # That's a bit much
            a += 10**12
        self.assertEqual(Address("192.168.1.1"), a)

class test_IPv4_subnet(TestCase):
    net_address_bytes = (192, 168, 1, 1)
    broadcast_address_bytes = (192, 168, 255, 255)

    def test_valid_address_and_prefix_constructor(self):
        net = Address(self.net_address_bytes)
        sub = Subnet(net, 24)
        self.assertTrue(isinstance(sub, Subnet))

    def test_valid_net_address_and_broadcast_constructor(self):
        net = Address(self.net_address_bytes)
        broadcast = Address(self.broadcast_address_bytes)

        sub = Subnet(net, broadcast)
        self.assertTrue(isinstance(sub, Subnet))
        self.assertEqual(16, sub.prefix_length)

    def test_invalid_arguments_constructor(self):
        net = Address(self.net_address_bytes)
        with self.assertRaises(TypeError) as ex:
            sub = Subnet(net, "hello")
        self.assertEqual(
            "Arguments \"(<IPv4 address: 192.168.1.1>, 'hello')\" of types \"('Address', 'str')\" cannot be used to instantiate Subnet",
            str(ex.exception)
        )

    def test_repr(self):
        s = Subnet(Address([10,10,10,0]), 24)
        self.assertEqual("<IPv4 subnet: 10.10.10.0/24>", repr(s))

    def test_set_not_a_valid_network_address(self):
        s = Subnet(Address([8, 8, 8, 8]), 24)
        with self.assertRaises(TypeError):
            s == "I'm not a network address"

    def test_comparison_not_a_valid_network_address(self):
        with self.assertRaises(TypeError):
            Subnet("I'm not a network address", 24)

    def test_equal_same_network_same_mask(self):
        sa = Subnet(Address([192,168,42,0]), 24)
        sb = Subnet(Address([192,168,42,0]), 24)

        self.assertEqual(sa, sb)
        self.assertEqual(sb, sa)

    def test_equal_same_network_diff_mask(self):
        sa = Subnet(Address([192,168,42,0]), 24)
        sb = Subnet(Address([192,168,42,0]), 23)

        self.assertNotEqual(sa, sb)
        self.assertNotEqual(sb, sa)

    def test_equal_diff_network_same_mask(self):
        sa = Subnet(Address([192,168,41,0]), 24)
        sb = Subnet(Address([192,168,42,0]), 24)

        self.assertNotEqual(sa, sb)
        self.assertNotEqual(sb, sa)

    def test_equal_diff_network_diff_mask(self):
        sa = Subnet(Address([192,168,41,0]), 24)
        sb = Subnet(Address([192,168,42,0]), 23)

        self.assertNotEqual(sa, sb)
        self.assertNotEqual(sb, sa)

    def test_mask(self):
        s=Subnet(Address([192, 168, 42, 0]), 1)
        self.assertEqual(s.netmask, 2147483648)

        s=Subnet(Address([192, 168, 42, 0]), 2)
        self.assertEqual(s.netmask, 3221225472)

        s=Subnet(Address([192, 168, 42, 0]), 32)
        self.assertEqual(s.netmask, 4294967295)

    def test_floor(self):
        network_address = Address([192, 168, 42, 0])
        s=Subnet(network_address, 24)
        self.assertEqual(s.floor(), network_address)
        mid_subnet_address = Address([192, 168, 42, 132])
        s=Subnet(mid_subnet_address, 24)
        self.assertEqual(s.floor(), network_address)

    def test_ceiling(self):
        network_address = Address([192, 168, 42, 0])
        s=Subnet(network_address, 24)
        self.assertEqual(s.ceiling(), Address([192, 168, 42, 255]))

        s=Subnet(network_address, 16)
        self.assertEqual(s.ceiling(), Address([192, 168, 255, 255]))

        s=Subnet(network_address, 20)
        self.assertEqual(s.ceiling(), Address([192, 168, 47, 255]))

    def test_inclusion_single(self):
        a=Address([192,168,42,45])

        network_address = Address([192, 168, 42, 0])
        s=Subnet(network_address, 24)
        self.assertIn(a, s)

        a=Address([192,168,42,255])
        self.assertIn(a, s)

        a=Address([192,168,42,0])
        self.assertIn(a, s)

        a=Address([192,168,43,0])
        self.assertNotIn(a, s)

        a=Address([192,168,41,255])
        self.assertNotIn(a, s)

        a=Address([0,0,0,0])
        self.assertNotIn(a, s)

        a=Address([255,255,255,255])
        self.assertNotIn(a, s)

    def test_inclusion_subnet(self):

        network_address = Address([192, 168, 42, 0])
        s=Subnet(network_address, 24)

        self.assertIn(s, s)

        network_address = Address([192, 168, 42, 0])
        t=Subnet(network_address, 25)

        self.assertIn(t, s)
        self.assertNotIn(s, t)

    def test_contains_bad_type(self):
        a=Address([192,168,42,0])
        s=Subnet(a, 24)
        with self.assertRaises(TypeError):
            'foo' in s

    def test_left_shift(self):
        a=Address([192,168,42,0])
        s=Subnet(a, 24)

        expected = Subnet(a, 23)
        self.assertEqual(expected, s << 1)

        with self.assertRaises(ValueError) as ex:
            s << 25
        self.assertEqual("Prefix length has to be between 0 and 32", str(ex.exception))

    def test_right_shift(self):
        a=Address([192,168,42,0])
        s=Subnet(a, 24)

        expected = Subnet(a, 25)
        self.assertEqual(expected, s >> 1)

        with self.assertRaises(ValueError) as ex:
            s >> 9
        self.assertEqual("Prefix length has to be between 0 and 32", str(ex.exception))
