import os
from unittest import expectedFailure
import json
from xml.etree import ElementTree as ET

from test import AppTestCase
from iatilib import parser, db
from iatilib.model import Activity, CodelistSector, IndexedResource


class ClientTestCase(AppTestCase):
    def setUp(self):
        super(ClientTestCase, self).setUp()
        self.client = self.app.test_client()


class TestAbout(ClientTestCase):
    def test_about_http(self):
        resp = self.client.get('/api/1/about')
        self.assertEquals(200, resp.status_code)


class TestEmptyDb(ClientTestCase):
    def test_json_http_ok(self):
        resp = self.client.get('/api/1/access/activities')
        self.assertEquals(200, resp.status_code)

    def tests_json_decode(self):
        resp = self.client.get('/api/1/access/activities')
        self.assert_(json.loads(resp.data))

    def test_json_ok(self):
        resp = self.client.get('/api/1/access/activities')
        js = json.loads(resp.data)
        self.assertTrue(js["ok"])

    def test_json_results(self):
        resp = self.client.get('/api/1/access/activities')
        js = json.loads(resp.data)
        self.assertEquals(js["results"], [])



class TestEmptyDbXML(ClientTestCase):
    def _test_http_ok(self):
        resp = self.client.get('/api/1/access/activities.xml')
        self.assertEquals(200, resp.status_code)





class TestSingleActivity(ClientTestCase):
    """
    The json and xml reprisentations of a single activity.
    """
    @expectedFailure
    def test_root_node(self):
        resp = self.client.get('/api/1/access/activities.xml')
        xml = ET.fromstring(resp.data)
        self.assertEquals(xml.tag, 'result')

    @expectedFailure
    def test_load_doc(self):
        # can be anything, there just needs to be > 0
        db.session.add(CodelistSector(code=47045))
        db.session.add(IndexedResource(id=u"TEST"))
        db.session.commit()

        def load_fix():
            fix = "test_1.xml"
            xml = ET.parse(os.path.join(
                os.path.dirname(__file__), "acc_tests", fix))
            return ET.tostring(xml.find('iati-activity'))
        activity, errors = parser.parse(load_fix())
        activity.parent_id = db.db.session.query(IndexedResource).one().id
        db.session.add(activity)
        db.session.commit()
        self.assertEquals(db.session.query(Activity).count(), 1)

    @expectedFailure
    def test_load_doc_api(self):
        # can be anything, there just needs to be > 0
        db.session.add(CodelistSector(code=47045))
        db.session.add(IndexedResource(id=u"TEST"))
        db.session.commit()

        def load_fix():
            fix = "test_1.xml"
            xml = ET.parse(os.path.join(
                os.path.dirname(__file__), "acc_tests", fix))
            return ET.tostring(xml.find('iati-activity'))
        activity, errors = parser.parse(load_fix())
        activity.parent_id = db.session.query(IndexedResource).one().id
        db.session.add(activity)
        db.session.commit()

        resp = self.client.get('/api/1/access/activities.xml')
        xml = ET.fromstring(resp.data)
        self.assert_(xml.find('iati-activity'))
