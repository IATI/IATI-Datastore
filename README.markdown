IATI Datastore
==============

The IATI datastore is running on [Heroku](http://heroku.com), using [BaseX](http://basex.org) 7.0.2 hosted on Amazon EC2.

---
#####Essential stats:
http://iati-datastore.herokuapp.com/api/1/about

#####List all activities:
http://iati-datastore.herokuapp.com/api/1/access/activities

#####Activity query:
http://iati-datastore.herokuapp.com/api/1/access/activities?iati-identifier=GB-CHC-1074937-GPAF-IMP-035

#####Activity query: (alternate form)
http://iati-datastore.herokuapp.com/api/1/access/activity/GB-CHC-1074937-GPAF-IMP-035

#####Activity query: By reporting org...
http://iati-datastore.herokuapp.com/api/1/access/activities?reporting-org=GB-CHC-1074937

#####Activity query: By nested attributes
http://iati-datastore.herokuapp.com/api/1/access/activities?budget_period-end.iso-date=2014-06-30

#####Activity query: By nested attributes (with OR logic)
http://iati-datastore.herokuapp.com/api/1/access/activities?budget_period-end.iso-date=2014-06-30|2015-03-31

---

Live DB
=======
The live database contains 106,415 activities and 501,274 transactions. Even with substantial indexing this is very slow. The API will serve the live database if the querystring contains ?live, for example:

http://iati-datastore.herokuapp.com/api/1/about?live

http://iati-datastore.herokuapp.com/api/1/access/activity/41AAA-00082842?live

Be aware: These endpoints take upwards of 10sec to serve. Don't try to list all activities; the result will be enormous and the frontend will be swamped!
