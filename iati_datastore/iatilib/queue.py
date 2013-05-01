import traceback

from flask.ext.script import Manager
from flask.ext.rq import get_worker as _get_worker, get_queue

from . import db
from .model import Log

manager = Manager(usage="Background task queue")


def db_log_exception(job, exc_type, exc_value, tb):
    # as this is called when an exception occurs session is probably a mess
    db.session.remove()
    log = Log()
    log.name = "queue"
    log.msg = "Exception in job %r" % job.description
    log.level = "ERROR"
    log.trace = traceback.format_exception(exc_type, exc_value, tb)
    db.session.add(log)
    db.session.commit()


def get_worker():
    # Set up the worker to log errors to the db rather than pushing them
    # into the failed queue.
    worker = _get_worker()
    worker.pop_exc_handler()
    worker.push_exc_handler(db_log_exception)
    return worker


@manager.command
def burst():
    "Run jobs then exit when queue is empty"
    get_worker().work(burst=True)


@manager.command
def background():
    "Monitor queue for jobs and run when they are there"
    get_worker().work(burst=False)


@manager.command
def empty():
    "Clear all jobs from queue"
    rq = get_queue()
    rq.empty()
