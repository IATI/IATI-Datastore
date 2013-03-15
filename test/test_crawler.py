import datetime
from unittest import TestCase

import mock

from . import AppTestCase

from iatilib import crawler, db
from iatilib.model import Dataset, Resource


class TestCrawler(AppTestCase):
    @mock.patch('iatilib.crawler.ckanclient.CkanClient.package_register_get')
    def test_fetch_package_list(self, mock):
        mock.return_value = [u"tst-a", u"tst-b"]
        datasets = crawler.fetch_dataset_list()
        self.assertIn("tst-a", [ds.name for ds in datasets])
        self.assertIn("tst-b", [ds.name for ds in datasets])

    @mock.patch('iatilib.crawler.ckanclient.CkanClient.package_register_get')
    def test_update_adds_datasets(self, mock):
        mock.return_value = [u"tst-a"]
        datasets = crawler.fetch_dataset_list()
        mock.return_value = [u"tst-a", u"tst-b"]
        datasets = crawler.fetch_dataset_list()
        self.assertEquals(2, len(datasets))

    @mock.patch('iatilib.crawler.ckanclient.CkanClient.package_entity_get')
    def test_fetch_dataset(self, mock):
        mock.return_value = {"resources": [{"url": "http://foo"}]}
        dataset = crawler.fetch_dataset_metadata(Dataset())
        self.assertEquals(1, len(dataset.resources))
        self.assertEquals("http://foo", dataset.resources[0].url)

    @mock.patch('iatilib.crawler.ckanclient.CkanClient.package_entity_get')
    def test_fetch_dataset_with_many_resources(self, mock):
        mock.return_value = {"resources": [
            {"url": "http://foo"},
            {"url": "http://bar"},
            {"url": "http://baz"},
        ]}
        dataset = crawler.fetch_dataset_metadata(Dataset())
        self.assertEquals(3, len(dataset.resources))

    @mock.patch('iatilib.crawler.ckanclient.CkanClient.package_entity_get')
    def test_fetch_dataset_count_commited_resources(self, mock):
        mock.return_value = {
            "resources": [
                {"url": u"http://foo"},
                {"url": u"http://bar"},
                {"url": u"http://baz"},
            ]
        }
        crawler.fetch_dataset_metadata(Dataset(name=u"tstds"))
        db.session.commit()
        self.assertEquals(3, Resource.query.count())

    @mock.patch('iatilib.crawler.requests')
    def test_fetch_resource_succ(self, mock):
        mock.get.return_value.content = "test"
        mock.get.return_value.status_code = 200
        resource = crawler.fetch_resource(Resource(url="http://foo"))
        self.assertEquals("test", resource.document)
        self.assertEquals(None, resource.last_parsed)
        self.assertEquals(None, resource.last_parse_error)

    @mock.patch('iatilib.crawler.requests')
    def test_fetch_resource_perm_fail(self, mock):
        mock.get.return_value.status_code = 404
        resource = crawler.fetch_resource(Resource(
            url="http://foo",
            document=u"stillhere"
        ))
        self.assertEquals(404, resource.last_status_code)
        self.assertEquals(u"stillhere", resource.document)

    def test_parse_resource_succ(self):
        resource = Resource(document="<iati-activities />")
        resource = crawler.parse_resource(resource)
        self.assertEquals([], resource.activities)
        self.assertEquals(None, resource.last_parse_error)
        self.assertAlmostEquals(
            resource.last_parsed,
            datetime.datetime.utcnow(),
            delta=datetime.timedelta(seconds=5))

    def test_parse_resource_fail(self):
        resource = Resource(document="")
        resource = crawler.parse_resource(resource)
        self.assertEquals([], resource.activities)
        self.assertEquals(None, resource.last_parsed)
        self.assertNotEquals(None, resource.last_parse_error)


class TestDate(TestCase):
    def test_date(self):
        self.assertEquals(
            "Wed, 22 Oct 2008 10:52:40 GMT",
            crawler.http_date(datetime.datetime(2008, 10, 22, 11, 52, 40))
        )
