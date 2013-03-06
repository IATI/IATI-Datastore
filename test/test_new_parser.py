import os
import codecs
import datetime

from lxml import etree as ET

from . import db

from . import AppTestCase

from iatilib import parse, codelists as cl


def fixture_filename(fix_name):
    return os.path.join(
        os.path.dirname(__file__), "fixtures", fix_name)


def fixture(fix_name, encoding='utf-8'):
    return codecs.open(fixture_filename(fix_name), encoding=encoding).read()


class TestParseActivity(AppTestCase):
    def test_id(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(
            u"47045-ARM-202-G05-H-00",
            act.iati_identifier)

    def test_reporting_org_ref(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(u"47045", act.reporting_org.ref)

    def test_activity_websites(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(
            [u"http://portfolio.theglobalfund.org/en/Grant/Index/ARM-202-G05-H-00"],
            act.websites)

    def test_participating_org(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(
            cl.OrganisationRole.funding,
            act.participating_orgs[0].role)

    def test_rejects_participatng_org_without_ref(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(1, len(act.participating_orgs))

    def test_recipient_country_percentages(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(1, len(act.recipient_country_percentages))
        self.assertEquals(
            cl.Country.armenia,
            act.recipient_country_percentages[0].country)

    def test_transaction_count(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(1, len(act.transactions))

    def test_transaction_type(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(
            cl.TransactionType.commitment,
            act.transactions[0].type)

    def test_transaction_date(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(
            datetime.date(2009, 10, 01),
            act.transactions[0].date)

    def test_transaction_value_date(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(
            datetime.date(2009, 10, 01),
            act.transactions[0].value_date)

    def test_transaction_value_amount(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(
            3991675,
            act.transactions[0].value_amount)

    def test_transaction_currency(self):
        # currency is picked up from default currency
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(
            cl.Currency.us_dollar,
            act.transactions[0].value_currency)

    def test_transaction_value_composite(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(
            (datetime.date(2009, 10, 01), 3991675, cl.Currency.us_dollar),
            act.transactions[0].value)

    def test_date_start_planned(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(None, act.start_planned)

    def test_date_start_actual(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(datetime.date(2009, 10, 01), act.start_actual)

    def test_date_end_planned(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(None, act.end_planned)

    def test_date_end_actual(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(None, act.end_actual)

    def test_sector_percentage_count(self):
        act = next(parse.document(
            fixture("complex_example_dfid.xml", encoding=None)))
        self.assertEquals(2, len(act.sector_percentages))

    def test_sector_percentage(self):
        act = next(parse.document(
            fixture("complex_example_dfid.xml", encoding=None)))
        self.assertEquals(
            cl.Sector.sectors_not_specified,
            act.sector_percentages[0].sector)
        self.assertEquals(
            cl.Vocabulary.oecd_development_assistance_committee,
            act.sector_percentages[0].vocabulary)

    def test_raw_xml(self):
        act = parse.activity(fixture("default_currency.xml"))
        norm_xml = ET.tostring(ET.fromstring(fixture("default_currency.xml")))
        self.assertEquals(norm_xml, act.raw_xml)


class TestFunctional(AppTestCase):
    def test_save_parsed_activity(self):
        act = parse.activity(fixture("default_currency.xml"))
        db.session.add(act)
        db.session.commit()

    def test_save_complex_example(self):
        acts = parse.document(
            fixture("complex_example_dfid.xml", encoding=None))
        db.session.add_all(acts)
        db.session.commit()
