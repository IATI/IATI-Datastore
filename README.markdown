IATI Datastore
==============

The IATI datastore is running on [Heroku](http://heroku.com), using [BaseX](http://basex.org) 7.0.2 hosted on Amazon EC2.

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

