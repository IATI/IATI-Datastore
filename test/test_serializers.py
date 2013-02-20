import datetime
from StringIO import StringIO
from unittest import TestCase
from functools import partial
import unicodecsv
from xml.etree import ElementTree as ET


from .factories import create_activity
from iatilib.frontend import serialize


def load_csv(data):
    sio = StringIO(data)
    return list(unicodecsv.DictReader(sio, encoding="utf-8"))

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

    def test_quoting(self):
        data = self.process([create_activity(reporting_org__text=u"l,r")])
        self.assertField({"reporting-org": "l,r"}, data[0])

    def test_unicode(self):
        data = self.process([create_activity(reporting_org__text=u"\u2603")])
        self.assertField({"reporting-org": u"\u2603"}, data[0])


class TestXMLSerializer(TestCase):
    def process(self, items):
        return ET.fromstring(serialize.xml(items).encode("utf-8"))

    def test_raw(self):
        # the xml that's output is the stuff in raw_xml
        data = self.process([
            create_activity(activity_parent__raw_xml=u"<test />")
            ])
        self.assert_(data.find(".//test") is not None)

    def test_unicode(self):
        data = self.process([
            create_activity(parent__raw_xml=u"<test>\u2603</test>")
            ])
        self.assertEquals(u"\u2603", data.find(".//test").text)

    def test_namespace(self):
        # raw xml that goes in with a ns prefix should come out with one
        # (even though it's meaningless without the ns declaration)
        # it's lousy to do this with string tests, but ET/Expat really
        # doesn't want to load xml with unbound prefixes
        items = [create_activity(parent__raw_xml=u"<t:test />")]
        ser_data = serialize.xml(items)
        self.assertIn("t:test", ser_data)
