import random
import sqlalchemy
from . import schema

class Db(object):
    def __init__(self, db_path):
        from os import path
        self.db_uri = 'sqlite:///{}'.format(path.abspath(db_path))

        # verbose logging for now
        # FIXME: parsing of types, etc.
        # see sqlalchemy's docs for other flags
        self.engine = sqlalchemy.create_engine(self.db_uri, echo=False)

        @sqlalchemy.event.listens_for(self.engine, 'connect')
        def enable_foreign_keys(connection, record):
            connection.execute('PRAGMA foreign_keys=ON')

        # create tables
        schema._schema.metadata.create_all(self.engine)
        # FIXME: create backup tables
        ## after_create event ??

        # sqlite doesn't allow multiple concurrent sessions
        # so just create one we will use for everything
        self.SessionMk = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = self.SessionMk()

        # entity cache
        self.__cache = dict()
        self.__cache_high_watermark = 600

    def get(self, type_, oid):
        """Get entity of type type_ by id"""
        key = (type_, oid)
        i = self.__cache.get(key)
        if i is None:
            i = self.session.query(type_).get(oid)
            if i:
                self.__cache[key] = i
                # clean-up cache if it gets too big
                if len(self.__cache) > self.__cache_high_watermark:
                    for k in random.sample(self.__cache.keys(), 400):
                        del self.__cache[k]
        return i

    def query(self, *entities, **kwargs):
        """Proxy query to session"""
        return self.session.query(*entities, **kwargs)

    def add(self, instance):
        """Proxy add to session"""
        return self.session.add(instance)

    def add_all(self, instances):
        """Proxy add_all to session"""
        return self.session.add_all(instances)

    def commit(self):
        """Proxy commit to session"""
        return self.session.commit()

    def flush(self):
        """Proxy flush to session"""
        return self.session.flush()

    def rollback(self):
        """Proxy rollback to session"""
        return self.session.rollback()

