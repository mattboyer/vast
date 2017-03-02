'''
IPv4 address space entities
'''


class Address(object):
    '''
    Models a single IPv4 address.
    '''

    def __init__(self, arg):
        self._uint = None

        if isinstance(arg, int):
            self._from_uint(arg)
        elif isinstance(arg, Address):
            self._from_uint(int(arg))
        elif isinstance(arg, str):
            self._from_string(arg)
        else:
            try:
                if iter(arg):
                    self._from_byte_seq(arg)
            except TypeError:
                raise TypeError(
                    "Argument \"{0}\" of type \"{1}\" cannot be used to "
                    "instantiate {2}".format(
                        arg,
                        type(arg).__name__,
                        self.__class__.__name__
                    )
                )

    def _from_uint(self, address_uint):
        if not (address_uint >= 0 and address_uint <= (2**32 - 1)):
            raise ValueError("Invalid IPv4 address uint32")

        # All the other class methods lead here
        self._uint = address_uint

    def _from_string(self, dotted_quad):
        try:
            split_quad = dotted_quad.split('.')
            if 4 != len(split_quad):
                raise Exception
            if not all(q.isdecimal() for q in split_quad):
                raise Exception

            byte_seq = [int(q) for q in split_quad]
        except Exception:
            raise ValueError(
                "Invalid IPv4 address: \"{0}\"".format(dotted_quad)
            )

        self._from_byte_seq(byte_seq)

    def _from_byte_seq(self, byte_seq):
        if 4 != len(byte_seq) or \
                not all(byte >= 0 and byte <= 255 for byte in byte_seq):
            raise ValueError("Invalid IPv4 address byte sequence: {0}".format(
                byte_seq))

        address_as_int = byte_seq[0] << 24
        address_as_int += byte_seq[1] << 16
        address_as_int += byte_seq[2] << 8
        address_as_int += byte_seq[3]

        self._from_uint(address_as_int)

    def __bytes__(self):
        byte_seq = []
        byte_seq.append(int(self) >> 24 & 0xFF)
        byte_seq.append(int(self) >> 16 & 0xFF)
        byte_seq.append(int(self) >> 8 & 0xFF)
        byte_seq.append(int(self) & 0xFF)
        return bytes(byte_seq)

    def __int__(self):
        return self._uint

    def __str__(self):
        return ".".join(str(b) for b in bytes(self))

    def __hash__(self):
        return hash(int(self))

    def __eq__(self, other_IP):
        try:
            return self._uint == int(other_IP)
        except ValueError:
            raise TypeError("Can only compare {0} to {0}".format(
                self.__class__.__name__
            ))

    def __ne__(self, other_IP):
        try:
            return self._uint != int(other_IP)
        except ValueError:
            raise TypeError("Can only compare {0} to {0}".format(
                self.__class__.__name__
            ))

    def __lt__(self, other_IP):
        try:
            return self._uint < int(other_IP)
        except ValueError:
            raise TypeError("Can only compare IPv4 to IPv4")

    def __le__(self, other_IP):
        try:
            return self._uint <= int(other_IP)
        except ValueError:
            raise TypeError("Can only compare IPv4 to IPv4")

    def __gt__(self, other_IP):
        try:
            return self._uint > int(other_IP)
        except ValueError:
            raise TypeError("Can only compare IPv4 to IPv4")

    def __ge__(self, other_IP):
        try:
            return self._uint >= int(other_IP)
        except ValueError:
            raise TypeError("Can only compare IPv4 to IPv4")

    def __add__(self, increment):
        try:
            return Address(self._uint + increment)
        except:
            raise

    def __and__(self, mask_bytes):
        """
        mask_bytes should be a big old uint32
        """

        return Address(self._uint & mask_bytes)

    def __repr__(self):
        return "<IPv4 address: {0}>".format(self)


# TODO Consistently use the term "prefix length"
class Subnet(object):
    '''Models a CIDR IPv4 subnet.'''

    def __init__(self, arg1, arg2):
        # TODO We need a copy constructor!!!!
        # Set private attributes in the constructor, just so they're there.
        self._network = None
        self._prefix_length = None

        if isinstance(arg1, Address) and isinstance(arg2, int):
            self._from_address_and_prefix_length(arg1, arg2)
        elif isinstance(arg1, Address) and isinstance(arg2, Address):
            self._from_start_and_end(arg1, arg2)
        else:
            raise TypeError(
                "Arguments \"{0}\" of types \"{1}\" cannot be used to "
                "instantiate {2}".format(
                    str((arg1, arg2)),
                    str((type(arg1).__name__, type(arg2).__name__)),
                    Subnet.__name__
                )
            )

    def _from_address_and_prefix_length(self, address, prefix_len):
        if not (prefix_len <= 32 and prefix_len >= 0):
            raise ValueError("Prefix length has to be between 0 and 32")

        self._prefix_length = prefix_len

        network_address = Address(address)
        mask = ~((2 ** (32 - prefix_len)) - 1)
        network_address &= mask
        self._network = network_address

    def _from_start_and_end(self, network, broadcast):
        # start is the network address, end is the broadcast address
        host_bits = int(network) ^ int(broadcast)

        prefix_len = 32
        while host_bits:
            host_bits >>= 1
            prefix_len -= 1

        self._from_address_and_prefix_length(network, prefix_len)

    def __rshift__(self, mask_decrement):
        rval = Subnet(self._network, self._prefix_length + mask_decrement)
        return rval

    def __lshift__(self, mask_decrement):
        rval = Subnet(self._network, self._prefix_length - mask_decrement)
        return rval

    def __mod__(self, new_mask):
        rval = Subnet(self._network, new_mask)
        return rval

    def __eq__(self, other):
        try:
            return (self._network == other.network) and \
                    (self._prefix_length == other.prefix_length)
        except AttributeError:
            raise TypeError("Can only compare {0} to {0}".format(
                self.__class__.__name__
            ))

    def __hash__(self):
        return hash(
            (int(self._network), self._prefix_length)
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "<IPv4 subnet: {0}/{1}>".format(
            str(self._network), self._prefix_length
        )

    def __len__(self):
        # We care about all addresses in the subnet, including the network and
        # broadcast address
        return 2 ** (32 - self._prefix_length)

    def mask_uint32(self):
        return Subnet._mask_uint32(self._prefix_length)

    @staticmethod
    def _mask_uint32(mask_length):
        mask = 0xFFFFFFFF
        mask = mask >> (32 - mask_length)
        mask = mask << (32 - mask_length)
        return mask

    @property
    def network(self):
        return self._network

    @property
    def prefix_length(self):
        return self._prefix_length

    def floor(self):
        return Address(int(self._network))

    def ceiling(self):
        return Address(
            int(self._network) | (self.mask_uint32() ^ (2**32-1))
        )

    def __contains__(self, other):
        if isinstance(other, Address):
            return self.floor() <= other and self.ceiling() >= other
        elif isinstance(other, Subnet):
            return self.floor() <= other.floor() and \
                    self.ceiling() >= other.ceiling()
        else:
            raise TypeError()

    # TODO Would it make sense to implement an iterator?
