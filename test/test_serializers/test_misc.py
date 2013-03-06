import datetime
from StringIO import StringIO
from unittest import TestCase
from functools import partial
import unicodecsv
from xml.etree import ElementTree as ET

from test import factories as fac
from test.factories import create_activity
from iatilib.frontend import serialize


def load_csv(data):
    sio = StringIO(data)
    return list(unicodecsv.DictReader(sio, encoding="utf-8"))


for factory in (create_activity,):
    globals()[factory.__name__] = partial(factory, _commit=False)





class TestXMLSerializer(TestCase):
    def process(self, items):
        return ET.fromstring(serialize.xml(items).encode("utf-8"))

    def test_raw(self):
        # the xml that's output is the stuff in raw_xml
        data = self.process([
            fac.ActivityFactory.build(raw_xml=u"<test />")
        ])
        self.assert_(data.find(".//test") is not None)

    def test_unicode(self):
        data = self.process([
            fac.ActivityFactory.build(raw_xml=u"<test>\u2603</test>")
        ])
        self.assertEquals(u"\u2603", data.find(".//test").text)

    def test_namespace(self):
        # raw xml that goes in with a ns prefix should come out with one
        # (even though it's meaningless without the ns declaration)
        # it's lousy to do this with string tests, but ET/Expat really
        # doesn't want to load xml with unbound prefixes
        items = [fac.ActivityFactory.build(raw_xml=u"<t:test />")]
        ser_data = serialize.xml(items)
        self.assertIn("t:test", ser_data)
