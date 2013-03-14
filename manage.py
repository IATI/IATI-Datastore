import os
import rq
import urlparse
import codecs
import logging

import requests
import sqlalchemy as sa
import prettytable
from flask.ext.script import Manager
from flask.ext.rq import get_worker

from iatilib.frontend import create_app
from iatilib import magic_numbers, parse, codelists, model, db, redis
from iatilib.crawler import manager as crawler_manager


manager = Manager(create_app(DEBUG=True))
manager.add_command("crawl", crawler_manager)


@manager.shell
def make_shell_context():
    return dict(
        app=manager.app,
        db=db,
        rdb=redis,
        models=model,
        codelists=codelists)


def qtable(itr, headers=None):
    if headers is None:
        headers = next(itr)
    tbl = prettytable.PrettyTable(headers)
    for row in itr:
        tbl.add_row(row)
    return tbl


@manager.command
def status():
    print "Database: %s" % manager.app.config["SQLALCHEMY_DATABASE_URI"]
    print

    resource_status = db.session.query(
        IndexedResource.state, sa.func.count()).group_by(IndexedResource.state)

    print "Download"
    print qtable(
        ((magic_numbers.label[n], c) for n, c in resource_status),
        ["state", "no of urls"])

    print "Parsing"
    parse_status = db.session.query(
        RawXmlBlob.parsed, sa.func.count()).group_by(RawXmlBlob.parsed)
    print qtable(parse_status, ["status", "no of blobs"])


@manager.command
def parse_blob(blob_id, pdb=False):
    """
    Parse a blob by id, don't insert into the db (debugging tool)
    """
    blob = RawXmlBlob.query.get(blob_id)
    print "Blob %s parsed status=%r" % (blob.id, blob.parsed)
    if pdb:
        try:
            import ipdb
            ipdb.set_trace()
        except ImportError:
            import pdb
            pdb.set_trace()
    activity, errors = parser.parse(blob.raw_xml)
    print "activity", activity
    print "activity.id", activity.id
    print "errors", errors


@manager.command
def dump_blob(blob_id):
    blob = RawXmlBlob.query.get(blob_id)
    print blob.raw_xml


def redis_connect():
    redis_url = os.getenv('REDISTOGO_URL', "redis://localhost:6379")
    urlparse.uses_netloc.append('redis')
    url = urlparse.urlparse(redis_url)
    return redis.Redis(
        host=url.hostname,
        port=url.port,
        db=0,
        password=url.password)


@manager.command
def bulk_parse(max_blobs=None):
    "Enque jobs to parse all unparsed blobs"
    if max_blobs:
        max_blobs = int(max_blobs)
    q = rq.Queue(connection=redis_connect())
    query = RawXmlBlob.query.filter_by(parsed=False)
    print "There are %d blobs that need to be parsed" % query.count()
    if not max_blobs:
        max_blobs = query.count()
    print "Enquing upto %d blobs" % max_blobs
    for blob in query.limit(max_blobs):
        q.enqueue_call(
            func=parser.parse_job,
            args=(blob.id,),
            result_ttl=0)


@manager.command
def bulk_parse_failiures():
    "Print the blob ids that failed to parse"
    failed_q = rq.Queue("failed", connection=redis_connect())
    job = failed_q.dequeue()
    while job:
        raw_xml_blob_id = job.args[0]
        print raw_xml_blob_id
        job = failed_q.dequeue()


@manager.command
def rqworker(burst=False):
    "Start an RQ worker"
    with rq.Connection(redis_connect()):
        worker = rq.Worker(rq.Queue())
        worker.work(burst=burst)


@manager.command
def batch_worker():
    get_worker().work(burst=True)


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
