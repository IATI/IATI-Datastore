API
===

.. contents::

.. toctree::
  :glob:

  api/*

Available data
--------------

URLs are of the form

``/api/1/access/{activity}.{format}``

-  XML `/api/1/access/activity.xml </api/1/access/activity.xml>`__
-  JSON
   `/api/1/access/activity.json </api/1/access/activity.json>`__
-  CSV (see below)
   `/api/1/access/activity.csv </api/1/access/activity.csv>`__

There are several additional CSV formats to get access to more data.

-  List of activity
   `/api/1/access/activity.csv </api/1/access/activity.csv>`__
-  Activities by sector
   `/api/1/access/activity/by_sector.csv </api/1/access/activity/by_sector.csv>`__
-  Activities by country
   `/api/1/access/activity/by_country.csv </api/1/access/activity/by_country.csv>`__

-  List of transactions
   `/api/1/access/transaction.csv </api/1/access/transactionscsv>`__

-  Transactions by sector
   `/api/1/access/transaction/by_sector.csv </api/1/access/transaction/by_sector.csv>`__
-  Transactions by country
   `/api/1/access/transaction/by_country.csv </api/1/access/transaction/by_country.csv>`__

-  List of budgets
   `/api/1/access/budget.csv </api/1/access/budget.csv>`__

-  Budgets by sector
   `/api/1/access/budget/by_sector.csv </api/1/access/budget/by_sector.csv>`__
-  Budgets by country
   `/api/1/access/budget/by_country.csv </api/1/access/budget/by_country.csv>`__

Filtering
---------

+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| Filter term                                      | Description                                                                                                  |
+==================================================+==============================================================================================================+
| iati-identifier                                  | `IATI Identifier <http://iatistandard.org/activity-standard/iati-identifier/>`__                             |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| recipient-country                                | `Recipient Country <http://iatistandard.org/activity-standard/recipient-country/>`__                         |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| recipient-region                                 | `Recipient Region <http://iatistandard.org/activity-standard/recipient-region/>`__                           |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| reporting-org                                    | Reporting Org                                                                                                |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| reporting-org.type                               | Reporting Org Type                                                                                           |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| sector                                           | Sector                                                                                                       |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| policy-marker                                    | Policy Marker                                                                                                |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| participating-org                                | `Participating Org <http://iatistandard.org/activity-standard/participating-org/>`__                         |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| participating-org.role                           | `Participating Org Role <http://iatistandard.org/activity-standard/participating-org/>`__                    |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| related-activity                                 | `Related Activity <http://iatistandard.org/activity-standard/related-activity/>`__                           |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| transaction                                      | `Transaction <http://iatistandard.org/activity-standard/transaction/>`__                                     |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| transaction\_provider-org                        | `Transaction Provider Organisation <http://iatistandard.org/activity-standard/transaction/provider-org>`__   |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| transaction\_provider-org.provider-activity-id   | `Transaction Provider Activity ID <http://iatistandard.org/activity-standard/transaction/provider-org>`__    |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| transaction\_receiver-org                        | `Transaction Receiver Organisation <http://iatistandard.org/activity-standard/transaction/receiver-org>`__   |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| transaction\_receiver-org.receiver-activity-id   | `Transaction Receiver Activity ID <http://iatistandard.org/activity-standard/transaction/receiver-org>`__    |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| start-date\_\_lt                                 | `Start Actual <http://iatistandard.org/activities-standard/activity-dates/>`__                               |
| start-date\_\_gt                                 |                                                                                                              |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| end-date\_\_lt                                   | `End Actual <http://iatistandard.org/activities-standard/activity-dates/>`__                                 |
| end-date\_\_gt                                   |                                                                                                              |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| last-change\_\_lt                                | Datetime of activity's last change in the datastore                                                          |
| last-change\_\_gt                                |                                                                                                              |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| last-updated-datetime\_\_lt                      | `Last Updated Datetime <http://iatistandard.org/activities-standard/iati-activity/>`__                       |
| last-updated-datetime\_\_gt                      |                                                                                                              |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+
| registry-dataset                                 | Dataset name on the registry                                                                                 |
+--------------------------------------------------+--------------------------------------------------------------------------------------------------------------+

The suffixes ``__lt`` and ``__gt`` distinguish filters for less than and
greater than a given value.

Combining filters gives the results that fufill all the terms. So

`/api/1/access/activity.xml?reporting-org=GB-1&recipient-country=CD </api/1/access/activity.xml?reporting-org=GB-1&recipient-country=CD>`__

will respond with all the DFID (GB-1) data for the Democratic Republic
of Congo (CD).

Complex Filtering
~~~~~~~~~~~~~~~~~

To filter DFID (GB-1) data by recipient-country as Democratic Republic
of Congo (CD) OR Uganda (UG)

`/api/1/access/activity.xml?reporting-org=GB-1&recipient-country=CD|UG </api/1/access/activity.xml?reporting-org=GB-1&recipient-country=CD|UG>`__

Paging through results
----------------------

Results are normally returned one page at a time, increment the
``offset`` parameter to get the next page.

-  `/api/1/access/activity.xml </api/1/access/activity.xml>`__
-  `/api/1/access/activity.xml?offset=2 </api/1/access/activity.xml?offset=2>`__

The datastore will respond with an HTTP 404 when you have asked for the
page beyond the last page.

You can also set the maximum number of results to receive via the
``limit`` parameter: \*
`/api/1/access/activity.xml?limit=50 </api/1/access/activity.xml?limit=100>`__

The default is 50. Trying to fetch more than about 1000 activities with
this this call is likely to result in an error.

Getting all the results at once
-------------------------------

The CSV and XML formats supports returning all results at once in a
'stream'. To request all results add 'stream=True' to your parameters.
So:

`/api/1/access/transaction.csv?reporting-org.ref=GB-1&stream=True </api/1/access/transaction.csv?reporting-org.ref=GB-1&stream=True>`__

will respond with all the DFID transactions data as CSV.

`/api/1/access/activity.xml?reporting-org.ref=GB-1&stream=True </api/1/access/activity.xml?reporting-org.ref=GB-1&stream=True>`__

will respond with all DFID activity data as XML.

Checking the Data
-----------------

The datastore keeps information on any errors it encountered whilst
fetching and parsing any of the resources. `More info </error>`__

-  list of datasets which have
   errored `api/1/error/dataset </api/1/error/dataset>`__
-  list of errors for specific dataset
   ``api/1/error/dataset/<errored dataset>``

General information about the datasets, such as the urls for the
resources and when they were fetched

-  List of datasets `api/1/about/dataset </api/1/about/dataset>`__
-  Specific details of dataset ``api/1/about/dataset/<dataset name>``

Source code
-----------

The IATI Datastore is still under development. You can `browse the
source code and report bugs on
Github <https://github.com/IATI/iati-datastore>`__.
