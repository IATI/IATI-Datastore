IATI Datastore
==============

The International Aid Transparency Initiative (IATI) aims to make
information about aid spending easier to access. To this end,
they publish the [IATI standard](http://iatistandard.org) and keep a
[registry of data that form](http://www.iatiregistry.org).

The *IATI Datastore* is provided to help users of IATI's data access the
extracts they are interested in. A public instance is available here:

http://iati-datastore.herokuapp.com

Installing for development
==========================

[![Build Status](https://api.travis-ci.org/okfn/iati-datastore.png)](https://travis-ci.org/[https://api.travis-ci.org/okfn/iati-datastore.png)

You will need [Redis](http://redis.io) and [Postgres](http://postgresql.org)
to run the full setup.

* Clone the source
* Install `pip install -e iati_datastore`
* Install `pip install -r requirements_dev.txt`
* Run the tests `nosetests iati_datastore`
  (the tests use an in-memory sqlite db)
* Create a database (in postgres), and set an environment variable
  `DATABASE_URL` to something like `postgres:///iati-ds`.
* Run `iati create_database` to create the db tables
* Run `iati crawl update` to start the process of grabbing the source data
* Run `iati runserver` to start a development server
* Run a worker with `iati queue background`
  - this will download and index the datafiles,
    check progess with `iati crawl status`.
* Go to http://127.0.0.1:5000

