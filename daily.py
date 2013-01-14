from iatilib import session
from iatilib import Parser
from iatilib.model import *
import dateutil.parser
import ckanclient
import argparse
import sys
import json

CKAN_API = 'http://iatiregistry.org/api'

def daily_crawler(debug_limit=None,verbose=False):
    # Dict: The existing resources in the database
    existing = { x.id : x for x in session.query(IndexedResource) }
    # Dict: Fresh resources from the main registry
    incoming = _scrape_resource_dict(debug_limit=debug_limit, verbose=verbose)
    # Use the unique IDs to examine the intersection/difference between EXISTING and INCOMING keys
    ex_k = set(existing.keys())
    in_k = set(incoming.keys())
    deleted_ids = list(ex_k - in_k)
    additional_ids = list(in_k - ex_k)
    for i in range(len(deleted_ids)):
        id = deleted_ids[i]
        if verbose:
            print 'Delete [%d/%d] %s' % (i+1,len(deleted_ids),id)
        # TODO remove all trace of the resources?
        session.delete(existing[id])
    session.commit()
    # Check existing resources
    scrape = list(additional_ids)
    for id in ex_k.intersection(in_k):
        if not existing[id].last_modified==incoming[id].last_modified:
            scrape.append( id )
    for i in range(len(scrape)):
        try:
            id = scrape[i]
            url = incoming[id].url
            if verbose: 
                status = 'update' if id in existing else 'new file'
                print 'Scrape [%d/%d] (%s) %s... ' % (i+1,len(scrape),status,_trim_string(url)),
                sys.stdout.flush()
            # Download and import
            parser = Parser(url,id)
            objects = parser.parse()
            # Done
            if id in existing:
                existing[id].apply_update( incoming[id] )
                session.commit()
                #for x in session.query(Activity).filter(Activity.resource_id==id):
                    #session.delete(x)
                for x in objects:
                    session.add( x )
            else:
                session.add( incoming[id] )
                session.commit()
                for x in objects:
                    if x.__tablename__=='activity':
                        assert x.parent_resource==id
                    session.add( x )
            if verbose: print 'Done.'
            print '    Got:', _object_summary(objects)
        except IOError, e:
            # TODO this should catch ~any error
            if verbose: print 'ERROR'
            print '  > Could not download %s: %s' % (resource['url'],str(e))
    if verbose:
        print 'Committing database...'
    session.commit()

def _trim_string(x, limit=50):
    if len(x)<limit: return x
    return x[:limit-3]+'...'

def _object_summary(objects):
    tmp = {}
    for x in objects:
        key = x.__tablename__
        tmp[key] = tmp.get(key,0)+1
    return ', '.join( ['%d %s' % (y,x) for x,y in sorted(tmp.items(),key=lambda (x,y):x) ] )

def _scrape_resource(url):
    r = requests.get(url)

def _scrape_resource_dict(debug_limit=None,verbose=False):
    """Scrape an index of all resources from CKAN, including some metadata.
    Run time is 10-60m approximately."""
    registry = ckanclient.CkanClient(base_location=CKAN_API)
    index = {}
    # Get the list of packages from CKAN
    pkg_names = registry.package_register_get()
    if debug_limit is not None:
        # For debugging purposes it helps not to scrape ~2000 packages
        pkg_names = pkg_names[:debug_limit]
    for i in range(len(pkg_names)):
        if verbose:
            print '[%d/%d] Scraping registry: Reading "%s"...' % (i+1,len(pkg_names),pkg_names[i]),
            sys.stdout.flush()
        pkg = registry.package_entity_get(pkg_names[i])
        last_modified_string = pkg.get('metadata_modified','')
        for resource in pkg.get('resources', []):
            data = { 
                    'last_modified' : dateutil.parser.parse( last_modified_string ),
                    'id' : resource['id'],
                    'url' : resource['url']
                    }
            index[resource['id']] = IndexedResource(**data)
        if verbose: print 'Done.'
    return index


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Daily script to crawl the IATI registry, populating an XML database.')
    parser.add_argument('-d', '--debug', type=int, dest='debug_limit', help='Debug: Limit number of files the crawler may access. Further files are considered to be deleted.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    arg = parser.parse_args()
    daily_crawler(debug_limit=arg.debug_limit,verbose=arg.verbose)

