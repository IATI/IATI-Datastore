import os
import codecs
import datetime
from unittest import TestCase, skip

import mock
from lxml import etree as ET

from . import db

from . import AppTestCase, fixture_filename

from iatilib import parse, codelists as cl


def fixture(fix_name, encoding='utf-8'):
    return codecs.open(fixture_filename(fix_name), encoding=encoding).read()


class TestParseActivity(AppTestCase):
    def test_id(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(
            u"47045-ARM-202-G05-H-00",
            act.iati_identifier)

    def test_title(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(
            (u"Support to the National Program on the Response to HIV " +
             u"Epicemic in the Republic of Armenia"),
            act.title)

    def test_description(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assert_(act.description.startswith(
            u"While Armenia is still a country with a concentrated HIV"))

    def test_reporting_org_ref(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(u"47045", act.reporting_org.ref)

    def test_reporting_org_type(self):
        act = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(
            cl.OrganisationType.multilateral,
            act.reporting_org.type
        )

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
        self.assertEquals(5, len(act.sector_percentages))

    def test_raw_xml(self):
        act = parse.activity(fixture_filename("default_currency.xml"))
        norm_xml = ET.tostring(ET.parse(fixture_filename("default_currency.xml")))
        self.assertEquals(norm_xml, act.raw_xml)

    def test_no_start_actual(self):
        activities = parse.document(fixture_filename("missing_dates.xml"))
        act = {a.iati_identifier:a for a in activities}
        self.assertEquals(None, act[u"GB-CHC-272465-680"].start_actual)

    def test_budget(self):
        activity = parse.activity(fixture("default_currency.xml"))
        self.assertEquals(6, len(activity.budgets))


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

    def test_save_repeated_participation(self):
        activities = parse.document(fixture_filename("repeated_participation.xml"))
        db.session.add_all(activities)
        db.session.commit()

    def test_different_roles(self):
        activities = parse.document(fixture_filename("same_orgs_different_roles.xml"))
        db.session.add_all(activities)
        db.session.commit()

    def test_big_values(self):
        activities = parse.document(fixture_filename("big_value.xml"))
        db.session.add_all(activities)
        db.session.commit()


class TestSector(AppTestCase):
    def test_code(self):
        sec = parse.sector_percentages([ET.XML(
            u'<sector vocabulary="DAC" code="16010">Child Protection Systems Strengthening</sector>'
        )])[0]
        self.assertEquals(cl.Sector.social_welfare_services, sec.sector)

    def test_missing_code(self):
        sec = parse.sector_percentages([ET.XML(
            u'<sector vocabulary="DAC">Child Protection Systems Strengthening</sector>'
        )])[0]
        self.assertEquals(None, sec.sector)

    def test_missing_everything(self):
        sec = parse.sector_percentages([ET.XML(
            u'<sector />'
        )])
        self.assertEquals([], sec)


class TestOrganisation(AppTestCase):
    def test_org_role_looseness(self):
        # organisationrole should be "Implementing" but can be "implementing"
        orgrole = parse.participating_orgs([ET.XML(
            u'<test role="implementing" ref="test" />'
        )])[0]
        self.assertEquals(orgrole.role, cl.OrganisationRole.implementing)

    def test_org_type(self):
        orgtype = parse.reporting_org(ET.XML(
            u"""<reporting-org ref="GB-CHC-202918" type="21" />"""
        ))
        self.assertEquals(cl.OrganisationType.international_ngo, orgtype.type)

    def test_org_type_missing(self):
        orgtype = parse.reporting_org(ET.XML(
            u"""<reporting-org ref="GB-CHC-202918" />"""
        ))
        self.assertEquals(None, orgtype.type)



class TestParticipation(AppTestCase):
    def test_repeated_participation(self):
        # Identical participations should be filtered
        participations = parse.participating_orgs([
            ET.XML(u'<participating-org ref="GB-CHC-272465" role="implementing" type="21">Concern Universal</participating-org>'),
            ET.XML(u'<participating-org ref="GB-CHC-272465" role="implementing" type="21">Concern Universal</participating-org>')
        ])
        self.assertEquals(1, len(participations))

    def test_same_org_different_role(self):
        participations = parse.participating_orgs([
            ET.XML(u'<participating-org ref="GB-CHC-272465" role="implementing" type="21">Concern Universal</participating-org>'),
            ET.XML(u'<participating-org ref="GB-CHC-272465" role="Funding" type="21">Concern Universal</participating-org>')
        ])
        self.assertEquals(2, len(participations))


class TestActivity(AppTestCase):
    def test_missing_id(self):
        # missing activity id means don't parse
        activities = parse.document(ET.XML(
            u'''
              <iati-activities>
                <iati-activity default-currency="GBP" xml:lang="en">
                    <reporting-org ref="GB-2" type="15">CDC Group plc</reporting-org>
                    <activity-status code="2">Implementation</activity-status>
                </iati-activity>
              </iati-activities>
                '''))
        self.assertEquals(0, len(list(activities)))


class TestTransaction(AppTestCase):
    def test_missing_code(self):
        transactions = parse.transactions([
            ET.XML(u'''<transaction>
                <transaction-date iso-date="31/12/2011" />
                <description>test</description>
                <value value-date="31/12/2011">116,017</value>
                <transaction-type>Disbursement</transaction-type>
                </transaction>''')
        ])
        self.assertEquals(0, len(transactions))

    def test_big_value(self):
        transaction = parse.transactions([
            ET.XML(u'''<transaction>
                <transaction-date iso-date="31/12/2011" />
                <description>test</description>
                <value value-date="31/12/2011">2663000000</value>
                <transaction-type code="D">Disbursement</transaction-type>
                </transaction>''')
        ])[0]
        self.assertEquals(2663000000, transaction.value_amount)

    @mock.patch('iatilib.parse.iati_int')
    def test_iati_int_called(self, mock):
        transaction = parse.transactions([
            ET.XML(u'''<transaction>
                <transaction-date iso-date="31/12/2011" />
                <description>test</description>
                <value value-date="31/12/2011">-1000</value>
                <transaction-type code="D">Disbursement</transaction-type>
                </transaction>''')
        ])[0]
        self.assertEquals(1, mock.call_count)


class TestBudget(TestCase):
    def parse_budget(self):
        return parse.budgets([ET.XML("""
            <budget type="1">
                <period-end iso-date="2010-03-31" />
                <value currency="USD">1840852</value>
            </budget>
        """)])[0]

    def test_budget_type(self):
        budget = self.parse_budget()
        self.assertEquals(budget.type, cl.BudgetType.original)

    def test_budget_type_looser(self):
        budget = parse.budgets([ET.XML("""
            <budget type="Original">
                <period-end iso-date="2010-03-31" />
                <value currency="USD">1840852</value>
            </budget>
        """)])[0]
        self.assertEquals(budget.type, cl.BudgetType.original)

    def test_budget_period_end(self):
        budget = self.parse_budget()
        self.assertEquals(budget.period_end, datetime.date(2010, 3, 31))

    def test_budget_period_start(self):
        budget = self.parse_budget()
        self.assertEquals(budget.period_start, None)

    def test_value_currency(self):
        budget = self.parse_budget()
        self.assertEquals(budget.value_currency, cl.Currency.us_dollar)

    def test_value_amount(self):
        budget = self.parse_budget()
        self.assertEquals(budget.value_amount, 1840852)



class TestDates(TestCase):
    def test_correct_date(self):
        self.assertEquals(
            datetime.date(2010, 1, 2),
            parse.iati_date("2010-01-02"))

    def test_variation_1(self):
        self.assertEquals(
            datetime.date(2011, 12, 31),
            parse.iati_date("31/12/2011"))


class TestValue(TestCase):
    def test_thousand_sep(self):
        self.assertEquals(20026, parse.iati_int(u"20,026"))

    def test_sign(self):
        self.assertEquals(-20026, parse.iati_int(u"-20026"))


class TestXVal(TestCase):
    def test_missing_val(self):
        with self.assertRaises(parse.MissingValue):
            parse.xval(ET.XML(u"<foo />"), "bar")

    def test_default_val(self):
        self.assertEquals(
            None,
            parse.xval(ET.XML(u"<foo />"), "bar", None))

