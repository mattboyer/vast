from ..net.IPv4 import Subnet
from . import get_dec_base
from .types import SQLAddress
from ..tools.logger import term

from sqlalchemy import Column, Unicode, SmallInteger, Integer
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship, remote, foreign, synonym, backref
from sqlalchemy.ext.declarative import declared_attr


sa_base = get_dec_base()


class AssignedSubnet(Subnet, sa_base):
    '''
    This class is used to set up declarative SQLAlchemy bindings.
    '''

    __tablename__ = 'assigned_ipv4'

    id = Column(Integer, primary_key=True)

    _name = Column(Unicode, name='name')
    _network = Column(SQLAddress, name='address')
    _prefix_length = Column(SmallInteger, name='prefix')

    # These synonyms are provided so that other code can dereference class
    # attributes that aren't private when, e.g. setting up a query to sort on
    # prefix length.
    mapped_name = synonym("_name")
    mapped_network = synonym("_network")
    mapped_prefix_length = synonym("_prefix_length")

    __table_args__ = (
        # We want to allow multiple names for the same network address,
        # provided they refer to assigned subnets of different sizes/prefix
        # lengths.
        UniqueConstraint(
            _network, _prefix_length,
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
    def parent_subnet_id(cls):  # pylint:disable=E0213
        return Column(Integer, ForeignKey(cls.id))

    @declared_attr
    def next(cls):  # pylint:disable=E0213
        return relationship(
            cls,
            uselist=False,
            remote_side=cls.next_subnet_id,
            primaryjoin=foreign(cls.next_subnet_id) == remote(cls.id),
            post_update=True,
            backref=backref(
                "previous",
                uselist=False,
            ),
        )

    # Let's see if I can get a sensible backref to work for parent in such a
    # way that : A) adding an AssignedSubnet to a given object's list of
    # children populates its parent_subnet_id B) setting an AssignedSubnet's
    # parent adds that object to the parent's children list
    @declared_attr
    def parent(cls):  # pylint:disable=E0213
        return relationship(
            cls,
            uselist=False,
            remote_side=cls.parent_subnet_id,
            primaryjoin=foreign(cls.parent_subnet_id) == remote(cls.id),
            post_update=True,
            backref=backref("children", uselist=True),
        )

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        # TODO Perform some sensible validation?
        if not len(value):
            raise ValueError(
                "%s name can't be empty" % self.__class__.__name__
            )
        self._name = value

    def __init__(self, *args):
        super(self.__class__, self).__init__(*args[:2])
        *_, name = args
        self.name = name

    def __repr__(self):
        return ("<IPv4 assignment: {t.bold}{0}{t.normal}/{t.green}{1}"
                "{t.normal} \"{t.yellow}{2}{t.normal}\">").format(
            self._network,
            self.prefix_length,
            self._name,
            t=term
        )
