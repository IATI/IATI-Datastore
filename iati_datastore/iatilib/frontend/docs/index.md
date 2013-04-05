
IATI Datastore
==============

The International Aid Transparency Initiative (IATI) aims to make
information about aid spending easier to access. To this end,
they publish the [IATI standard](http://iatistandard.org) and keep a
[registry of data that form](http://www.iatiregistry.org).

The *IATI Datastore* is provided to help users of IATI's data access the
extracts they are interested in.


Available data
--------------

URLs are of the form

`/api/1/access/{activities}.{format}`


* XML [`/api/1/access/activities.xml`](http://iati-datastore.herokuapp.com/api/1/access/activities.xml)
* JSON [`/api/1/access/activities.json`](http://iati-datastore.herokuapp.com/api/1/access/activities.json)
* CSV (see below) [`/api/1/access/activities.csv`](http://iati-datastore.herokuapp.com/api/1/access/activities.csv)


There are several additional CSV formats to get access to more data.

* List of activities [`/api/1/access/activities.csv`](http://iati-datastore.herokuapp.com/api/1/access/activities.csv)
* Activities by sector [`/api/1/access/activities/by_sector.csv`](http://iati-datastore.herokuapp.com/api/1/access/activities/by_sector.csv)
* Activities by country [`/api/1/access/activities/by_country.csv`](http://iati-datastore.herokuapp.com/api/1/access/activities/by_country.csv)

* List of transactions [`/api/1/access/transactions.csv`](http://iati-datastore.herokuapp.com/api/1/access/transactions.csv)
* Transactions by sector [`/api/1/access/transactions/by_sector.csv`](http://iati-datastore.herokuapp.com/api/1/access/transactions/by_sector.csv)
* Transactions by country [`/api/1/access/transactions/by_country.csv`](http://iati-datastore.herokuapp.com/api/1/access/transactions/by_country.csv)


* List of budgets [`/api/1/access/budgets.csv`](http://iati-datastore.herokuapp.com/api/1/access/budgets.csv)
* Budgets by sector [`/api/1/access/budgets/by_sector.csv`](http://iati-datastore.herokuapp.com/api/1/access/budgets/by_sector.csv)
* Budgets by country [`/api/1/access/budgets/by_country.csv`](http://iati-datastore.herokuapp.com/api/1/access/budgets/by_country.csv)



Filtering
---------

<table class="table">
    <tr>
        <th>Filter term</th>
        <th>Description</th>
    </tr>
    <tr>
        <td>recipient-country</td>
        <td><a href="http://iatistandard.org/activities-standard/recipient-country/">Recipient Country</a></td>
    </tr>
    <tr>
        <td>recipient-region</td>
        <td><a href="http://iatistandard.org/activities-standard/recipient-region/">Recipient Region</a></td>
    </tr>
    <tr>
        <td>reporting-org</td>
        <td><a href="http://iatistandard.org/activities-standard/reporting-org/">Reporting Org</td>
    </tr>
    <tr>
        <td>reporting-org_type</td>
        <td><a href="http://iatistandard.org/activities-standard/reporting-org/">Reporting Org Type</td>
    </tr>
    <tr>
        <td>sector</td>
        <td><a href="http://iatistandard.org/activities-standard/sector/">Sector</td>
    </tr>
    <tr>
        <td>participating-org</td>
        <td><a href="http://iatistandard.org/activities-standard/participating-org/">Participating Org</a></td>
    </tr>
</table>


Combining filters gives the results that furfill all the terms. So

[`/api/1/access/activities.xml?reporting-org=GB-1&recipient-country=CD`](http://iati-datastore.herokuapp.com/api/1/access/activities.xml?reporting-org=GB-1&recipient-country=CD)

will respond with all the DFID data for the Democratic Republic of Congo.


Paging through results
----------------------

Results are normally returned one page at a time, increment the the `page`
paramter to get the next page.

* [`/api/1/access/activities.xml`](http://iati-datastore.herokuapp.com/api/1/access/activities.xml)
* [`/api/1/access/activities.xml?page=2`](http://iati-datastore.herokuapp.com/api/1/access/activities.xml?page=2)

The datastore will respond with an HTTP 404 when you have asked for the page
beyond the last page.



Getting all the results at once
-------------------------------

The CSV format supports returning all results at once in a 'stream'. To
request all results add 'stream=True' to your parameters. So

[`/api/1/access/transactions.csv?reporting_org_ref=GB-1&stream=True`](http://datastore.herokuapp.com/api/1/access/transactions.csv?reporting_org_ref=GB-1&stream=True)

will respond with all the DFID transactions data.


