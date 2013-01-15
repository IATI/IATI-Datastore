#!/usr/bin/env python

import os
import iatilib

def create_test_data(source_dir):
    listing = os.listdir(source_dir)[:20]
    for i in range(len(listing)):
        r = {
            'id': u'test-id-%d' % i,
            'url': u'file://%s/%s' % (TESTDATA,listing[i]),
            'state': -1
        }
        x = iatilib.model.IndexedResource(**r)
        iatilib.session.add(x)
    iatilib.session.commit()

if __name__=='__main__':
    existing = iatilib.session.query(iatilib.model.IndexedResource).count()

    if not existing==0:
        print 'Refusing to write test data to a non-empty DB (contains %d indexed resources)' % existing
        exit()

    TESTDATA='/Users/zephod/code/iati-datastore/_testdata'
    create_test_data(TESTDATA)
