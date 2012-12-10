IATI Datastore
==============

The IATI datastore is running on [Heroku](http://heroku.com), using [BaseX](http://basex.org) 7.0.2 hosted on Amazon EC2.

##### List all activities
http://localhost:5000/api/1/activities
##### Activity query:
http://localhost:5000/api/1/activities?iati-identifier=GB-CHC-1074937-GPAF-IMP-035
##### Activity query: (alternate form)
http://localhost:5000/api/1/activity/GB-CHC-1074937-GPAF-IMP-035
##### Activity query: By reporting org...
http://localhost:5000/api/1/activities?reporting-org=GB-CHC-1074937
##### Activity query: By nested attributes
http://localhost:5000/api/1/activities?budget_period-end.iso-date=2014-06-30
##### Activity query: By nested attributes (with OR logic)
http://localhost:5000/api/1/activities?budget_period-end.iso-date=2014-06-30|2015-03-31
