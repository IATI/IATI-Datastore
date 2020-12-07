import datetime
from unittest import TestCase

import mock

from . import AppTestCase, fixture_filename
from . import factories as fac

from iatilib import crawler, db, parse
from iatilib.model import Dataset, Resource, Activity, DeletedActivity


class TestCrawler(AppTestCase):
    @mock.patch('iatilib.crawler.registry')
    def test_fetch_package_list(self, mock):
        mock.action.package_list.return_value = [u"tst-a", u"tst-b"]
        datasets = crawler.fetch_dataset_list()
        mock.action.package_list.assert_called_once_with()
        self.assertIn("tst-a", [ds.name for ds in datasets])
        self.assertIn("tst-b", [ds.name for ds in datasets])

    @mock.patch('iatilib.crawler.registry')
    def test_update_adds_datasets(self, mock):
        mock.action.package_list.return_value = [u"tst-a"]
        datasets = crawler.fetch_dataset_list()
        mock.action.package_list.assert_called_once_with()
        mock.action.package_list.return_value = [u"tst-a", u"tst-b"]
        datasets = crawler.fetch_dataset_list()
        self.assertEquals(2, datasets.count())

    @mock.patch('iatilib.crawler.registry')
    def test_update_deletes_datasets(self, mock):
        mock.action.package_list.return_value = [u"tst-a", u"tst-b"]
        datasets = crawler.fetch_dataset_list()
        mock.action.package_list.assert_called_once_with()
        mock.action.package_list.return_value = [u"tst-a"]
        datasets = crawler.fetch_dataset_list()
        self.assertEquals(1, datasets.count())

    @mock.patch('iatilib.crawler.registry')
    def test_fetch_dataset(self, mock):
        mock.action.package_show.return_value = {
            "resources": [{"url": "http://foo"}],
        }
        dataset = crawler.fetch_dataset_metadata(Dataset())
        mock.action.package_show.assert_called_once_with(id=None)
        self.assertEquals(1, len(dataset.resources))
        self.assertEquals("http://foo", dataset.resources[0].url)

    @mock.patch('iatilib.crawler.registry')
    def test_fetch_package_search(self, mock):
        mock.action.package_search.return_value = {
            'count': 2,
            'results': [
                {'name': 'tst-a', 'state': 'active'},
                {'name': 'tst-b', 'state': 'active'},
            ]
        }
        date = datetime.date(2000, 1, 2)
        datasets = crawler.fetch_dataset_list(date)
        # check the solr parameters are formed correctly
        mock.action.package_search.assert_any_call(
            fq='metadata_modified:[2000-01-02T00:00:00Z TO NOW]')

        # check that the result of of fetch_dataset_list are only the 2 datasets
        self.assertEquals(set(['tst-a', 'tst-b']), set([ds.name for ds in datasets]))

    @mock.patch('iatilib.crawler.registry')
    def test_fetch_package_search_update(self, mock):
        #initial call to fetch dataset list sets up 3 datasets inside the
        # datastore
        mock.action.package_list.return_value = [
            u"tst-deleted", u"tst-not-modified", 'tst-modified'
        ]
        crawler.fetch_dataset_list()

        # the second call, we are giving a time delta, this time the registry
        # has 3 modified datasets, 1 deleted, 1 modified, 1 new
        mock.action.package_search.return_value = {
            'count': 3,
            'results': [
                {'name': 'tst-deleted', 'state': 'deleted'},
                {'name': 'tst-modified', 'state': 'active'},
                {'name': 'tst-new', 'state': 'active'},
            ]
        }
        date = datetime.date(2000, 1, 2)
        datasets = set([ds.name for ds in crawler.fetch_dataset_list(date)])

        # we want to check that the result returned are only the modified/new
        # datasets as these are the ones that are sent to the job queues
        # normally a call without a time delta results in all the datasets
        # being sent to the job queues
        self.assertEquals(set(['tst-modified', 'tst-new']), datasets)

        # finally we check over all the datasets to make sure nothing has
        # happened to the not modified dataset, and that tst-deleted was
        # actually deleted.
        all_datasets = set([i.name for i in Dataset.query.all()])
        self.assertEquals(
            set(['tst-not-modified', 'tst-modified', 'tst-new']),
            all_datasets,
        )

    @mock.patch('iatilib.crawler.registry')
    def test_fetch_dataset_with_many_resources(self, mock):
        mock.action.package_show.return_value = {
            "resources": [
                {"url": "http://foo"}, {"url": "http://bar"},
                {"url": "http://baz"},
            ]
        }
        dataset = crawler.fetch_dataset_metadata(Dataset())
        mock.action.package_show.assert_called_once_with(id=None)
        self.assertEquals(3, len(dataset.resources))

    @mock.patch('iatilib.crawler.registry')
    def test_fetch_dataset_count_commited_resources(self, mock):
        mock.action.package_show.return_value = {
            "resources": [
                {"url": "http://foo"},
                {"url": "http://bar"},
                {"url": "http://baz"},
            ]
        }
        crawler.fetch_dataset_metadata(Dataset(name=u"tstds"))
        mock.action.package_show.assert_called_once_with(id="tstds")
        db.session.commit()
        self.assertEquals(3, Resource.query.count())

    @mock.patch('iatilib.crawler.requests')
    def test_fetch_resource_succ(self, mock):
        mock.get.return_value.content = "test"
        mock.get.return_value.status_code = 200
        resource = crawler.fetch_resource(Resource(url="http://foo"))
        self.assertEquals(b"test", resource.document)
        self.assertEquals(None, resource.last_parsed)
        self.assertEquals(None, resource.last_parse_error)

    @mock.patch('iatilib.crawler.requests')
    def test_fetch_resource_perm_fail(self, mock):
        mock.get.return_value.status_code = 404
        resource = crawler.fetch_resource(Resource(
            url="http://foo",
            document=b"stillhere"
        ))
        self.assertEquals(404, resource.last_status_code)
        self.assertEquals(b"stillhere", resource.document)

    def test_parse_resource_succ(self):
        resource = Resource(document=b"<iati-activities />", url="http://foo")
        resource = crawler.parse_resource(resource)
        self.assertEquals([], list(resource.activities))
        self.assertEquals(None, resource.last_parse_error)
        now = datetime.datetime.utcnow()
        self.assertAlmostEquals(
            resource.last_parsed,
            now,
            delta=datetime.timedelta(seconds=15))

    def test_parse_resource_succ_replaces_activities(self):
        # what's in the db before the resource is updated
        act = fac.ActivityFactory.build(iati_identifier="deleted_activity")
        resource = fac.ResourceFactory.create(
            url=u"http://test",
            activities=[act]
        )
        # the updated resource (will remove the activities)
        resource.document=b"<iati-activities />"
        resource = crawler.parse_resource(resource)
        db.session.commit()
        self.assertEquals(None, Activity.query.get(act.iati_identifier))
        self.assertIn(
            "deleted_activity",
            [da.iati_identifier for da in DeletedActivity.query.all()]
        )

    def test_deleted_activity_removal(self):
        db.session.add(DeletedActivity(iati_identifier='test_deleted_activity',
                deletion_date=datetime.datetime(2000, 1, 1)))
        db.session.commit()
        resource = fac.ResourceFactory.create(
            url=u"http://test",
            document=b"""
                <iati-activities>
                  <iati-activity>
                    <iati-identifier>test_deleted_activity</iati-identifier>
                    <title>test_deleted_activity</title>
                    <reporting-org ref="GB-CHC-202918" type="21">Oxfam GB</reporting-org>
                  </iati-activity>
                </iati-activities>
            """,
        )
        self.assertIn(
            "test_deleted_activity",
            [da.iati_identifier for da in db.session.query(DeletedActivity).all()]
        )
        resource = crawler.parse_resource(resource)
        db.session.commit()
        self.assertNotIn(
            "test_deleted_activity",
            [da.iati_identifier for da in DeletedActivity.query.all()]
        )

    def test_last_changed_datetime(self):
        resource = fac.ResourceFactory.create(
            url=u"http://test",
            document=b"""
                <iati-activities>
                  <iati-activity>
                    <iati-identifier>test_deleted_activity</iati-identifier>
                    <title>test_deleted_activity</title>
                    <reporting-org ref="GB-CHC-202918" type="21">Oxfam GB</reporting-org>
                  </iati-activity>
                  <iati-activity>
                    <iati-identifier>test_deleted_activity_2</iati-identifier>
                    <title>test_deleted_activity_2</title>
                    <reporting-org ref="GB-CHC-202918" type="21">Oxfam GB</reporting-org>
                  </iati-activity>
                </iati-activities>
            """
        )
        crawler.parse_resource(resource)
        db.session.commit()
        db.session.query(Activity).update(
            values={'last_change_datetime': datetime.datetime(2000, 1, 1)},
            synchronize_session=False)
        db.session.commit()
        crawler.parse_resource(resource)
        acts = db.session.query(Activity).all()
        self.assertEquals(datetime.datetime(2000, 1, 1),
            acts[0].last_change_datetime)



    def test_parse_resource_fail(self):
        resource = Resource(document=b"", url="")
        with self.assertRaises(parse.ParserError):
            resource = crawler.parse_resource(resource)
            self.assertEquals(None, resource.last_parsed)

    @mock.patch('iatilib.crawler.registry')
    def test_deleted_activities(self, mock):
        fac.DatasetFactory.create(
            name='deleteme',
            resources=[ fac.ResourceFactory.create(
                url=u"http://yes",
                activities=[
                    fac.ActivityFactory.build(
                        iati_identifier=u"deleted_activity",
                        title=u"orig",
                    )
                ]
            )]
        )
        mock.action.package_list.return_value = [u"tst-a", u"tst-b"]
        self.assertIn("deleteme", [ds.name for ds in Dataset.query.all()])
        datasets = crawler.fetch_dataset_list()
        self.assertNotIn("deleteme", [ds.name for ds in datasets])
        self.assertIn(
            "deleted_activity",
            [da.iati_identifier for da in DeletedActivity.query.all()]
        )

    def test_document_metadata(self):
        res = fac.ResourceFactory.create(
            url=u"http://res2",
            document=open(fixture_filename("complex_example_dfid.xml")).read().encode()
        )
        result = crawler.parse_resource(res)

        self.assertEquals("1.00", result.version)


class TestResourceUpdate(AppTestCase):
    def test_activity_in_two_resources(self):
        # If an activity is reported in two resources, the one in the db
        # wins.

        # Example: Activity GB-1-111635 appears in two resources.
        # 'http://projects.dfid.gov.uk/iati/Region/798'
        # 'http://projects.dfid.gov.uk/iati/Country/CD'

        # this resouce was the first to import activity "47045-ARM-202-G05-H-00"
        fac.ResourceFactory.create(
            url=u"http://res1",
            activities=[
                fac.ActivityFactory.build(
                    iati_identifier=u"47045-ARM-202-G05-H-00",
                    title=u"orig",
                )
            ]
        )
        # this resource has just been retreived, it also contains an
        # activity "47045-ARM-202-G05-H-00"
        fac.ResourceFactory.create(
            url=u"http://res2",
            document=open(fixture_filename("single_activity.xml")).read().encode()
        )

        crawler.update_activities(u"http://res2")
        self.assertEquals(
            u"orig",
            Activity.query.get(u"47045-ARM-202-G05-H-00").title
        )


class TestDate(TestCase):
    def test_date(self):
        # I'm not installing pytz for a single unit test
        ZERO = datetime.timedelta(0)

        class UTC(datetime.tzinfo):
            def utcoffset(self, dt):
                return ZERO

            def tzname(self, dt):
                return "UTC"

            def dst(self, dt):
                return ZERO

        utc = UTC()

        self.assertEquals(
            "Wed, 22 Oct 2008 11:52:40 GMT",
            crawler.http_date(
                datetime.datetime(2008, 10, 22, 11, 52, 40, tzinfo=utc))
        )
