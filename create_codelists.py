#!/usr/bin/env python

from iatilib import session
from iatilib.model import *
import unicodecsv
import urllib
from cStringIO import StringIO

def _download_csv(url, types={}):
    buf = StringIO()
    buf.write( urllib.urlopen(url).read() )
    buf.seek(0)
    reader = unicodecsv.reader(buf)
    headers = reader.next()
    for x in range(len(headers)):
        headers[x] = headers[x].replace('-','_')
    out = []
    for row in reader:
        row = { headers[x]:row[x] for x in range(len(row)) }
        for key in row.keys():
            row[key] = types.get(key,unicode)(row[key])
        out.append(row)
    return out

def main():
    url_sectors = 'http://datadev.aidinfolabs.org/data/codelist/Sector/version/1.0/lang/en.csv'
    session.query(CodelistSector).delete()
    for _dict in _download_csv(url_sectors, types={'category':int,'code':int}):
        obj = CodelistSector(**_dict)
        session.add(obj)
    session.commit()

if __name__=='__main__':
    main()
