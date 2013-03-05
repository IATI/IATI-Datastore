import os
import codecs
from unittest import TestCase

from defusedxml import EntitiesForbidden

from . import AppTestCase
from . import factories as fac

from iatilib import parser


class TestParser(TestCase):
    # no need for this to set the app up, so just a TestCase
    def test_defused_xml(self):
        # Avoid some well-known xml attacks
        # https://bitbucket.org/tiran/defusedxml/overview
        bomb = """<!DOCTYPE bomb [
            <!ENTITY a "xxxxxxx... a couple of ten thousand chars">
            ]>
            <bomb>&a;&a;&a;... repeat</bomb>"""

        with self.assertRaises(EntitiesForbidden):
            parser.parse(bomb)

    def test_default_currency(self):
        activity, errors = parser.parse(
            open(fixture_filename("default_currency.xml")).read(),
            validate=False)
        self.assertEquals(activity.transaction[0].value.currency, "USD")


def fixture_filename(fix_name):
    return os.path.join(
        os.path.dirname(__file__), "fixtures", fix_name)


def fixture(fix_name, encoding='utf-8'):
    return codecs.open(fixture_filename(fix_name), encoding=encoding).read()


class TestParserModels(AppTestCase):
    # these do need db access
    def test_new_activity(self):
        # new activities should have been inserted when they are
        # returned by the parser.
        blob = fac.RawXmlBlobFactory.create(
            parsed=False,
            raw_xml=fixture("default_currency.xml"),
        )
        activity = parser.parse_blob(blob, validate=False)
        self.assertNotEquals(None, activity.id)

    def test_broke_activity_01(self):
        from iatilib import db
        from iatilib import model
        db.session.add(model.CodelistSector())
        db.session.commit()
        blob = fac.RawXmlBlobFactory.create(
            parsed=True,
            raw_xml=fixture("broken_activity_01.xml"),
            activity=fac.create_activity()
        )
        activity = parser.parse_blob(blob)
        self.assertNotEquals(None, activity.id)
