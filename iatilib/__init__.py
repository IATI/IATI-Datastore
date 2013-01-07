import os
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, scoped_session

_logger = None

# Parse environment
db_url = os.environ.get('DATABASE_URL')
database_echo = os.environ.get('DATABASE_ECHO', '').lower()=='true'
assert db_url is not None, 'No DATABASE_URL defined in the environment.'

engine = create_engine(db_url,echo=database_echo)
session = scoped_session(sessionmaker(engine))

def log(type, message, *args, **kwargs):
    """Log into the internal iati logger."""
    global _logger
    if _logger is None:
        import logging
        _logger = logging.getLogger('iati')
        # Only set up a default log handler if the
        # end-user application didn't set anything up.
        if not logging.root.handlers and _logger.level == logging.NOTSET:
            _logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            _logger.addHandler(handler)
    getattr(_logger, type)(message.rstrip(), *args, **kwargs)

