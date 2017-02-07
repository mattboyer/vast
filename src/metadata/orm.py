from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .. import SQLITE_PATH
from ..tools.logger import ModuleLogger
from .assigned import AssignedSubnet
from . import get_dec_base

log = ModuleLogger(__name__)


class DataManager(object):
    '''
    Encapsulates a SQLAlchemy session instance and provides data persistence
    methods for domain objects.
    '''

    def __init__(self):
        log.debug('Creating engine for %s', SQLITE_PATH)
        session_engine = create_engine(
            # That's right, *three* slashes + an absolute path
            # That's how SQLAlchemy rolls. Just fucken hardcore, you know?
            'sqlite:///' + SQLITE_PATH
        )
        decbase = get_dec_base()
        decbase.metadata.create_all(session_engine)
        session_factory = sessionmaker(bind=session_engine)
        self._sa_session = session_factory()

    def update_record(self, assigned_subnet):
        self._update_single_record(assigned_subnet)
        self._sa_session.commit()

    def update_records(self, subnet_sequence):
        for sub in subnet_sequence:
            self._update_single_record(sub)
        self._sa_session.commit()

    def _update_single_record(self, assigned_subnet):
        '''
        Creates/updates a record for an assigned subnet, but doesn't commit
        '''
        # XXX Why is it we don't need to call begin()??
        # self._sa_session.begin()

        existing_records = self._sa_session.query(AssignedSubnet).filter_by(
            _network=assigned_subnet.network,
            _prefix_length=assigned_subnet.prefix_length,
        )
        old_record = existing_records.first()
        if old_record is None:
            log.debug('Creating new record for %r', assigned_subnet)
            self._sa_session.add(assigned_subnet)
        else:
            log.debug('Updating existing record for %r', assigned_subnet)
            old_record.name = assigned_subnet.name
            if assigned_subnet.next:
                old_record.set_next(assigned_subnet.next)
            if assigned_subnet.parent:
                old_record.set_parent(assigned_subnet.parent)

    def all_records(self):
        # Use a baked query?
        # This simply returns a generator-like object
        return self._sa_session.query(AssignedSubnet)

    def query(self, *args, **kwargs):
        # Use a baked query?
        # This simply returns a generator-like object
        return self._sa_session.query(*args, **kwargs)
