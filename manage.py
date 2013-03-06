import os
import rq
import urlparse
import codecs

import requests
import redis
import sqlalchemy as sa
import prettytable
from flask.ext.script import Manager


from iatilib.frontend import create_app, db
from iatilib import magic_numbers, parser, codelists


manager = Manager(create_app())


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


if __name__ == "__main__":
    manager.run()
