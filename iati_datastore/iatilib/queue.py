import traceback

from flask_rq import get_worker as _get_worker, get_queue
import click
from . import db
from .model import Log, Resource
from flask import Blueprint


manager = Blueprint('queue', __name__)
manager.cli.short_help = 'Background task queue'


def db_log_exception(job, exc_type, exc_value, tb):
    # as this is called when an exception occurs session is probably a mess
    db.session.remove()
    resource = Resource.query.get(job.args[0])
    if resource:
        dataset = resource.dataset_id
        url = resource.url
    else:
        dataset = "nodataset"
        url = "noresource"
    log = Log(
        logger="job {0}".format(job.func_name),
        dataset=dataset,
        resource=url,
        msg="Exception in job %r" % job.description,
        level="error",
        trace=traceback.format_exception(exc_type, exc_value, tb)
    )
    db.session.add(log)
    db.session.commit()
    job.cancel()
    job.delete()


def get_worker():
    # Set up the worker to log errors to the db rather than pushing them
    # into the failed queue.
    worker = _get_worker()
    worker.pop_exc_handler()
    worker.push_exc_handler(db_log_exception)
    return worker


@manager.cli.command('burst')
def burst():
    "Run jobs then exit when queue is empty"
    get_worker().work(burst=True)


@manager.cli.command('background')
def background():
    "Monitor queue for jobs and run when they are there"
    get_worker().work(burst=False)


@manager.cli.command('empty')
def empty():
    "Clear all jobs from queue"
    rq = get_queue()
    rq.empty()
