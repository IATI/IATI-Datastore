from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.redis import Redis

# Monkeypatch to disable signalling
# https://github.com/IATI/iati-datastore/issues/172#issuecomment-45877966
from flask.ext.sqlalchemy import _MapperSignalEvents
_MapperSignalEvents._record = lambda *args, **kwargs: None

db = SQLAlchemy()
redis = Redis()

_logger = None


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
