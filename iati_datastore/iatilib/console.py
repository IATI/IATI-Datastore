import os
import codecs
import logging
import datetime as dt
import click
from flask.cli import FlaskGroup, with_appcontext

import requests
from sqlalchemy import not_

from iatilib import parse, codelists, model, db, redis

from iatilib.frontend.app import create_app

@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Management script for the IATI application."""
    pass


@cli.command()
@with_appcontext
def download_codelists():
    "Download CSV codelists from IATI"
    for major_version in ['1', '2']:
        for name, url in codelists.urls[major_version].items():
            filename = "iati_datastore/iatilib/codelists/%s/%s.csv" % (major_version, name)
            print("Downloading %s.xx %s" % (major_version, name))
            resp = requests.get(url[major_version])
            resp.raise_for_status()
            resp.encoding = "utf-8"
            assert len(resp.text) > 0, "Response is empty"
            with codecs.open(filename, "w", encoding=resp.encoding) as cl:
                cl.write(resp.text)


@cli.command()
@with_appcontext
def cleanup():
    from iatilib.model import Log
    db.session.query(Log).filter(
            Log.created_at < dt.datetime.utcnow() - dt.timedelta(days=5)
    ).filter(not_(Log.logger.in_(
            ['activity_importer', 'failed_activity', 'xml_parser']),
    )).delete('fetch')
    db.session.commit()
    db.engine.dispose()


@click.option(
        '-x', '--fail-on-xml-errors', "fail_xml")
@click.option(
        '-s', '--fail-on-spec-errors', "fail_spec")
@click.option('-v', '--verbose', "verbose")
@click.argument('filenames', nargs=-1)
@cli.command()
@with_appcontext
def parse_file(filenames, verbose=False, fail_xml=False, fail_spec=False):
    for filename in filenames:
        if verbose:
            print("Parsing", filename)
        try:
            db.session.add_all(parse.document(filename))
            db.session.commit()
        except parse.ParserError as exc:
            logging.error("Could not parse file %r", filename)
            db.session.rollback()
            if isinstance(exc, parse.XMLError) and fail_xml:
                raise
            if isinstance(exc, parse.SpecError) and fail_spec:
                raise


@cli.command()
@with_appcontext
def create_database():
    db.create_all()


@cli.command()
@with_appcontext
def empty_database():
    db.drop_all()
