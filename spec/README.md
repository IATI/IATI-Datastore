Tools and datafiles used in extracting a list of all database fields required to store records.

spec.json
=========
This is a JSON file scraped from http://iatistandard.org/activity-schema-table/
I originally attempted to formulate this spec from the XSD files, but the XML is tricky to process due to its layers of inheritance and types; no Python library can juggle XSDs comfortably (except for use in verifying a .xml); and online tools are mostly Java-based class generators.
A simpler approach is to extract the list of expected fields from IATI's HTML webpage. In the JS console:

    // step 0: copy and paste the contents of http://code.jquery.com/jquery-1.9.0.min.js
    all = []
    readRow = function(i,tr) { var tds = $(tr).find('td'); var out = { section:$(tds[0]).text(), item:$(tds[1]).text(), definition:$(tds[2]).text(), format:$(tds[3]).text(), xml:$(tds[4]).text(), occur:$(tds[5]).text(),  }; all.push(out); }
    $('#tblMain tr').each( readRow )
    $('body').text( JSON.stringify(all) );
    // final step: copy-paste the new page content into a .json textfile

spec_to_python.py
=================
(TODO explain)




