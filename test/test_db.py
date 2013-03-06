import iatilib
from iatilib import db
from iatilib.model import *
import unittest
from unittest import skip
import job_1_crawl_ckan
from datetime import datetime

from . import AppTestCase

#DB_OBJECTS = [IndexedResource,Transaction,Sector,Activity]
TIMESTAMP = datetime(day=31,month=1,year=2013)

class DbTestCase(AppTestCase):
    pass

# An empty database should be empty
@skip("test db")
class CaseEmpty(DbTestCase):
    def test_health(self):
        q = db.session.query(IndexedResource)
        count = q.count()
        assert count == 0, count

# Build up a DB and delete it again
@skip("ckan_crawl")
class CaseCrawlCkan(DbTestCase):
    # Various test fixtures
    def _data0(self):
        return [ {'id':u'id-one','last_modified':TIMESTAMP,'url':u''},
                 {'id':u'id-zero','last_modified':TIMESTAMP,'url':u''} ]
    def _data1(self):
        return [ {'id':u'id-zero','last_modified':TIMESTAMP,'url':u''},
                 {'id':u'id-one','last_modified':TIMESTAMP,'url':u''},
                 {'id':u'id-two','last_modified':TIMESTAMP,'url':u''} ]
    def _data2(self):
        return [ {'id':u'id-two','last_modified':TIMESTAMP,'url':u''},
                 {'id':u'id-one','last_modified':TIMESTAMP,'url':u''} ]
    # Setup and teardown
    def setUp(self):
        super(CaseCrawlCkan, self).setUp()
        job_1_crawl_ckan.update_db(self._data0())
        for x in db.session.query(IndexedResource):
            x.state=1
        db.session.commit()
    def tearDown(self):
        db.session.query(IndexedResource).delete()
    # Core tests
    def test_simple(self):
        q = db.session.query(IndexedResource)
        assert q.count()==2, q.count()
        for x in q: assert x.state==1, q.status
    def test_addResource(self):
        job_1_crawl_ckan.update_db(self._data1())
        q = db.session.query(IndexedResource)
        assert q.count()==3, q.count()
        states = { x.id : x.state for x in q }
        assert states=={'id-zero':1,'id-one':1,'id-two':-1}, states
    def test_addResourceAgain(self):
        job_1_crawl_ckan.update_db(self._data1())
        job_1_crawl_ckan.update_db(self._data1())
        q = db.session.query(IndexedResource)
        assert q.count()==3, q.count()
        states = { x.id : x.state for x in q }
        assert states=={'id-zero':1,'id-one':1,'id-two':-1}, states
    def test_deleteResource(self):
        job_1_crawl_ckan.update_db(self._data2())
        q = db.session.query(IndexedResource)
        assert q.count()==3, q.count()
        states = { x.id : x.state for x in q }
        assert states=={'id-zero':-3,'id-one':1,'id-two':-1}, states
    def test_deleteAndRecreate(self):
        job_1_crawl_ckan.update_db(self._data2())
        job_1_crawl_ckan.update_db(self._data1())
        q = db.session.query(IndexedResource)
        assert q.count()==3, q.count()
        states = { x.id : x.state for x in q }
        assert states=={'id-zero':-2,'id-one':1,'id-two':-1}, states

# TODO install some further XML test fixtures
