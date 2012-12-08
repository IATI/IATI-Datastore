import os
from datetime import datetime
import traceback
from . import basex

_logger = None

# Parse environment
db_config = {
    'DATABASE_URL':None,
    'DATABASE_PORT':None,
    'DATABASE_USER':None,
    'DATABASE_PASS':None,
    'DATABASE_NAME':None
}
for k in db_config.keys():
    db_config[k] = os.environ.get(k)
    if not db_config[k]: 
        raise ValueError('No %s defined in the environment. The following must all be defined: %s' % (k, ','.join(db_config.keys())))
db_config['DATABASE_PORT'] = int( db_config['DATABASE_PORT'] )

def open_db():
    return basex.BaseX(db_config['DATABASE_URL'], db_config['DATABASE_PORT'], db_config['DATABASE_USER'], db_config['DATABASE_PASS'], db_config['DATABASE_NAME'])

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

