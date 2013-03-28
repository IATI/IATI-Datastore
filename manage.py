import os
import codecs
import logging

import requests
from flask.ext.script import Manager
from flask.ext.rq import get_worker, get_queue

from iatilib.frontend import create_app
from iatilib import parse, codelists, model, db, redis
from iatilib.crawler import manager as crawler_manager

q_manager = Manager(usage="Background task queue")


@q_manager.command
def burst():
    "Run jobs then exit when queue is empty"
    get_worker().work(burst=True)


@q_manager.command
def background():
    "Monitor queue for jobs and run when they are there"
    get_worker().work(burst=False)


@q_manager.command
def empty():
    "Clear all jobs from queue"
    rq = get_queue()
    rq.empty()

manager = Manager(create_app(DEBUG=True))
manager.add_command("crawl", crawler_manager)
manager.add_command("queue", q_manager)


@manager.shell
def make_shell_context():
    return dict(
        app=manager.app,
        db=db,
        rdb=redis,
        model=model,
        codelists=codelists)


@manager.command
def download_codelists():
    for name, url in codelists.urls.items():
        filename = "iatilib/codelists/%s.csv" % name
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            print filename, "exists, skipping"
        else:
            print "Downloading", name
            resp = requests.get(url)
            resp.raise_for_status()
            assert len(resp.text) > 0, "Response is empty"
            with codecs.open(filename, "w", encoding="utf-8") as cl:
                cl.write(resp.text)


@manager.option(
    '-x', '--fail-on-xml-errors',
    action="store_true", dest="fail_xml")
@manager.option(
    '-s', '--fail-on-spec-errors',
    action="store_true", dest="fail_spec")
@manager.option('-v', '--verbose', action="store_true")
@manager.option('filenames', nargs='+')
def parse_file(filenames, verbose=False, fail_xml=False, fail_spec=False):
    for filename in filenames:
        if verbose:
            print "Parsing", filename
        try:
            db.session.add_all(parse.document(filename))
            db.session.commit()
        except parse.ParserError, exc:
            logging.error("Could not parse file %r", filename)
            db.session.rollback()
            if isinstance(exc, parse.XMLError) and fail_xml:
                raise
            if isinstance(exc, parse.SpecError) and fail_spec:
                raise


@manager.command
def create_database():
    db.create_all()

if __name__ == "__main__":
    manager.run()
