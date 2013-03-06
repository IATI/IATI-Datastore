IATI Datastore
==============

The International Aid Transparency Initiative (IATI) aims to make aims
to make information about aid spending easier to access. To this end,
they publish the [IATI standardd](http://iatistandard.org) and keep a
[registry of data that form](http://www.iatiregistry.org).

The *IATI Datastore* is provided to help users of IATI's data access the
extracts they are interested in. A public instance is available here:

http://iati-datastore.herokuapp.com


Operation
=========

* `job_1_crawl_ckan.py` Gets the urls of documents stored in IATI format
* `job_2_download_xml.py` Downloads the documents into the db
* `job_3_parse.py` Parses the documents into the db

These jobs all run regularly.


Installation
============

* Clone the source
* Install requirements `pip install -e requirements_dev.txt`.
* Run the tests `python -m unittest discover` or `nosetests` if you prefer
  (they will use an in-memory sqlite db)
* Create a test database (we use postgres), and set an environment variable
  `DATABASE_URL` to something like `postgres:///iati-ds`.
* Run `python manage.py runserver` to create the db and run a test server
* Run `python create_codelists.py` to add some lookup tables.
* Go to http://127.0.0.1:5000

