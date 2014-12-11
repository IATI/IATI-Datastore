import os
import codecs
import logging
import datetime as dt

import requests
from flask.ext.script import Manager
from sqlalchemy import not_

from iatilib.frontend import create_app
from iatilib import parse, codelists, model, db, redis
from iatilib.crawler import manager as crawler_manager
from iatilib.queue import manager as queue_manager


manager = Manager(create_app(DEBUG=True))
manager.add_command("crawl", crawler_manager)
manager.add_command("queue", queue_manager)


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
    "Download CSV codelists from IATI"
    for major_version in ['1', '2']:
        for name, url in codelists.urls[major_version].items():
            filename = "iati_datastore/iatilib/codelists/%s/%s.csv" % (major_version, name)
            print "Downloading %s.xx %s" % (major_version, name)
            resp = requests.get(url[major_version])
            resp.raise_for_status()
            assert len(resp.text) > 0, "Response is empty"
            with codecs.open(filename, "w", encoding="utf-8") as cl:
                cl.write(resp.text)


@manager.command
def cleanup():
    from iatilib.model import Log
    db.session.query(Log).filter(
        Log.created_at < dt.datetime.utcnow() - dt.timedelta(days=5)
    ).filter(not_(Log.logger.in_(
        ['activity_importer', 'failed_activity', 'xml_parser']),
    )).delete('fetch')
    db.session.commit()
    db.engine.dispose()
    

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


def main():
    manager.run()

if __name__ == "__main__":
    main()

