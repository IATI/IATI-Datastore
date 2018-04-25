IATI Datastore
==============

[![Build Status](https://travis-ci.org/IATI/IATI-Datastore.svg?branch=master)](https://travis-ci.org/IATI/IATI-Datastore)
[![Coverage Status](https://img.shields.io/coveralls/IATI/IATI-Datastore.svg)](https://coveralls.io/r/IATI/IATI-Datastore?branch=master)
[![Code Health](https://landscape.io/github/IATI/IATI-Datastore/master/landscape.png)](https://landscape.io/github/IATI/IATI-Datastore/master)
[![License: MIT](https://img.shields.io/badge/license-AGPLv3-blue.svg)](https://github.com/IATI/iati-datastore/blob/master/LICENSE.txt)


Introduction
------------

The International Aid Transparency Initiative (IATI) aims to make
information about aid spending easier to access. To this end,
we publish the [IATI standard](http://iatistandard.org) and keep a
[registry of data in that form](http://www.iatiregistry.org).

The *IATI Datastore* is provided to help users of IATI's data access the
extracts they are interested in. A public instance is available here:

http://datastore.iatistandard.org


Requirements
------------

You will need [Redis](http://redis.io), [Postgres](http://postgresql.org), python, pip and develpment libraries (for libpq, libxml2 and libxslt) to run the full setup.
For example, on Ubuntu:
    
    sudo aptitude install postgresql redis-server python-pip libpq-dev libxml2-dev libxslt-dev libevent-dev python-dev

Installing for development
--------------------------

[![Build Status](https://api.travis-ci.org/IATI/IATI-Datastore.png)](https://travis-ci.org/IATI/iati-datastore)

```
# Clone the source
git clone https://github.com/IATI/IATI-Datastore.git

# Install development dependencies 
pip install -r requirements_dev.txt

# Run the tests  (these tests use an in-memory sqlite db)
nosetests iati_datastore

# Create a new PostgreSQL database
sudo -u postgres psql -c "CREATE DATABASE iati_datastore"

# Set an environment variable for `DATABASE_URL` linking to the database created
export DATABASE_URL=postgres:///iati_datastore

# Create the db tables
iati create_database

# Note: To create the tables the new database may need access privileges granted to your system user
# See http://dba.stackexchange.com/questions/117109/how-to-manage-default-privileges-for-users-on-a-database-vs-schema/117661#117661
sudo -u postgres psql -c "CREATE USER [SYSTEM USER]"
sudo -u postgres psql -c "GRANT ALL ON DATABASE iati_datastore TO [SYSTEM USER]"

# Start the process of grabbing the source data
iati crawl update

# Start a development server – this should be run in a seperate terminal window
iati runserver

# Run a worker. This will download and index the datafiles
iati queue background

# The progess of the worker can be checked using:
iati crawl status

# A local API is available at: http://127.0.0.1:5000
```


Deploying with apache
---------------------

* Install the requirements listed above
* Install Apache and mod_wsgi

        sudo aptitude install apache2 libapache2-mod-wsgi

* Clone the source
* Install `pip install -e iati_datastore`
* Create a database (in postgres), and set an environment variable
  `DATABASE_URL`. e.g.:

        sudo -u postgres createdb iati-datastore -O my_username -E utf-8
        export DATABASE_URL='postgres:///iati-datastore'

* Run `iati create_database` to create the db tables
* Set up a cron job for updates. (Add the following line after running `crontab -e`)
 
        0 0 * * * export DATABASE_URL='postgres:///iati-datastore'; /usr/local/bin/iati crawl update

* Run a worker with `iati queue background`
    - This needs to persist when you close your ssh connection. A simple way of doing this is using [screen](http://www.gnu.org/software/screen/).

* Set up apache using mod_wsgi

* Create a datastore.wsgi file containing this code (this is necessary because Apache's mod wsgi handles environment variables differently):

        import os
        os.environ['DATABASE_URL'] = 'postgres:///iati-datastore'
        from iatilib.wsgi import app as application

* Add this inside the `<VirtualHost>` tags of your apache configuration:

        WSGIDaemonProcess datastore user=my_username group=my_username
        WSGIProcessGroup datastore
        WSGIScriptAlias / /home/datastore/datastore.wsgi


Updating activities after changing import code
----------------------------------------------

* Run this SQL query on the database - `UPDATE resource SET last_succ=NULL;`
* Restart background process
* Run `iati crawl update` (or wait for cron to run it for you)


Generation of Documentation
---------------------------

API documentation in the docs folder is generated using [Spinx](http://www.sphinx-doc.org).

    cd iati-datastore/docs
    make dirhtml
