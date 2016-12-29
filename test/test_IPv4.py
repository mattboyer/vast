from unittest import TestCase, skip

from src.net.IPv4 import Address, Subnet

class test_IPv4_Address(TestCase):

    def setUp(self):
        self.unicast_str = '192.168.1.1'
        self.unicast_bytes = (192, 168, 1, 1)
        self.unicast_uint = 3232235777

    def test_no_argument(self):
        with self.assertRaises(TypeError):
            Address()

    def test_valid_byte_tuple_in_constructor(self):
        a = Address(self.unicast_bytes)
        self.assertTrue(isinstance(a, Address))
        self.assertEquals("<IPv4 address: 192.168.1.1>", repr(a))
        self.assertEquals(self.unicast_uint, a._uint)

    def test_valid_byte_list_in_constructor(self):
        a = Address(list(self.unicast_bytes))
        self.assertTrue(isinstance(a, Address))
        self.assertEquals("<IPv4 address: 192.168.1.1>", repr(a))
        self.assertEquals(self.unicast_uint, a._uint)

    def test_valid_dotted_quad_str_in_constructor(self):
        a = Address(self.unicast_str)
        self.assertTrue(isinstance(a, Address))
        self.assertEquals("<IPv4 address: 192.168.1.1>", repr(a))
        self.assertEquals(self.unicast_uint, a._uint)

    def test_valid_uint_in_constructor(self):
        a = Address(self.unicast_uint)
        self.assertTrue(isinstance(a, Address))
        self.assertEquals("<IPv4 address: 192.168.1.1>", repr(a))
        self.assertEquals(self.unicast_uint, a._uint)

    def test_invalid_address_in_constructor(self):
        with self.assertRaises(ValueError):
            Address([192, 168, 1])
        with self.assertRaises(ValueError):
            Address([192, 168, 1, 1, 0])
        with self.assertRaises(ValueError):
            Address([292, 168, 1, 1])

    @skip
    def test_equal(self):
        a=Address([0,0,0,0])
        b=Address()
        self.assertEquals(a, b)
        self.assertEquals(b, a)

    @skip
    def test_not_equal(self):
        a=Address([10,0,0,0])
        b=Address()
        self.assertNotEquals(a, b)
        self.assertNotEquals(b, a)

    @skip
    def test_invalid_comparisons(self):
        with self.assertRaises(TypeError):
            Address([192, 168, 1, 2]) != 'fdds'
        with self.assertRaises(TypeError):
            'foo' != Address([192, 168, 1, 2])
        with self.assertRaises(TypeError):
            Address([192, 168, 1, 2]) == 'fdds'
        with self.assertRaises(TypeError):
            'foo' == Address([192, 168, 1, 2])

        with self.assertRaises(TypeError):
            Address([192, 168, 1, 2]) < 'fdds'
        with self.assertRaises(TypeError):
            'foo' < Address([192, 168, 1, 2])
        with self.assertRaises(TypeError):
            Address([192, 168, 1, 2]) <= 'fdds'
        with self.assertRaises(TypeError):
            'foo' <= Address([192, 168, 1, 2])

        with self.assertRaises(TypeError):
            Address([192, 168, 1, 2]) > 'fdds'
        with self.assertRaises(TypeError):
            'foo' > Address([192, 168, 1, 2])
        with self.assertRaises(TypeError):
            Address([192, 168, 1, 2]) >= 'fdds'
        with self.assertRaises(TypeError):
            'foo' >= Address([192, 168, 1, 2])

    @skip
    def test_lt(self):
        self.assertLess(Address([10, 1, 1, 1]), Address([10, 1, 1, 2]))
        self.assertFalse(Address([10, 1, 1, 1]) < Address([10, 1, 1, 1]))
        self.assertLess(Address([]), Address([10, 1, 1, 2]))
        self.assertLess(Address([]), Address([255, 255, 255, 255]))

    @skip
    def test_le(self):
        self.assertLessEqual(Address([10, 1, 1, 1]), Address([10, 1, 1, 2]))
        self.assertLessEqual(Address([10, 1, 1, 1]), Address([10, 1, 1, 1]))
        self.assertFalse(Address([1,2,3,4]) <= Address([1,2,3,3]))
        self.assertLessEqual(Address([]), Address([10, 1, 1, 2]))
        self.assertLessEqual(Address([]), Address([255, 255, 255, 255]))

    @skip
    def test_gt(self):
        self.assertGreater(Address([10, 1, 1, 1]), Address([10, 1, 1, 0]))
        self.assertFalse(Address([0, 0, 0, 0]) > Address([10, 1, 1, 1]))
        self.assertGreater(Address([1, 1, 1, 1]), Address([]))
        self.assertGreater(Address([255, 255, 255, 255]), Address())

    @skip
    def test_ge(self):
        self.assertGreaterEqual(Address([10, 1, 1, 3]), Address([10, 1, 1, 2]))
        self.assertGreaterEqual(Address([10, 1, 1, 1]), Address([10, 1, 1, 1]))
        self.assertFalse(Address([1,2,3,2]) >= Address([1,2,3,3]))
        self.assertGreaterEqual(Address([1, 1, 1, 1]), Address([]))
        self.assertGreaterEqual(Address([255, 255, 255, 255]), Address())




class test_IPv4_subnet(TestCase):

    @skip
    def test_subnet_constructor(self):
        s = Subnet()
        self.assertEquals("IPv4 subnet: 0.0.0.0/0", repr(s))


    @skip
    def test_set(self):
        s = Subnet()
        s.set(Address([10,10,10,0]), 24)
        self.assertEquals("IPv4 subnet: 10.10.10.0/24", repr(s))


    @skip
    def test_set_not_a_valid_network_address(self):
        s = Subnet()
        with self.assertRaises(TypeError):
            s == "I'm not a network address"

    @skip
    def test_comparison_not_a_valid_network_address(self):
        s = Subnet()
        with self.assertRaises(TypeError):
            s.set("I'm not a network address", 24)

    @skip
    def test_equal_same_network_same_mask(self):
        sa = Subnet()
        sa.set(Address([192,168,42,0]), 24)

        sb = Subnet()
        sb.set(Address([192,168,42,0]), 24)
        self.assertEquals(sa, sb)
        self.assertEquals(sb, sa)

    @skip
    def test_equal_same_network_diff_mask(self):
        sa = Subnet()
        sa.set(Address([192,168,42,0]), 24)

        sb = Subnet()
        sb.set(Address([192,168,42,0]), 23)
        self.assertNotEquals(sa, sb)
        self.assertNotEquals(sb, sa)

    @skip
    def test_equal_diff_network_same_mask(self):
        sa = Subnet()
        sa.set(Address([192,168,41,0]), 24)

        sb = Subnet()
        sb.set(Address([192,168,42,0]), 24)
        self.assertNotEquals(sa, sb)
        self.assertNotEquals(sb, sa)

    @skip
    def test_equal_diff_network_diff_mask(self):
        sa = Subnet()
        sa.set(Address([192,168,41,0]), 24)

        sb = Subnet()
        sb.set(Address([192,168,42,0]), 23)
        self.assertNotEquals(sa, sb)
        self.assertNotEquals(sb, sa)

    @skip
    def test_mask(self):
        s=Subnet()
        s.set(Address([192, 168, 42, 0]), 1)
        self.assertEquals(s.mask_uint32(), 2147483648)
        s.set(Address([192, 168, 42, 0]), 2)
        self.assertEquals(s.mask_uint32(), 3221225472)
        s.set(Address([192, 168, 42, 0]), 32)
        self.assertEquals(s.mask_uint32(), 4294967295)


    @skip
    def test_floor(self):
        s=Subnet()
        network_address = Address([192, 168, 42, 0])
        s.set(network_address, 24)
        self.assertEquals(s.floor(), network_address)
        mid_subnet_address = Address([192, 168, 42, 132])
        s.set(mid_subnet_address, 24)
        self.assertEquals(s.floor(), network_address)

    @skip
    def test_ceiling(self):
        s=Subnet()
        network_address = Address([192, 168, 42, 0])
        s.set(network_address, 24)
        self.assertEquals(s.ceiling(), Address([192, 168, 42, 255]))

        s.set(network_address, 16)
        self.assertEquals(s.ceiling(), Address([192, 168, 255, 255]))

        s.set(network_address, 20)
        self.assertEquals(s.ceiling(), Address([192, 168, 47, 255]))

    @skip
    def test_inclusion_single(self):
        a=Address([192,168,42,45])

        s=Subnet()
        network_address = Address([192, 168, 42, 0])
        s.set(network_address, 24)
        self.assertIn(a, s)

        a=Address([192,168,42,255])
        self.assertIn(a, s)

        a=Address([192,168,42,0])
        self.assertNotIn(a, s)

        a=Address([192,168,43,0])
        self.assertNotIn(a, s)

        a=Address([192,168,41,255])
        self.assertNotIn(a, s)

        a=Address([0,0,0,0])
        self.assertNotIn(a, s)

        a=Address([255,255,255,255])
        self.assertNotIn(a, s)

    @skip
    def test_inclusion_subnet(self):

        s=Subnet()
        network_address = Address([192, 168, 42, 0])
        s.set(network_address, 24)

        self.assertIn(s, s)

        t=Subnet()
        network_address = Address([192, 168, 42, 0])
        t.set(network_address, 25)

        self.assertIn(t, s)
        self.assertNotIn(s, t)

    @skip
    def test_contains_bad_type(self):
        s=Subnet()
        a=Address([192,168,42,0])
        s.set(a, 24)
        with self.assertRaises(TypeError):
            'foo' in s
