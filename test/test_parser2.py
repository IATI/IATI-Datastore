import os

from lxml import etree as ET
from defusedxml import EntitiesForbidden

from . import AppTestCase

from iatilib import parser


def fixture_filename(fix_name):
    return os.path.join(
            os.path.dirname(__file__), "fixtures", fix_name)


class TestParser(AppTestCase):
    def test_defused_xml(self):
        # Avoid some well-known xml attacks
        # https://bitbucket.org/tiran/defusedxml/overview
        bomb = """<!DOCTYPE bomb [
            <!ENTITY a "xxxxxxx... a couple of ten thousand chars">
            ]>
            <bomb>&a;&a;&a;... repeat</bomb>"""

        with self.assertRaises(EntitiesForbidden):
            parser.parse(bomb)

    def test_foo(self):
        activity, errors = parser.parse(
            open(fixture_filename("default_currency.xml")).read(),
            validate=False)
        self.assertEquals(activity.transaction[0].value.currency, "USD")
