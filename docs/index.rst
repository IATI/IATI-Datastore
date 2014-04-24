Home
====

What is the IATI Datastore?
---------------------------

The IATI Datastore is an online service that gathers all data published to the IATI standard into a single queryable source. This can deliver selections of IATI data in JSON or XML formats, or CSV (spreadsheet) for less-technical users.

How does it work?
-----------------

Data that is recorded on the IATI Registry, and is valid against the standard, is pulled into the Datastore on a nightly basis. This enables people to query for IATI activities across several facets (eg: country, publisher, sector). Activities that satisfy the criteria can then be access in XML, JSON or CSV (spreadsheet) format.

Who is it for?
--------------

The store is a service for analysts, data journalists, infomediaries and developers. IATI is providing this ‘back-end’ service to streamline the work of the growing community of open data and transparency technologists who are beginning to build applications that can deliver accessible and usable information to a wide range of users.

Why a store?
------------

This repository is called a store, not a database, because it cannot be used as a single dataset. IATI is a publishing standard, not an integral information system. One activity can be reported through IATI by a donor, an implementing organisation and a third-party (secondary-source publisher): in other words you cannot simply add everything together.

How to access the Datastore
---------------------------

* An API is available that enables people to construct queries.

* For those wishing to just access the data in CSV format, an online form is available to assist with queries

Are there any limitations on the Datastore?
-------------------------------------------

In its current format the store allows you to filter IATI activities by publisher, organisation type, sector, or country as well as by the date of the most recent update. In future all fields will be queryable.

In its current CSV format the store allows three different row outputs: where each row represents an activity, transaction or budget item. In future sub-national geographic information and results reporting will also be available.


