import iatilib
from iatilib import session
from iatilib.model import *
import unittest
import job_crawl_ckan
from datetime import datetime


DB_OBJECTS = [IndexedResource,Transaction,Sector,Activity]
TIMESTAMP = datetime(day=31,month=1,year=2013)

class DbTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert iatilib.db_url=='sqlite:///:memory:', 'Test data running on real DB! %s' % iatilib.db_url
        for x in DB_OBJECTS:
            count = session.query(x).count()
            assert count==0, 'previous tests left some cruft: %d %s' % (count,x)

    @classmethod
    def tearDownClass(cls):
        for x in DB_OBJECTS:
            session.query(x).delete()
            session.commit()

# An empty database should be empty
class CaseEmpty(DbTestCase):
    def test_health(self):
        q = session.query(IndexedResource)
        count = q.count()
        assert count == 0, count

# Build up a DB and delete it again
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
        job_crawl_ckan.update_db(self._data0())
        for x in session.query(IndexedResource):
            x.state=1
        session.commit()
    def tearDown(self): 
        session.query(IndexedResource).delete()
    # Core tests
    def test_simple(self):
        q = session.query(IndexedResource)
        assert q.count()==2, q.count()
        for x in q: assert x.state==1, q.status
    def test_addResource(self):
        job_crawl_ckan.update_db(self._data1())
        q = session.query(IndexedResource)
        assert q.count()==3, q.count()
        states = { x.id : x.state for x in q }
        assert states=={'id-zero':1,'id-one':1,'id-two':-1}, states
    def test_addResourceAgain(self):
        job_crawl_ckan.update_db(self._data1())
        job_crawl_ckan.update_db(self._data1())
        q = session.query(IndexedResource)
        assert q.count()==3, q.count()
        states = { x.id : x.state for x in q }
        assert states=={'id-zero':1,'id-one':1,'id-two':-1}, states
    def test_deleteResource(self):
        job_crawl_ckan.update_db(self._data2())
        q = session.query(IndexedResource)
        assert q.count()==3, q.count()
        states = { x.id : x.state for x in q }
        assert states=={'id-zero':-3,'id-one':1,'id-two':-1}, states
    def test_deleteAndRecreate(self):
        job_crawl_ckan.update_db(self._data2())
        job_crawl_ckan.update_db(self._data1())
        q = session.query(IndexedResource)
        assert q.count()==3, q.count()
        states = { x.id : x.state for x in q }
        assert states=={'id-zero':-2,'id-one':1,'id-two':-1}, states

# TODO install some further XML test fixtures
