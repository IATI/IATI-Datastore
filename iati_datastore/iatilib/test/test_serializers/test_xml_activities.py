from unittest import TestCase

from xml.etree import ElementTree as ET

from iatilib.test import factories as fac
from iatilib.test.test_serializers import TestWrapper
from iatilib.frontend import serialize


class TestXMLSerializer(TestCase):
    def process(self, items):
        pagination = TestWrapper(items, 0, 0, 0)
        return ET.fromstring(u"".join(serialize.xml(pagination)).encode("utf-8"))

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
        ser_data = "".join(serialize.xml(TestWrapper(items, 0, 0, 0)))
        self.assertIn("t:test", ser_data)

    def test_results_count(self):
        data =[ fac.ActivityFactory.build(raw_xml=u"<test />") ]
        ser_data = "".join(serialize.xml(TestWrapper(data, 1, 0, 0)))
        result = ET.fromstring(ser_data)
        self.assertEquals("1", result[1][0][0].text)

    def test_version(self):
        data = self.process([
            fac.ActivityFactory.build(raw_xml=u"<iati-activity></iati-activity>", version='x.yy')
        ])
        self.assertEquals('x.yy', data.find('.//iati-activity').attrib['{http://datastore.iatistandard.org/ns}version'])
