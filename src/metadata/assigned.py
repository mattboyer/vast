from ..net.IPv4 import Subnet
from . import get_dec_base, DataException
from .types import SQLAddress

from sqlalchemy import Column, Unicode, SmallInteger, Integer
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship, remote, foreign
from sqlalchemy.ext.declarative import declared_attr
from blessings import Terminal


sa_base = get_dec_base()


class AssignedSubnet(Subnet, sa_base):
    '''
    This class is used to set up declarative SQLAlchemy bindings.
    '''

    __tablename__ = 'assigned_ipv4'

    id = Column(Integer, primary_key=True)
    _name = Column(Unicode)
    _network = Column(SQLAddress)
    _prefix_length = Column(SmallInteger)
    __table_args__ = (
        UniqueConstraint(
            # Do we want to allow multiple names for the same subnet in the DB?
            '_network', '_prefix_length',
            name='assigned_ipv4_subnet_key'
        ),
        {
            'sqlite_autoincrement': True
        },
    )

    @declared_attr
    def next_subnet_id(cls):  # pylint:disable=E0213
        return Column(Integer, ForeignKey(cls.id))

    @declared_attr
    def previous_subnet_id(cls):  # pylint:disable=E0213
        return Column(Integer, ForeignKey(cls.id))

    @declared_attr
    def next(cls):  # pylint:disable=E0213
        return relationship(
            cls,
            uselist=False,
            remote_side=cls.next_subnet_id,
            primaryjoin=foreign(cls.next_subnet_id) == remote(cls.id),
            post_update=True,
        )

    @declared_attr
    def previous(cls):  # pylint:disable=E0213
        return relationship(
            cls,
            uselist=False,
            remote_side=cls.previous_subnet_id,
            primaryjoin=foreign(cls.previous_subnet_id) == remote(cls.id),
            post_update=True,
        )

    # TODO Use a hybrid property setter?
    def set_next(self, next_subnet):
        setattr(self, 'next', next_subnet)
        next_subnet.previous = self

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        # TODO Perform some sensible validation?
        if not len(value):
            raise DataException(
                "%s name can't be empty" % self.__class__.__name__
            )
        self._name = value

    def __init__(self, *args):
        super(self.__class__, self).__init__(*args[:2])
        *_, name = args
        self._name = name
        self._next = None
        self._prev = None

    def __repr__(self):
        t = Terminal()
        return ("<IPv4 assignment: {t.bold}{0}{t.normal}/{t.green}{1}"
                "{t.normal} \"{t.yellow}{2}{t.normal}\">").format(
            self._network,
            self.prefix_length,
            self._name,
            t=t
        )
