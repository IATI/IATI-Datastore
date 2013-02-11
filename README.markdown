IATI Datastore
==============

The IATI datastore is running on [Heroku](http://heroku.com), using a Postgres database updated by a nightly scraper (`job_crawl_ckan` and `job_download_xml`).

Link to documentation: http://iati-datastore.herokuapp.com

### DB Notes

`IndexedResource` objects have an associated `state` field, which amounts to a magic number (see `iatilib/magic_numbers.py`):

     1   |  OK. Resource was downloaded and indexed.
         |  (Can be discovered via the API).
     0   |  INVALID STATE
         |  (Malformed; misbehaving CKAN crawler?)
    -1   |  Freshly discovered resource.
         |  (Downloader thread needs to fetch this)
    -2   |  last_modified has changed on CKAN.
         |  (Downloader thread needs to fetch this)
    -3   |  Not seen in last crawl of CKAN.
         |  (deleted? should be removed from DB?)
    -4   |  A downloader thread is trying to download this.
         |  (And it might have crashed...)

