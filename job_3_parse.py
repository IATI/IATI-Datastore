#!/usr/bin/env python
import sys
import traceback
import argparse

from iatilib import db, parser
from iatilib.model import RawXmlBlob


def parse_loop(debug_limit=None, verbose=False, fail_fast=False):
    parsed = 0
    while True:
        q = RawXmlBlob.query.filter(RawXmlBlob.parsed == False)
        if verbose:
            print '%d blobs need to be parsed.' % q.count()
        xmlblob = q.first()
        if xmlblob is None:
            return
        try:
            # Lock this xmlblob so parallel threads dont pick it up
            xmlblob.parsed = True
            db.session.commit()
            # Recursively delete associated Activity/Transaction/etc objects
            xmlblob.activity = None
            # Parse new objects into the db
            xmlblob.activity, errors = parser.parse(xmlblob.raw_xml)
            db.session.commit()
        except Exception:
            db.session.rollback()
            print >>sys.stderr, "Could not parse xml blob id=%s" % xmlblob.id
            traceback.print_exc()
            xmlblob.parsed = False
            db.session.commit()
            if fail_fast:
                raise
        parsed += 1
        if (debug_limit is not None) and parsed >= debug_limit:
            return


if __name__ == '__main__':
    from iatilib.frontend import create_app
    create_app()
    argparser = argparse.ArgumentParser(description='')
    argparser.add_argument('-d', '--debug', type=int, dest='debug_limit', help='Debug: Limit the number of activities to be handled in this sweep.')
    argparser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    argparser.add_argument(
        '--fail-fast',
        action='store_true',
        help='Terminate if parser hits an error')

    arg = argparser.parse_args()
    parse_loop(
        debug_limit=arg.debug_limit,
        verbose=arg.verbose,
        fail_fast=arg.fail_fast)

