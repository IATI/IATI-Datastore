#!/usr/bin/env python 

from iatilib import session, parser
from iatilib.model import *
import dateutil.parser
import traceback
import ckanclient
import argparse
import sys
import json

def download(debug_limit=None,verbose=False):
    q = session.query(IndexedResource)\
            .filter(IndexedResource.state<=0)\
            .filter(IndexedResource.state!=-3)\
            .limit(debug_limit)
    count_resources = q.count()
    if verbose:
        print 'Found %d resources to download.' % count_resources
    i = 0
    for indexed_resource in q:
        i += 1
        state_strings = {
                -1: 'new file',
                -2: 'updated' }
        state_string = state_strings.get(indexed_resource.state,'unknown')
        url = indexed_resource.url
        try:
            if verbose:
                print 'Scrape [%d/%d] (%s) %s... ' % (i,count_resources,state_string,url),
                sys.stdout.flush()
            # Download and import
            activities,logerrors = parser.parse(url)
            print 'Done. Got:', _object_summary(activities)
            # Delete this resource's activities
            for activity in indexed_resource.activities:
                session.delete(activity)
            for error in indexed_resource.logerrors:
                session.delete(error)
            session.commit()
            # Add the new objects
            for activity in activities:
                indexed_resource.activities.append( activity )
            for error in logerrors:
                indexed_resource.logerrors.append( error )
            indexed_resource.state=1
            session.commit()
        except IOError, e:
            print 'Failed'
            print '  > Could not download %s: %s' % (url,str(e))
        except Exception as e:
            traceback.print_exc()
            print 'Uncaught error in: %s - %s' % (url, str(e))

def _object_summary(objects):
    if objects==[]:
        return '(nothing)'
    tmp = {}
    for x in objects:
        key = x.__tablename__
        tmp[key] = tmp.get(key,0)+1
    return ', '.join( ['%d %s' % (y,x) for x,y in sorted(tmp.items(),key=lambda (x,y):x) ] )


if __name__=='__main__':
    argparser = argparse.ArgumentParser(description='')
    argparser.add_argument('-d', '--debug', type=int, dest='debug_limit', help='Debug: Limit the number of records to be handled in this sweep.')
    argparser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    arg = argparser.parse_args()
    download(debug_limit=arg.debug_limit,verbose=arg.verbose)

