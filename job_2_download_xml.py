#!/usr/bin/env python

from iatilib import db
from iatilib.model import *
from iatilib.magic_numbers import *
from lxml import etree
import traceback
import argparse
import sys

def download_loop(debug_limit=None,verbose=False):
    downloaded = 0
    while True:
        q = db.session.query(IndexedResource)\
                .filter(IndexedResource.state.in_([CKAN_NEW,CKAN_UPDATED]))
        if verbose:
            print '%d resources in the queue to be downloaded.' % q.count()
        indexed_resource = q.first()
        if indexed_resource is None:
            return
        # Quick! Flag this resource so that parallel downloaders don't try to fetch it
        indexed_resource.state = BEING_DOWNLOADED
        db.session.commit()
        download(indexed_resource,verbose=verbose)
        downloaded += 1
        if (debug_limit is not None) and downloaded >= debug_limit:
            return

def download(indexed_resource,verbose=False):
    # Reset the error log
    for error in indexed_resource.logerrors:
        db.session.delete(error)
    if verbose:
        print '-> %s... ' % (indexed_resource.url),
        sys.stdout.flush()
    # Download XML activities
    try:
        doc = etree.parse(indexed_resource.url)
        for x in indexed_resource.xml_blobs:
            db.session.delete(x)
        xml_activities = doc.findall('iati-activity')
        for xml_activity in xml_activities:
            string = unicode(etree.tostring(xml_activity))
            raw_xml_blob = RawXmlBlob(raw_xml=string, parent_id=indexed_resource.id, parsed=False)
            indexed_resource.xml_blobs.append(raw_xml_blob)
        print 'Done. Got %d activity blobs.' % len(indexed_resource.xml_blobs)
        indexed_resource.state = READY
        db.session.commit()
    except etree.XMLSyntaxError, e:
        error = 'Download Failed: Invalid XML: %s' % (unicode(e))
        print error
        indexed_resource.logerrors.append(LogError(text=error,level=2))
        indexed_resource.state = BROKEN
    except IOError, e:
        error = 'Download Failed: Bad URL? %s' % (unicode(e))
        print error
        indexed_resource.logerrors.append(LogError(text=error,level=2))
        indexed_resource.state = BROKEN
    except Exception as e:
        error = 'Download Failed: Uncaught Exception: %s' % (unicode(e))
        print error
        indexed_resource.logerrors.append(LogError(text=error,level=2))
        indexed_resource.state = BROKEN # Retry on the next pass
    # Send new objects to the database
    db.session.commit()

if __name__=='__main__':
    from iatilib.frontend import create_app
    argparser = argparse.ArgumentParser(description='')
    argparser.add_argument('-d', '--debug', type=int, dest='debug_limit', help='Debug: Limit the number of records to be handled in this sweep.')
    argparser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    arg = argparser.parse_args()

    app = create_app()
    download_loop(debug_limit=arg.debug_limit,verbose=arg.verbose)

