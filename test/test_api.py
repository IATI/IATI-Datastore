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


class TestEmptyDb_JSON(ClientTestCase):
    url = '/api/1/access/activities'

    def test_http_ok(self):
        resp = self.client.get(self.url)
        self.assertEquals(200, resp.status_code)

    def tests_json_decode(self):
        resp = self.client.get(self.url)
        self.assert_(json.loads(resp.data))

    def test_json_ok(self):
        resp = self.client.get(self.url)
        js = json.loads(resp.data)
        self.assertTrue(js["ok"])

    def test_json_results(self):
        resp = self.client.get(self.url)
        js = json.loads(resp.data)
        self.assertEquals(js["results"], [])


class TestEmptyDb_XML(ClientTestCase):
    """
    Raw XML for empty db.

    Basic layout (see: https://github.com/okfn/iati-datastore/issues/14)
    <result>
       <page>5</page>
       ...metadata here...
       <result-activities>...concatted string...
       </result-activities>
    </result>
    """
    url = '/api/1/access/activities.xml'

    def test_http_ok(self):
        resp = self.client.get(self.url)
        self.assertEquals(200, resp.status_code)

    def test_decode(self):
        resp = self.client.get(self.url)
        # an ElementTree node object does not test as true
        self.assert_(hasattr(ET.fromstring(resp.data), "tag"))

    def test_resp_ok(self):
        resp = self.client.get(self.url)
        xml = ET.fromstring(resp.data)
        self.assertTrue(xml.find('ok').text == 'True')

    def test_results(self):
        resp = self.client.get(self.url)
        xml = ET.fromstring(resp.data)
        self.assertEquals(xml.findall('result-activities'), [])




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
