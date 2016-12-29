import sqlalchemy.types as types

from ..net.IPv4 import Address
from ..tools.logger import ModuleLogger

log = ModuleLogger(__name__)


class SQLAddress(types.TypeDecorator):
    impl = types.Integer

    def process_bind_param(self, value, dialect):
        int_addr = int(value)
        log.debug("Converted %r to %d", value, int_addr)
        return int_addr

    def process_result_value(self, value, dialect):
        return Address(value)

    def process_literal_param(self, value, dialect):
        raise Exception("WTF?!")

    def python_type(self):
        return Address
