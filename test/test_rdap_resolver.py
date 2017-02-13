from unittest import TestCase

from src.net.IPv4 import Address, Subnet
from src.metadata.orm import get_dec_base
from src.metadata.RDAP import RDAP_Resolver

class test_RDAP_resolver(TestCase):

    def setUp(self):
        self.rslvr = RDAP_Resolver()
