from datetime import datetime
import logging
import traceback

from iatilib.model import Log, db

class SQLAlchemyHandler(logging.Handler):

    def emit(self, record):
        trace = None
        exc = record.__dict__['exc_info']
        if exc:
            trace = traceback.format_exc()
        log = Log(
            dataset=record.msg.dataset,
            resource=record.msg.resource,
            logger=record.msg.logger,
            level=record.__dict__['levelname'],
            trace=trace,
            msg=record.msg.message,
            created_at=datetime.fromtimestamp(record.created)
        )
        db.session.add(log)
        #db.session.commit()


class DatasetMessage(object):
    def __init__(self, message, logger=None, dataset=None, resource=None, **kwargs):
        self.message = message
        self.logger = logger
        self.dataset = dataset
        self.resource = resource
        self.kwargs = kwargs

    def __str__(self):
        return '{0} >>> {1} : {2}'.format(self.message, self.dataset, self.resource)
