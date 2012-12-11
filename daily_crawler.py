from iatilib import open_db, xmldict
import urllib
import ckanclient
import os
from pprint import pprint

INDEX_FILE = 'index.xml'

def daily_crawler(verbose=False):
    # Timestamp to check metadata_modified against
    url = 'http://iatiregistry.org/api'
    registry = ckanclient.CkanClient(base_location=url)
    # Fetch the list of resources on IatiRegistry
    index = _fetch_resource_index(registry, debug_limit=4, verbose=verbose)
    if verbose:
        print '--- index ---'
        pprint(index)
    session=open_db()
    resources_deleted, resources_changed = _sync_index(session,index,verbose=verbose)
    session.close()
    if verbose:
        print '--- resources_deleted ---'
        pprint(resources_deleted)
        print '--- resources_changed ---'
        pprint(resources_changed)

    # Sync that with the list of resources in our DB

def _db_write_file(filename):
    # Overwrite the content of this file
    print session.delete(os.path.basename(filename))
    print session.add(filename)

def _fetch_resource_index(registry,debug_limit=None,verbose=False):
    """Scrape an index of all resources from CKAN, including some metadata.
    Run time is 30-60m approximately."""
    index = []
    # Get the list of packages from CKAN
    pkg_names = registry.package_register_get()
    if debug_limit is not None:
        # For debugging purposes it helps not to scrape ~2000 packages
        pkg_names = pkg_names[:debug_limit]
    for i in range(len(pkg_names)):
        if verbose:
            print '[%d/%d] Fetch data for package "%s"...' % (i+1,len(pkg_names),pkg_names[i])
        pkg = registry.package_entity_get(pkg_names[i])
        last_modified = pkg.get('metadata_modified','')
        for resource in pkg.get('resources', []):
            index.append({
                'name':resource['id'], 
                'url':resource['url'], 
                'last_modified':last_modified})
    return index


def _sync_index(session,index,verbose=False):
    """Maintain an index XML file in the databse listing all the resources we know about.
    This is used to detect where a file has been updated or removed."""
    # Load the index of known packages
    index_old_xml = session.get_index()
    index_file = xmldict.xml_to_dict( index_old_xml )
    root = index_file.get('root') or {}
    index_old = root.get('resources',{}).get('resource',[])
    # Store the updated index of known packages
    index_xml = xmldict.dict_to_xml({
        'root' : {
            'resources': {'resource': index},
            } } )
    assert xmldict.xml_to_dict(index_xml)['root']['resources']['resource']==index
    session.store_index(index_xml)
    # Return a list of deleted files and a list of modified files
    index_old_dict = { x['name'] : x for x in index_old }
    keys_old = set(index_old_dict.keys())
    keys_new = set([ x['name'] for x in index ])
    resources_deleted = [ index_old_dict[x] for x in keys_old-keys_new ]
    resources_changed = []
    for resource in index:
        resource_old = index_old_dict.get( resource['name'] )
        if not resource_old or not (resource_old['last_modified']==resource['last_modified']):
            resources_changed.append( resource )
    return resources_deleted, resources_changed

def _fetch_resource(resource_id, url, tmpdir='tmp/', verbose=False):
    filename = os.path.join(tmpdir,resource_id+'.xml')
    with open(filename) as localFile:
        if verbose:
            print '> writing %s...'%filename,
        webFile = urllib.urlopen(url)
        localFile.write(webFile.read())
        webFile.close()
        if verbose:
            print ' done.'

if __name__=='__main__':
    daily_crawler(verbose=True)

