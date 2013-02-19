import datetime
from StringIO import StringIO
from unittest import TestCase
from functools import partial
import csv

from .factories import create_activity
from iatilib.frontend import serialize


def load_csv(data):
    sio = StringIO(data)
    return list(csv.DictReader(sio))

create_activity = partial(create_activity, _commit=False)


class TestCSVSerializer(TestCase):
    def process(self, data):
        return load_csv(serialize.csv(data))

    def assertField(self, mapping, row):
        assert len(mapping) == 1
        key, val = mapping.items()[0]
        self.assertIn(key, row)
        self.assertEquals(row[key], val)

    def test_empty(self):
        data = self.process([])
        self.assertEquals(0, len(data))

    def test_len_one(self):
        data = self.process([create_activity()])
        self.assertEquals(1, len(data))

    def test_len_many(self):
        data = self.process([create_activity(), create_activity()])
        self.assertEquals(2, len(data))

    def test_field_1(self):
        data = self.process([create_activity(iatiidentifier__text="TEST")])
        self.assertField({"iati-identifier": "TEST"}, data[0])

    def test_field_2(self):
        data = self.process([create_activity(reporting_org__text="TESTRO")])
        self.assertField({"reporting-org": "TESTRO"}, data[0])

    def test_field_3(self):
        data = self.process([create_activity(title__text="testtt")])
        self.assertField({"title": "testtt"}, data[0])

    def test_date_field(self):
        data = self.process([create_activity(
            start_planned=datetime.date(2012, 1, 1))])
        self.assertField({"start-planned": "2012-01-01"}, data[0])
