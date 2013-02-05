spec.json
=========
The JSON format document controlling the database layout. It lists the XPaths to be parsed into database fields. Updating this file and re-running the code generator will alter the database structure and require the IATI database to be re-parsed.
> Source: Originally scraped from http://iatistandard.org/activity-schema-table/ and modified by hand.
I originally attempted to formulate this spec from the XSD files, but the XML is tricky to process due to its layers of inheritance and types; no Python library can juggle XSDs comfortably (except for use in verifying a .xml); and online tools are mostly Java-based class generators.

codegen.py
===========
This outputs the model code to be pasted into model.py. This code is a direct consequence of the structure of spec.json, which attempts to balance the hierarchical nature of XML against the static fields of a database table. (Eg. most activities only have a single document-link node, therefore no need to add a one-to-many subtable for them).
Usage:
* Run from the root directory, eg. `python spec/codegen.py`
* To update the db spec: Open up model.py and delete the lower part of the file (after the comment).
* Replace with the output of codegen.py.




