IATI Datastore
==============

The International Aid Transparency Initiative (IATI) aims to make
information about aid spending easier to access. To this end,
they publish the [IATI Standard](http://iatistandard.org) and keep a
[Registry of data in that form](http://www.iatiregistry.org).

The *IATI Datastore* is provided to help users of IATI data access the
extracts they are interested in.


Available data
--------------

URLs are of the form

`/api/1/access/{activity}.{format}`


* XML [`/api/1/access/activity.xml`](http://iati-datastore.herokuapp.com/api/1/access/activity.xml)
* JSON [`/api/1/access/activity.json`](http://iati-datastore.herokuapp.com/api/1/access/activity.json)
* CSV (see below) [`/api/1/access/activity.csv`](http://iati-datastore.herokuapp.com/api/1/access/activity.csv)


There are several additional CSV formats to get access to more data.

* List of activity [`/api/1/access/activity.csv`](http://iati-datastore.herokuapp.com/api/1/access/activity.csv)
* Activities by sector [`/api/1/access/activity/by_sector.csv`](http://iati-datastore.herokuapp.com/api/1/access/activity/by_sector.csv)
* Activities by country [`/api/1/access/activity/by_country.csv`](http://iati-datastore.herokuapp.com/api/1/access/activity/by_country.csv)

* List of transactions [`/api/1/access/transaction.csv`](http://iati-datastore.herokuapp.com/api/1/access/transactionscsv)
* Transactions by sector [`/api/1/access/transaction/by_sector.csv`](http://iati-datastore.herokuapp.com/api/1/access/transaction/by_sector.csv)
* Transactions by country [`/api/1/access/transaction/by_country.csv`](http://iati-datastore.herokuapp.com/api/1/access/transaction/by_country.csv)


* List of budgets [`/api/1/access/budget.csv`](http://iati-datastore.herokuapp.com/api/1/access/budget.csv)
* Budgets by sector [`/api/1/access/budget/by_sector.csv`](http://iati-datastore.herokuapp.com/api/1/access/budget/by_sector.csv)
* Budgets by country [`/api/1/access/budget/by_country.csv`](http://iati-datastore.herokuapp.com/api/1/access/budget/by_country.csv)



Filtering
---------

<table class="table">
    <tr>
        <th>Filter term</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>iati-identifier</td>
        <td><a href="http://iatistandard.org/activity-standard/iati-identifier/">IATI Identifier</a></td>
    </tr>
    <tr>
        <td>recipient-country</td>
        <td><a href="http://iatistandard.org/activity-standard/recipient-country/">Recipient Country</a></td>
    </tr>
    <tr>
        <td>recipient-region</td>
        <td><a href="http://iatistandard.org/activity-standard/recipient-region/">Recipient Region</a></td>
    </tr>
    <tr>
        <td>reporting-org</td>
        <td><a href="http://iatistandard.org/activity-standard/reporting-org/">Reporting Org</td>
    </tr>
    <tr>
        <td>reporting-org.type</td>
        <td><a href="http://iatistandard.org/activity-standard/reporting-org/">Reporting Org Type</td>
    </tr>
    <tr>
        <td>sector</td>
        <td><a href="http://iatistandard.org/activity-standard/sector/">Sector</td>
    </tr>
    <tr>
        <td>policy-marker</td>
        <td><a href="http://iatistandard.org/activity-standard/thematic-marker/">Policy Marker</td>
    </tr>
    <tr>
        <td>participating-org</td>
        <td><a href="http://iatistandard.org/activity-standard/participating-org/">Participating Org</a></td>
    </tr>
    <tr>
        <td>participating-org.role</td>
        <td><a href="http://iatistandard.org/activity-standard/participating-org/">Participating Org Role</a></td>
    </tr>
    <tr>
        <td>related-activity</td>
        <td><a href="http://iatistandard.org/activity-standard/related-activity/">Related Activity</a></td>
    </tr>
    <tr>
        <td>transaction</td>
        <td><a href="http://iatistandard.org/activity-standard/transaction/">Transaction</a></td>
    </tr>
    <tr>
        <td>transaction_provider-org</td>
        <td><a href="http://iatistandard.org/activity-standard/transaction/provider-org">Transaction Provider Organisation</a></td>
    </tr>
    <tr>
        <td>transaction_provider-org.provider-activity-id</td>
        <td><a href="http://iatistandard.org/activity-standard/transaction/provider-org">Transaction Provider Activity ID</a></td>
    </tr>
    <tr>
        <td>transaction_receiver-org</td>
        <td><a href="http://iatistandard.org/activity-standard/transaction/receiver-org">Transaction Receiver Organisation</a></td>
    </tr>
    <tr>
        <td>transaction_receiver-org.receiver-activity-id</td>
        <td><a href="http://iatistandard.org/activity-standard/transaction/receiver-org">Transaction Receiver Activity ID</a></td>
    </tr>

    <tr>
        <td>start-date__lt<br/>start-date__gt</td>
        <td><a href="http://iatistandard.org/activities-standard/activity-dates/">Start Actual</a></td>
    </tr>
    <tr>
        <td>end-date__lt<br/>end-date__gt</td>
        <td><a href="http://iatistandard.org/activities-standard/activity-dates/">End Actual</a></td>
    </tr>
    <tr>
        <td>last-change__lt<br/>last-change__gt</td>
        <td>Datetime of activity's last change in the datastore</td>
    </tr>
    <tr>
        <td>last-updated-datetime__lt<br/>last-updated-datetime__gt</td>
        <td><a href="http://iatistandard.org/activities-standard/iati-activity/">Last Updated Datetime</a></td>
    </tr>
    <tr>
        <td>registry-dataset</td>
        <td>Dataset name on the registry</td>
    </tr>
</table>

The suffixes `__lt` and `__gt` distinguish filters for less than and greater than a given value.

Combining filters gives the results that fufill all the terms. So

[`/api/1/access/activity.xml?reporting-org=GB-1&recipient-country=CD`](http://iati-datastore.herokuapp.com/api/1/access/activity.xml?reporting-org=GB-1&recipient-country=CD)

will respond with all the DFID data for the Democratic Republic of Congo.

###Complex Filtering###

To filter by recipient-country as Democratic Republic of Congo OR Uganda

[`/api/1/access/activity.xml?reporting-org=GB-1&recipient-country=CD|UG`](http://iati-datastore.herokuapp.com/api/1/access/activity.xml?reporting-org=GB-1&recipient-country=CD|UG)


Paging through results
----------------------

Results are normally returned one page at a time, increment the the `offset`
parameter to get the next page.

* [`/api/1/access/activity.xml`](http://iati-datastore.herokuapp.com/api/1/access/activity.xml)
* [`/api/1/access/activity.xml?offset=2`](http://iati-datastore.herokuapp.com/api/1/access/activity.xml?offset=2)

The datastore will respond with an HTTP 404 when you have asked for the page
beyond the last page.

You can also set the maximum number of results to receive via the `limit`
parameter:
* [`/api/1/access/activity.xml?limit=50`](http://iati-datastore.herokuapp.com/api/1/access/activity.xml?limit=100)

The default is 50.


Getting all the results at once
-------------------------------

The CSV format supports returning all results at once in a 'stream'. To
request all results add 'stream=True' to your parameters. So

[`/api/1/access/transaction.csv?reporting-org.ref=GB-1&stream=True`](http://iati-datastore.herokuapp.com/api/1/access/transaction.csv?reporting-org.ref=GB-1&stream=True)

will respond with all the DFID transactions data.



Checking the Data
-----------------

The datastore keeps information on any errors it encountered whilst fetching and parsing any of tthe resources. [More info](http://iati-datastore.herokuapp.com/error)


* list of datasets which have errored[`api/1/error/dataset`](http://iati-datastore.herokuapp.com/api/1/error/dataset)
* list of errors for specific dataset `api/1/error/dataset/<errored dataset>`

General information about the datasets, such as the urls for the resources and when they were fetched
 
* List of datasets[`api/1/about/dataset`](http://iati-datastore.herokuapp.com/api/1/about/dataset)
* Specific details of dataset `api/1/about/dataset/<dataset name>`

Source code
-----------

The IATI Datastore is still under development. You can [browse the source code and report bugs on Github](https://github.com/okfn/iati-datastore).
