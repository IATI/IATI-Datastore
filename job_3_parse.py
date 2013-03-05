#!/usr/bin/env python
import sys
import traceback
import argparse
import random

import sqlalchemy as sa

from iatilib import db, parser
from iatilib.model import RawXmlBlob


def parse_loop(debug_limit=None, verbose=False, fail_fast=False):
    parsed = 0
    while True:
        # yuck. Order by random is baaaad for Postgres, but it will stop one
        # broken record holding up parsing all of them.
        q = RawXmlBlob.query.filter_by(parsed=False)
        if verbose:
            print '%d blobs need to be parsed.' % q.count()
        xmlblob = random.choice(q.limit(100).all())
        if xmlblob is None:
            return
        try:
            xmlblob.activity = parser.parse_blob(xmlblob)
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

