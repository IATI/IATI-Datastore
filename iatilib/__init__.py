import os
import sqlalchemy
import sqlalchemy.orm

database_url = os.environ.get('DATABASE_URL')
database_echo = os.environ.get('DATABASE_ECHO', '').lower()=='true'

if not database_url:
    raise ValueError('No DATABASE_URL defined in the environment. Try running:\n          $ export DATABASE_URL=postgresql://user:pass@localhost/mydatabase')

engine = sqlalchemy.create_engine(database_url,echo=database_echo)
Session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(engine))

import model
import importer

