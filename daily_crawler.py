from iatilib import open_db
import urllib
import ckanclient
import argparse
import sys

def daily_crawler(debug_limit=None,verbose=False):
    # Timestamp to check metadata_modified against
    url = 'http://iatiregistry.org/api'
    registry = ckanclient.CkanClient(base_location=url)
    # Fetch the list of resources on IatiRegistry
    index = _fetch_resource_index(registry, debug_limit=debug_limit, verbose=verbose)
    if verbose:
        print 'Found %d resources.' % len(index)
    session=open_db()
    resources_deleted, resources_changed = _sync_index(session,index,verbose=verbose)
    if verbose:
        print '--- %d resources deleted ---' % len(resources_deleted)
        print '--- %d resources changed ---' % len(resources_changed)
    # Delete all of the deleted files
    for name in resources_deleted:
        if verbose: 
            print 'Deleting %s... ' % name, 
            sys.stdout.flush()
        result = session.delete(name)
        if verbose: print 'Done.'
    scrape = resources_changed.items()
    for i in range(len(scrape)):
        name,resource = scrape[i]
        if verbose: 
            print '[%d/%d] Scraping %s... ' % (i+1,len(scrape),resource['url']),
            sys.stdout.flush()
        content = _download(resource['url'],verbose=verbose)
        result = session.store_file(name,content)
        if verbose: print 'Done.'
    print 'Done. DB contains %s activites.' % session.query('count(//iati-activity)')
    session.close()

def _fetch_resource_index(registry,debug_limit=None,verbose=False):
    """Scrape an index of all resources from CKAN, including some metadata.
    Run time is 30-60m approximately."""
    index = {}
    # Get the list of packages from CKAN
    pkg_names = registry.package_register_get()
    if debug_limit is not None:
        # For debugging purposes it helps not to scrape ~2000 packages
        pkg_names = pkg_names[:debug_limit]
    for i in range(len(pkg_names)):
        if verbose:
            print '[%d/%d] Building index: Reading "%s"...' % (i+1,len(pkg_names),pkg_names[i]),
            sys.stdout.flush()
        pkg = registry.package_entity_get(pkg_names[i])
        last_modified = pkg.get('metadata_modified','')
        for resource in pkg.get('resources', []):
            name = resource['id']
            url = resource['url']
            index[name] = {
                'url':url,
                'last_modified':last_modified
            }
        if verbose: print 'Done.'
    return index

def _sync_index(session,index,verbose=False):
    """Maintain an index XML file in the database listing all the resources we know about.
    This is used to detect where a file has been updated or removed."""
    # Load the index of known packages
    index_old = session.get_index() or {}
    # Store the updated index of known packages
    session.store_index(index)
    # Return a list of deleted files and a list of modified files
    resources_deleted = { x:index_old[x] for x in set(index_old.keys())-set(index.keys()) }
    resources_changed = {}
    for name,resource in index.items():
        if not (name in index_old and index_old[name]['last_modified']==resource['last_modified']):
            resources_changed[name] = resource 
    return resources_deleted, resources_changed

def _download(url, verbose=False):
    r = urllib.urlopen(url)
    return r.read()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Daily script to crawl the IATI registry, populating an XML database.')
    parser.add_argument('-d', '--debug', type=int, dest='debug_limit', help='Debug: Limit number of files the crawler may access. Further files are considered to be deleted.')
    arg = parser.parse_args()
    daily_crawler(debug_limit=arg.debug_limit,verbose=True)

