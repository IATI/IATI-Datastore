#!/usr/bin/env python

from iatilib import session
from iatilib.model import *
from iatilib.magic_numbers import *
from sqlalchemy import func
import dateutil.parser
import ckanclient
import argparse
import sys
import json

CKAN_WEB_BASE = 'http://iatiregistry.org/dataset/%s'
CKAN_API = 'http://iatiregistry.org/api'

def update_db(incoming, verbose=False):
    """Update the DB's resources using the freshly obtained resources from CKAN."""
    # Dict: The incoming resources from CKAN
    incoming = { x['id'] : x for x in incoming }
    # Dict: The existing resources in the database
    existing = { x.id : x for x in session.query(IndexedResource) }
    known_deleted = set([ x.id for x in session.query(IndexedResource).filter(IndexedResource.state==CKAN_DELETED) ])
    # Use the unique IDs to examine the intersection/difference between EXISTING and INCOMING keys
    ex_k = set(existing.keys())
    in_k = set(incoming.keys())
    deleted_ids = ex_k - in_k - known_deleted
    additional_ids = in_k - ex_k
    # Tag deleted resources
    for id in deleted_ids:
        existing[id].state = CKAN_DELETED
    # Add new resources
    for id in additional_ids:
        incoming[id]['state'] = CKAN_NEW
        session.add( IndexedResource(**incoming[id]) )
    # Tag existing resources if they have been modified
    count_updated = 0
    count_undeleted = 0
    for id in ex_k.intersection(in_k):
        a = existing[id]
        b = incoming[id]
        if a.state==-3:
            count_undeleted += 1
            existing[id].state = CKAN_UPDATED
            existing[id].url = incoming[id]['url']
            existing[id].last_modified = incoming[id]['last_modified']
        elif (not a.last_modified==b['last_modified']):
            count_updated += 1
            existing[id].state = CKAN_UPDATED
            existing[id].url = incoming[id]['url']
            existing[id].last_modified = incoming[id]['last_modified']
    if verbose:
        print 'Resources: %d created, %d updated, %d deleted, %d undeleted' % (len(additional_ids), count_updated, len(deleted_ids), count_undeleted)
        print 'Committing database...'
    session.commit()
    if verbose:
        counts = dict( session.query(IndexedResource.state,func.count(IndexedResource.state)).group_by(IndexedResource.state))
        print 'DB State:'
        print '  %d awaiting download ("created")'%counts.get(CKAN_NEW,0)
        print '  %d awaiting download ("updated")'%counts.get(CKAN_UPDATED,0)
        print '  %d awaiting garbage collection'%counts.get(CKAN_DELETED,0)
        print '  %d stuck downloading'%counts.get(BEING_DOWNLOADED,0)
        print '  %d processed.'%counts.get(READY,0)
        for (x,y) in counts.iteritems():
            if x not in [CKAN_NEW,CKAN_UPDATED,CKAN_DELETED,BEING_DOWNLOADED,READY]:
                print '  %d in state %d'%(x,y)

def crawl_ckan(debug_limit=None,verbose=False):
    """Scrape an index of all resources from CKAN, including some metadata.
    Run time is 10-60m approximately."""
    registry = ckanclient.CkanClient(base_location=CKAN_API)
    index = []
    # Get the list of packages from CKAN
    pkg_names = registry.package_register_get()
    if debug_limit is not None:
        # For debugging purposes it helps not to scrape ~2000 packages
        pkg_names = pkg_names[:debug_limit]
    for i in range(len(pkg_names)):
        if verbose:
            print '[%d/%d] Crawling CKAN registry: Reading "%s"...' % (i+1,len(pkg_names),pkg_names[i]),
            sys.stdout.flush()
        pkg = registry.package_entity_get(pkg_names[i])
        last_modified_string = pkg.get('metadata_modified','')
        for resource in pkg.get('resources', []):
            index.append( {
                    'last_modified' : dateutil.parser.parse( last_modified_string ),
                    'id' : resource['id'],
                    'url' : resource['url'],
                    'ckan_url' : CKAN_WEB_BASE % pkg.get('name',pkg['id'])
                })
        if verbose: 
            print 'Done.'
    return index

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Crawl the IATI registry, looking for created/deleted/updated resources.')
    parser.add_argument('-d', '--debug', type=int, dest='debug_limit', help='Debug: Limit number of resources the crawler may access. Further resources are considered to be deleted.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    arg = parser.parse_args()
    # Fetch dict: Fresh resources from the main registry
    incoming = crawl_ckan(debug_limit=arg.debug_limit, verbose=arg.verbose)
    # Update DB to reflect changes
    update_db(incoming,verbose=arg.verbose)
