import os
from unittest import expectedFailure
import json
from xml.etree import ElementTree as ET

from test import AppTestCase
from iatilib import parser, db
from iatilib.model import (Activity, CodelistSector, IndexedResource, RawXmlBlob)


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


def fixture_filename(fix_name):
    return os.path.join(
            os.path.dirname(__file__), "fixtures", fix_name)


def load_fix(fix_name):
    # can be anything, there just needs to be > 0
    db.session.add(CodelistSector(code=47045))
    ir = IndexedResource(id=u"TEST")

    fix_xml = ET.parse(fixture_filename(fix_name))

    for activity_xml in fix_xml.findall('iati-activity'):
        blob = RawXmlBlob(
            parent=ir,
            raw_xml=ET.tostring(
                activity_xml,
                encoding='utf-8').decode('utf-8'))
        db.session.add(blob)
        db.session.commit()

        activity, errors = parser.parse(blob.raw_xml)
        activity.parent_id = blob.id
        db.session.add(activity)
        db.session.commit()


class TestSingleActivity(ClientTestCase):
    """
    Different reprisentations of the same input activity
    """

    def test_xml_activity_count(self):
        load_fix("single_activity.xml")
        resp = self.client.get('/api/1/access/activities.xml')
        xml = ET.fromstring(resp.data)
        self.assertEquals(1, len(xml.findall('.//iati-activity')))

    def test_xml_activity_data(self):
        load_fix("single_activity.xml")
        in_xml = ET.parse(fixture_filename("single_activity.xml"))
        resp = self.client.get('/api/1/access/activities.xml')
        xml = ET.fromstring(resp.data)
        self.assertEquals(
            ET.tostring(in_xml.find('.//iati-activity')),
            ET.tostring(xml.find('.//iati-activity')))

    def test_json_activity_count(self):
        load_fix("single_activity.xml")
        resp = self.client.get('/api/1/access/activities')
        js = json.loads(resp.data)
        self.assertEquals(1, len(js["results"]))

    def test_json_activity_data(self):
        load_fix("single_activity.xml")
        exp = json.load(open(fixture_filename("single_activity.out.json")))
        resp = self.client.get('/api/1/access/activities')
        js = json.loads(resp.data)
        self.assertEquals(exp["results"], js["results"])


class TestManyActivities(ClientTestCase):
    def test_xml_activity_count(self):
        load_fix("many_activities.xml")
        resp = self.client.get('/api/1/access/activities.xml')
        xml = ET.fromstring(resp.data)
        self.assertEquals(2, len(xml.findall('.//iati-activity')))

    def test_xml_activity_data(self):
        load_fix("many_activities.xml")
        in_xml = ET.parse(fixture_filename("many_activities.xml"))
        resp = self.client.get('/api/1/access/activities.xml')
        xml = ET.fromstring(resp.data)
        self.assertEquals(
            ET.tostring(in_xml.find('.//iati-activity')),
            ET.tostring(xml.find('.//iati-activity')))

    def test_json_activity_count(self):
        load_fix("many_activities.xml")
        resp = self.client.get('/api/1/access/activities')
        js = json.loads(resp.data)
        self.assertEquals(2, len(js["results"]))

    def test_json_activity_data(self):
        load_fix("many_activities.xml")
        exp = json.load(open(fixture_filename("many_activities.out.json")))
        resp = self.client.get('/api/1/access/activities')
        js = json.loads(resp.data)
        self.assertEquals(exp["results"], js["results"])
