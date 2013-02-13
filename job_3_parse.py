#!/usr/bin/env python 

from werkzeug.debug.tbtools import get_current_traceback
from iatilib import session, parser
from iatilib.model import *
import argparse

def parse_loop(debug_limit=None,verbose=False):
    parsed = 0
    while True:
        q = session.query(RawXmlBlob)\
                .filter(RawXmlBlob.parsed==False)
        if verbose: 
            print '%d blobs need to be parsed.' % q.count()
        xmlblob = q.first()
        if xmlblob is None:
            return
        try:
            # Lock this xmlblob so parallel threads dont pick it up
            xmlblob.parsed = True
            session.commit()
            # Recursively delete associated Activity/Transaction/etc objects
            xmlblob.activity = None
            session.commit()
            # Parse new objects into the db
            xmlblob.activity, errors = parser.parse(xmlblob.raw_xml)
            session.commit()
        except Exception, e:
            print 'Uncaught Exception: %s' % unicode(e)
            traceback = get_current_traceback()
            for line in traceback.generate_plaintext_traceback():
                print line
            session.rollback()
            xmlblob.parsed = False
            session.commit()
        parsed += 1
        if (debug_limit is not None) and parsed >= debug_limit:
            return

if __name__=='__main__':
    argparser = argparse.ArgumentParser(description='')
    argparser.add_argument('-d', '--debug', type=int, dest='debug_limit', help='Debug: Limit the number of activities to be handled in this sweep.')
    argparser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    arg = argparser.parse_args()
    parse_loop(debug_limit=arg.debug_limit,verbose=arg.verbose)

