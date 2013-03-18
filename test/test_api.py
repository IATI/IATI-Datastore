import os
import json
from xml.etree import ElementTree as ET
import csv
from StringIO import StringIO

from unittest import skip
import mock

from test import AppTestCase
from iatilib import parse, db


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

    def test_content_type(self):
        resp = self.client.get(self.url)
        self.assertEquals("application/json", resp.content_type)

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

    def test_content_type(self):
        resp = self.client.get(self.url)
        self.assertEquals("application/xml; charset=utf-8", resp.content_type)

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

    def test_root_element(self):
        resp = self.client.get(self.url)
        xml = ET.fromstring(resp.data)
        self.assertEquals(xml.tag, "result")


class TestEmptyDb_ActivityCSV(ClientTestCase):
    """
    CSV for empty db
    """
    url = '/api/1/access/activities.csv'

    def test_http_ok(self):
        resp = self.client.get(self.url)
        self.assertEquals(200, resp.status_code)

    def test_content_type(self):
        resp = self.client.get(self.url)
        self.assertEquals("text/csv; charset=utf-8", resp.content_type)

    def test_fields(self):
        resp = self.client.get(self.url)
        headers = next(csv.reader(StringIO(resp.data)))
        for exp in ["start-planned", "start-actual"]:
            self.assertIn(exp, headers)


class TestEmptyDb_TransactionCSV(ClientTestCase):
    """
    CSV for empty db
    """
    url = '/api/1/access/transactions.csv'

    def test_http_ok(self):
        resp = self.client.get(self.url)
        self.assertEquals(200, resp.status_code)

    def test_content_type(self):
        resp = self.client.get(self.url)
        self.assertEquals("text/csv; charset=utf-8", resp.content_type)


class TestEmptyDb_BudgetCSV(ClientTestCase):
    """
    CSV for empty db
    """
    url = '/api/1/access/budgets.csv'

    def test_http_ok(self):
        resp = self.client.get(self.url)
        self.assertEquals(200, resp.status_code)

    def test_content_type(self):
        resp = self.client.get(self.url)
        self.assertEquals("text/csv; charset=utf-8", resp.content_type)



def fixture_filename(fix_name):
    return os.path.join(
            os.path.dirname(__file__), "fixtures", fix_name)


def load_fix(fix_name):
    activities = parse.document(fixture_filename(fix_name))
    db.session.add_all(activities)
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
        x1 = in_xml.find('.//iati-activity')
        x2 = xml.find('.//iati-activity')
        self.assertEquals(x1, x2)

    @skip("json rep")
    def test_json_activity_count(self):
        load_fix("single_activity.xml")
        resp = self.client.get('/api/1/access/activities')
        js = json.loads(resp.data)
        self.assertEquals(1, len(js["results"]))

    @skip("json rep")
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

    @skip("json rep")
    def test_json_activity_count(self):
        load_fix("many_activities.xml")
        resp = self.client.get('/api/1/access/activities')
        js = json.loads(resp.data)
        self.assertEquals(2, len(js["results"]))

    @skip("json rep")
    def test_json_activity_data(self):
        load_fix("many_activities.xml")
        exp = json.load(open(fixture_filename("many_activities.out.json")))
        resp = self.client.get('/api/1/access/activities')
        js = json.loads(resp.data)
        self.assertEquals(exp["results"], js["results"])

    def test_csv_activity_count(self):
        load_fix("many_activities.xml")
        resp = self.client.get('/api/1/access/activities.csv')
        reader = csv.DictReader(StringIO(resp.data))
        self.assertEquals(2, len(list(reader)))


class TestPagination(ClientTestCase):
    @mock.patch('iatilib.frontend.api1.dsfilter.activities')
    def test_defaults(self, mock):
        self.client.get('/api/1/access/activities')
        self.assertEquals(1, mock.return_value.paginate.call_count)

    def test_missing_page(self):
        resp = self.client.get('/api/1/access/activities?page=2')
        self.assertEquals(404, resp.status_code)

    def test_invalid_page(self):
        resp = self.client.get('/api/1/access/activities?page=-1')
        self.assertEquals(404, resp.status_code)


class ApiViewMixin(object):
    @mock.patch('iatilib.frontend.api1.validators.activity_api_args')
    def test_validator_called(self, mock):
        self.client.get(self.base_url)
        self.assertEquals(1, mock.call_count)

    def test_filter_called(self):
        with mock.patch(self.filter) as mm:
            self.client.get(self.base_url + '?country_code=MW')
            self.assertEquals(1, mm.call_count)

    def test_serializer_called(self):
        with mock.patch(self.serializer) as mm:
            self.client.get(self.base_url)
            self.assertEquals(1, mm.call_count)

    def test_invalid_format(self):
        resp = self.client.get(self.base_url + ".zzz")
        self.assertEquals(404, resp.status_code)


class TestActivityView(ClientTestCase, ApiViewMixin):
    base_url = '/api/1/access/activities.csv'
    filter = 'iatilib.frontend.api1.dsfilter.activities'
    serializer = 'iatilib.frontend.api1.serialize.csv'


class TestActivityBySectorView(ClientTestCase, ApiViewMixin):
    base_url = '/api/1/access/activities/by_sector.csv'
    filter = 'iatilib.frontend.api1.ActivityBySectorView.filter'
    serializer = 'iatilib.frontend.api1.ActivityBySectorView.serializer'


class TestActivityByCountryView(ClientTestCase, ApiViewMixin):
    base_url = '/api/1/access/activities/by_country.csv'
    filter = 'iatilib.frontend.api1.ActivityByCountryView.filter'
    serializer = 'iatilib.frontend.api1.ActivityByCountryView.serializer'


class TestTransactionView(ClientTestCase, ApiViewMixin):
    base_url = '/api/1/access/transactions.csv'
    filter = 'iatilib.frontend.api1.TransactionsView.filter'
    serializer = 'iatilib.frontend.api1.TransactionsView.serializer'


class TestBudgetView(ClientTestCase):
    base_url = '/api/1/access/budgets.csv'
    filter = 'iatilib.frontend.api1.dsfilter.budgets'
    serializer = 'iatilib.frontend.api1.serialize.budget_csv'
