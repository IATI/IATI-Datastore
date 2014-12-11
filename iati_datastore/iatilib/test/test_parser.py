import os
import codecs
import datetime
from decimal import Decimal
from unittest import TestCase, skip

import mock
from lxml import etree as ET

from iatilib.test import db, AppTestCase, fixture_filename
from iatilib import parse, codelists as cl
# Remove all lines containind nottest to enable all the 2.01 tests that we currently expect to fail
from nose.tools import nottest


def fixture(fix_name, encoding='utf-8'):
    return codecs.open(fixture_filename(fix_name), encoding=encoding).read()


class TestParse201Activity(AppTestCase):
    # TODO: Ensure that sectors and transactions are fully tested, maybe borrow some tests from TestSector and TestTransaction below
    # TODO: Check through the sample XML for any 2.01 changes that aren't yet being tested here

    def setUp(self):
        super(TestParse201Activity, self).setUp()
        self.activities = list(parse.document(fixture_filename("2.01-example-annotated.xml")))
        self.act = self.activities[0]

    def test_id(self):
        self.assertEquals(
            u"AA-AAA-123456789-ABC123",
            self.act.iati_identifier)
    
    def test_title(self):
        self.assertEquals(
            u"Activity title",
            self.act.title)

    def test_last_updated_time(self):
        self.assertEquals(datetime.date(2014, 9, 10), self.act.last_updated_datetime)

    def test_description(self):
        self.assert_(self.act.description.startswith(
            u"General activity description text."))
    
    def test_reporting_org_ref(self):
        self.assertEquals(u"AA-AAA-123456789", self.act.reporting_org.ref)

    def test_reporting_org_type(self):
        self.assertEquals(
            cl.OrganisationType.multilateral,
            self.act.reporting_org.type
        )

    # TODO reporting ORG text

    # activity-website not in 2.01
    #def test_activity_websites(self):
    #    self.assertEquals(
    #        [u"http://portfolio.theglobalfund.org/en/Grant/Index/ARM-202-G05-H-00"],
    #        self.act.websites)

    def test_default_currency(self):
        self.assertEquals(
            cl.Currency.us_dollar,
            self.act.default_currency
        )

    @nottest
    def test_participating_org(self):
        self.assertEquals(
            cl.OrganisationRole.funding,
            self.act.participating_orgs[0].role)
        self.assertEquals(
            cl.OrganisationRole.accountable,
            self.act.participating_orgs[1].role)
        self.assertEquals(
            cl.OrganisationRole.extending,
            self.act.participating_orgs[2].role)

    # TODO Maybe add 2.01 test file for this
    #def test_accepts_participatng_org_without_ref(self):
    #    self.assertEquals(2, len(self.act.participating_orgs))

    def test_recipient_country_percentages(self):
        act = self.act
        self.assertEquals(2, len(self.act.recipient_country_percentages))
        self.assertEquals(
            cl.Country.afghanistan,
            act.recipient_country_percentages[0].country)
        self.assertEquals(
            cl.Country.antigua_and_barbuda,
            act.recipient_country_percentages[1].country)
        self.assertEquals(
            25,
            act.recipient_country_percentages[0].percentage)
        self.assertEquals(
            25,
            act.recipient_country_percentages[1].percentage)

    def test_recipient_region_percentages(self):
        act = self.act
        self.assertEquals(2, len(act.recipient_region_percentages))
        self.assertEquals(
            cl.Region.south_america_regional,
            act.recipient_region_percentages[0].region)
        self.assertEquals(
            cl.Region.south_of_sahara_regional,
            act.recipient_region_percentages[1].region)
        self.assertEquals(
            25,
            act.recipient_region_percentages[0].percentage)
        self.assertEquals(
            25,
            act.recipient_region_percentages[1].percentage)


        # TODO this is looking for the text in the element.
        # Need to test this for RO for 2.01
        #self.assertEquals(
        #"South America, regional", act.recipient_region_percentages[0].name)
        #self.assertEquals(
        #    "South of Sahara, regional", act.recipient_region_percentages[1].name)

    def test_transaction_count(self):
        self.assertEquals(1, len(self.act.transactions))

    @nottest
    def test_transaction_type(self):
        self.assertEquals(
            cl.TransactionType.incoming_funds,
            self.act.transactions[0].type)

    def test_transaction_date(self):
        self.assertEquals(
            datetime.date(2012, 1, 1),
            self.act.transactions[0].date)

    def test_transaction_value_date(self):
        self.assertEquals(
            datetime.date(2012, 1, 1),
            self.act.transactions[0].value_date)

    def test_transaction_value_amount(self):
        self.assertEquals(
            1000,
            self.act.transactions[0].value_amount)

    def test_transaction_currency(self):
        self.assertEquals(
            cl.Currency.euro,
            self.act.transactions[0].value_currency)

    def test_transaction_value_composite(self):
        self.assertEquals(
            (datetime.date(2012, 1, 1), 1000, cl.Currency.euro),
            self.act.transactions[0].value)

    def test_transaction_ref(self):
        self.assertEquals(u'1234', self.act.transactions[0].ref)

    def test_transaction_provider_org_ref(self):
        self.assertEquals(u'BB-BBB-123456789', 
                            self.act.transactions[0].provider_org.ref)

    def test_transaction_reciever_org_ref(self):
        self.assertEquals(u'AA-AAA-123456789', 
                            self.act.transactions[0].receiver_org.ref)

    def test_date_start_planned(self):
        self.assertEquals(datetime.date(2012, 4, 15), self.act.start_planned)

    def test_date_start_actual(self):
        self.assertEquals(datetime.date(2012, 4, 28), self.act.start_actual)

    def test_date_end_planned(self):
        self.assertEquals(datetime.date(2015, 12, 31), self.act.end_planned)

    def test_date_end_actual(self):
        self.assertEquals(None, self.act.end_actual)

    # TODO Deal properly with sector and recipient-country/region at activity/country level
    #def test_sector_percentage_count(self):
    #    act = next(parse.document(
    #        fixture("complex_example_dfid.xml", encoding=None)))
    #    self.assertEquals(5, len(act.sector_percentages))
    
    def test_raw_xml(self):
        norm_xml = ET.tostring(ET.parse(fixture_filename("2.01-example-annotated.xml")).find('iati-activity'), encoding=unicode).strip(u'\n ')
        self.assertEquals(norm_xml, self.act.raw_xml)


    def test_budget(self):
        self.assertEquals(1, len(self.act.budgets))

    def test_policy_markers(self):
        self.assertEquals(2, len(self.act.policy_markers))
        self.assertEquals(cl.PolicyMarker.aid_to_environment, self.act.policy_markers[0].code)
        self.assertEquals(cl.PolicyMarker.gender_equality, self.act.policy_markers[1].code)

    def test_related_activity(self):
        self.assertEquals(1, len(self.act.related_activities))
        self.assertEquals("AA-AAA-123456789-6789", self.act.related_activities[0].ref)

    def test_activity_status(self):
        self.assertEquals(cl.ActivityStatus.implementation, self.act.activity_status)

    def test_collaboration_type(self):
        self.assertEquals(cl.CollaborationType.bilateral, self.act.collaboration_type)
       
    def test_default_finance_type(self):
        self.assertEquals(cl.FinanceType.aid_grant_excluding_debt_reorganisation,
                self.act.default_finance_type)

    def test_default_flow_type(self):
        self.assertEquals(cl.FlowType.oda, self.act.default_flow_type)

    def test_default_aid_type(self):
        self.assertEquals(cl.AidType.general_budget_support,
                self.act.default_aid_type)

    def test_default_tied_status(self):
        self.assertEquals(cl.TiedStatus.partially_tied, self.act.default_tied_status) 

    def test_default_hierarchy(self):
        self.assertEquals(cl.RelatedActivityType.parent, self.act.hierarchy) 

    def test_default_language(self):
        self.assertEquals(cl.Language.english, self.act.default_language) 


class TestParseActivity(AppTestCase):
    def setUp(self):
        super(TestParseActivity, self).setUp()
        self.act = parse.activity(fixture("default_currency.xml"))

    def test_bad_xml(self):
        with self.assertRaises(ET.LxmlError):
            act = parse.activity(fixture("broken.xml"))


    def test_id(self):
        self.assertEquals(
            u"47045-ARM-202-G05-H-00",
            self.act.iati_identifier)

    def test_title(self):
        self.assertEquals(
            (u"Support to the National Program on the Response to HIV " +
             u"Epicemic in the Republic of Armenia"),
            self.act.title)

    def test_last_updated_time(self):
        self.assertEquals(datetime.date(2012, 9, 25), self.act.last_updated_datetime)

    def test_description(self):
        self.assert_(self.act.description.startswith(
            u"While Armenia is still a country with a concentrated HIV"))

    def test_reporting_org_ref(self):
        self.assertEquals(u"47045", self.act.reporting_org.ref)

    def test_reporting_org_type(self):
        self.assertEquals(
            cl.OrganisationType.multilateral,
            self.act.reporting_org.type
        )

    def test_activity_websites(self):
        self.assertEquals(
            [u"http://portfolio.theglobalfund.org/en/Grant/Index/ARM-202-G05-H-00"],
            self.act.websites)

    def test_default_currency(self):
        self.assertEquals(
            cl.Currency.us_dollar,
            self.act.default_currency
        )

    def test_participating_org(self):
        self.assertEquals(
            cl.OrganisationRole.funding,
            self.act.participating_orgs[0].role)

    def test_accepts_participatng_org_without_ref(self):
        self.assertEquals(2, len(self.act.participating_orgs))

    def test_recipient_country_percentages(self):
        self.assertEquals(1, len(self.act.recipient_country_percentages))
        self.assertEquals(
            cl.Country.armenia,
            self.act.recipient_country_percentages[0].country)
        self.assertEquals(
            "Armenia", self.act.recipient_country_percentages[0].name)
        self.assertEquals(
            None,
            self.act.recipient_country_percentages[0].percentage)

    def test_recipient_region_percentages(self):
        act = parse.activity(fixture("iati_activity_JP.xml"))
        self.assertEquals(1, len(act.recipient_region_percentages))
        self.assertEquals(
            cl.Country.japan,
            act.recipient_country_percentages[0].country)
        self.assertEquals(
            "Far East Asia, regional", act.recipient_region_percentages[0].name)
        self.assertEquals(
            100,
            act.recipient_region_percentages[0].percentage)

    def test_transaction_count(self):
        self.assertEquals(1, len(self.act.transactions))

    def test_transaction_type(self):
        self.assertEquals(
            cl.TransactionType.commitment,
            self.act.transactions[0].type)

    def test_transaction_date(self):
        self.assertEquals(
            datetime.date(2009, 10, 01),
            self.act.transactions[0].date)

    def test_transaction_value_date(self):
        self.assertEquals(
            datetime.date(2009, 10, 01),
            self.act.transactions[0].value_date)

    def test_transaction_value_amount(self):
        self.assertEquals(
            3991675,
            self.act.transactions[0].value_amount)

    def test_transaction_currency(self):
        # currency is picked up from default currency
        act = parse.activity(fixture("transaction_provider.xml"))
        self.assertEquals(
            cl.Currency.pound_sterling,
            act.transactions[0].value_currency)

    def test_transaction_value_composite(self):
        act = parse.activity(fixture("transaction_provider.xml"))
        self.assertEquals(
            (datetime.date(2011, 8, 19), 29143, cl.Currency.pound_sterling),
            act.transactions[0].value)

    def test_transaction_ref(self):
        act = parse.activity(fixture("transaction_ref.xml"))
        self.assertEquals(u'36258', act.transactions[0].ref)
        self.assertEquals(None, act.transactions[1].ref)

    def test_transaction_provider_org_ref(self):
        act = parse.activity(fixture("transaction_provider.xml"))
        self.assertEquals(u'GB-1-201242-101', 
                            act.transactions[0].provider_org.ref)

    def test_transaction_reciever_org_ref(self):
        act = parse.activity(fixture("transaction_provider.xml"))
        self.assertEquals(u'GB-CHC-313139', 
                            act.transactions[0].receiver_org.ref)

    def test_date_start_planned(self):
        self.assertEquals(datetime.date(2009, 10, 03), self.act.start_planned)

    def test_date_start_actual(self):
        self.assertEquals(datetime.date(2009, 10, 01), self.act.start_actual)

    def test_date_end_planned(self):
        self.assertEquals(datetime.date(2009, 10, 04), self.act.end_planned)

    def test_date_end_actual(self):
        self.assertEquals(datetime.date(2009, 10, 02), self.act.end_actual)


    def test_sector_percentage_count(self):
        act = next(parse.document(
            fixture("complex_example_dfid.xml", encoding=None)))
        self.assertEquals(5, len(act.sector_percentages))

    def test_raw_xml(self):
        norm_xml = ET.tostring(ET.parse(fixture_filename("default_currency.xml")))
        self.assertEquals(norm_xml, self.act.raw_xml)

    def test_no_start_actual(self):
        activities = parse.document(fixture_filename("missing_dates.xml"))
        act = {a.iati_identifier:a for a in activities}
        self.assertEquals(None, act[u"GB-CHC-272465-680"].start_actual)

    def test_budget(self):
        self.assertEquals(6, len(self.act.budgets))

    def test_policy_markers(self):
        activities = [ a for a in parse.document(fixture_filename("CD.xml")) ]

        self.assertEquals(8, len(activities[1].policy_markers))
        self.assertEquals(cl.PolicyMarker.gender_equality, activities[1].policy_markers[0].code)
        self.assertEquals(cl.PolicyMarker.aid_to_environment, activities[1].policy_markers[1].code)
        self.assertEquals(cl.PolicyMarker.participatory_developmentgood_governance,
                activities[1].policy_markers[2].code)
        self.assertEquals(cl.PolicyMarker.trade_development, activities[1].policy_markers[3].code)

    def test_related_activity(self):
        activities = [ a for a in parse.document(fixture_filename("CD.xml")) ]
        self.assertEquals(4, len(activities[0].related_activities))
        self.assertEquals("GB-1-105838-101", activities[0].related_activities[0].ref)

    def test_activity_status(self):
        activities = [ a for a in parse.document(fixture_filename("default_currency.xml")) ]
        self.assertEquals(cl.ActivityStatus.implementation, activities[0].activity_status)

    def test_collaboration_type(self):
        activities = [ a for a in parse.document(fixture_filename("CD.xml")) ]
        self.assertEquals(cl.CollaborationType.bilateral, activities[1].collaboration_type)
        
    def test_default_finance_type(self):
        activities = [ a for a in parse.document(fixture_filename("CD.xml")) ]
        self.assertEquals(cl.FinanceType.aid_grant_excluding_debt_reorganisation,
                activities[1].default_finance_type)

    def test_default_flow_type(self):
        activities = [ a for a in parse.document(fixture_filename("CD.xml")) ]
        self.assertEquals(cl.FlowType.oda, activities[1].default_flow_type)

    def test_default_aid_type(self):
        activities = [ a for a in parse.document(fixture_filename("CD.xml")) ]
        self.assertEquals(cl.AidType.projecttype_interventions,
                activities[1].default_aid_type)

    def test_default_tied_status(self):
        activities = [ a for a in parse.document(fixture_filename("CD.xml")) ]
        self.assertEquals(cl.TiedStatus.untied, activities[1].default_tied_status) 

    def test_default_hierarchy(self):
        activities = [ a for a in parse.document(fixture_filename("default_currency.xml")) ]
        self.assertEquals(cl.RelatedActivityType.parent, activities[0].hierarchy) 

    def test_default_language(self):
        activities = [ a for a in parse.document(fixture_filename("default_currency.xml")) ]
        self.assertEquals(cl.Language.english, activities[0].default_language) 

    def test_default_language_none(self):
        default_language = parse.default_language(
            ET.XML('<iati-activity xml:lang="en" default-currency="GBP" hierarchy="1"/>'))
        self.assertEquals(cl.Language.english, default_language) 
        no_default_language = parse.default_language(
            ET.XML('<iati-activity default-currency="GBP" hierarchy="1"/>'))
        self.assertEquals(None, no_default_language) 



class TestFunctional(AppTestCase):
    def test_save_parsed_activity(self):
        act = parse.activity(fixture("default_currency.xml"))
        db.session.add(act)
        db.session.commit()

    def test_save_parsed_201(self):
        activities = parse.document(fixture_filename("2.01-example-annotated.xml"))
        db.session.add_all(activities)
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
        sec = parse.sector_percentages(ET.XML(
            u'<wrapper><sector vocabulary="DAC" code="16010">Child Protection Systems Strengthening</sector></wrapper>'
        ))[0]
        self.assertEquals(cl.Sector.social_welfare_services, sec.sector)
        self.assertEquals(u"Child Protection Systems Strengthening", sec.text)

    def test_missing_code(self):
        sec = parse.sector_percentages(ET.XML(
            u'<wrapper><sector vocabulary="DAC">Child Protection Systems Strengthening</sector></wrapper>'
        ))[0]
        self.assertEquals(None, sec.sector)

    def test_missing_everything(self):
        sec = parse.sector_percentages(ET.XML(
            u'<wrapper><sector /></wrapper>'
        ))
        self.assertEquals([], sec)

class TestPercentages(AppTestCase):
    def test_recipient_country_percentages(self):
        recipient_country_percentages = parse.recipient_country_percentages(ET.XML(
            u'<wrapper><recipient-country code="BD" percentage="3"></recipient-country></wrapper>'
        ))
        self.assertEquals(3, recipient_country_percentages[0].percentage)

    def test_recipient_region_percentages(self):
        recipient_region_percentages = parse.recipient_region_percentages(ET.XML(
            u"""<wrapper>
                    <recipient-region code="998" percentage="4"></recipient-region>
                    <recipient-region code="998"></recipient-region>
                </wrapper>"""
        ))
        self.assertEquals(4, recipient_region_percentages[0].percentage)
        self.assertEquals(None, recipient_region_percentages[1].percentage)

class TestOrganisation(AppTestCase):
    def test_org_role_looseness(self):
        # organisationrole should be "Implementing" but can be "implementing"
        orgrole = parse.participating_orgs(ET.XML(
            u'<wrap><participating-org role="implementing" ref="test" /></wrap>'
        ))[0]
        self.assertEquals(orgrole.role, cl.OrganisationRole.implementing)

    def test_org_type(self):
        orgtype = parse.reporting_org(ET.XML(
            u"""<wrap><reporting-org ref="GB-CHC-202918" type="21" /></wrap>"""
        ))
        self.assertEquals(cl.OrganisationType.international_ngo, orgtype.type)

    def test_org_type_missing(self):
        orgtype = parse.reporting_org(ET.XML(
            u"""<wrap><reporting-org ref="GB-CHC-202918" /></wrap>"""
        ))
        self.assertEquals(None, orgtype.type)



class TestParticipation(AppTestCase):
    def test_repeated_participation(self):
        # Identical participations should be filtered
        participations = parse.participating_orgs(
            ET.XML(u"""
                <wrap> 
                <participating-org ref="GB-CHC-272465" role="implementing" type="21">Concern Universal</participating-org>
            <participating-org ref="GB-CHC-272465" role="implementing" type="21">Concern Universal</participating-org>
                </wrap> 
                """),
        )
        self.assertEquals(1, len(participations))

    def test_same_org_different_role(self):
        participations = parse.participating_orgs(
            ET.XML(u"""<wrap>
            <participating-org ref="GB-CHC-272465" role="implementing" type="21">Concern Universal</participating-org>
            <participating-org ref="GB-CHC-272465" role="Funding" type="21">Concern Universal</participating-org>
            </wrap>
            """)
        )
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

    def test_dates(self):
        activities = list(parse.document(fixture_filename("CD.xml")))
        self.assertEquals(datetime.date(2004, 1, 1), activities[0].start_planned)
        self.assertEquals(datetime.date(2004, 1, 1), activities[0].start_actual)
        self.assertEquals(datetime.date(2010, 12, 31), activities[0].end_planned)
        self.assertEquals(datetime.date(2010, 12, 31), activities[0].end_actual)


class TestTransaction(AppTestCase):
    def __init__(self, methodName='runTest'):
        super(TestTransaction, self).__init__(methodName)
        self.codelists = """
            <activity><transaction>
              <transaction-type code="C"/>
              <value value-date="2012-12-31">4119000</value>
              <transaction-date iso-date="2012-12-31"/>
              <flow-type code="30"/>
              <finance-type code="110"/>
              <aid-type code="B01"/>
              <disbursement-channel code="2"/>
              <tied-status code="5"/>
            </transaction></activity>
        """

    def test_missing_code(self):
        transactions = parse.transactions(
            ET.XML(u'''<activity><transaction>
                <transaction-date iso-date="31/12/2011" />
                <description>test</description>
                <value value-date="31/12/2011">116,017</value>
                <transaction-type>Disbursement</transaction-type>
                </transaction></activity>''')
        )
        self.assertEquals(1, len(transactions))

    def test_big_value(self):
        transaction = parse.transactions(
            ET.XML(u'''<activity><transaction>
                <transaction-date iso-date="31/12/2011" />
                <description>test</description>
                <value value-date="31/12/2011">2663000000</value>
                <transaction-type code="D">Disbursement</transaction-type>
                </transaction></activity>''')
        )[0]
        self.assertEquals(2663000000, transaction.value_amount)

    @mock.patch('iatilib.parse.iati_decimal')
    def test_iati_int_called(self, mock):
        transaction = parse.transactions(
            ET.XML(u'''<activity><transaction>
                <transaction-date iso-date="31/12/2011" />
                <description>test</description>
                <value value-date="31/12/2011">-1000</value>
                <transaction-type code="D">Disbursement</transaction-type>
                </transaction></activity>''')
        )[0]
        self.assertEquals(1, mock.call_count)

    def test_provider_activity_id(self):
        sample = """<activity><transaction>
          <transaction-type code="IF"/>
          <provider-org ref="GB-1" provider-activity-id="GB-1-202907">
            DFID
          </provider-org>
          <value value-date="2012-07-02" currency="GBP">51693</value>
          <transaction-date iso-date="2012-07-02"/>
        </transaction></activity>
        """
        transaction = parse.transactions(ET.XML(sample))[0]
        self.assertEquals(u'GB-1-202907', transaction.provider_org_activity_id)

    def test_provider_org_text(self):
        sample = """<activity><transaction>
          <transaction-type code="IF"/>
          <provider-org>DFID</provider-org>
          <value value-date="2012-07-02" currency="GBP">51693</value>
          <transaction-date iso-date="2012-07-02"/>
        </transaction></activity>
        """
        transaction = parse.transactions(ET.XML(sample))[0]
        self.assertEquals(u'DFID', transaction.provider_org_text)

    def test_receiver_activity_id(self):
        sample = """<activity><transaction>
          <transaction-type code="IF"/>
          <receiver-org ref="GB-CHC-1068839" receiver-activity-id="GB-CHC-1068839-dfid_ag_11-13">Bond</receiver-org>
          <value value-date="2011-06-01" currency="GBP">271111</value>
          <transaction-date iso-date="2012-03-31"/>
          </transaction></activity>
        """
        transaction = parse.transactions(ET.XML(sample))[0]
        self.assertEquals(u'GB-CHC-1068839-dfid_ag_11-13', transaction.receiver_org_activity_id)

    def test_receiver_org_text(self):
        sample = """<activity><transaction>
          <transaction-type code="IF"/>
          <receiver-org ref="GB-CHC-1068839" receiver-activity-id="GB-CHC-1068839-dfid_ag_11-13">Bond</receiver-org>
          <value value-date="2012-07-02" currency="GBP">51693</value>
          <transaction-date iso-date="2012-07-02"/>
        </transaction></activity>
        """
        transaction = parse.transactions(ET.XML(sample))[0]
        self.assertEquals(u'Bond', transaction.receiver_org_text)

    def test_description(self):
        sample = """<activity><transaction>
          <transaction-type code="IF"/>
          <value value-date="2011-08-19" currency="GBP">29143</value>
          <description>Funds received from DFID for activities in Aug- Sept 2011</description>
          <transaction-date iso-date="2011-08-19"/>
        </transaction></activity>"""
        transaction = parse.transactions(ET.XML(sample))[0]
        self.assertEquals(
                u'Funds received from DFID for activities in Aug- Sept 2011',
                transaction.description
        )

    def test_flow_type(self):
        transaction = parse.transactions(ET.XML(self.codelists))[0]
        self.assertEquals(u'30', transaction.flow_type.value) 

    def test_finance_type(self):
        transaction = parse.transactions(ET.XML(self.codelists))[0]
        self.assertEquals(u'110', transaction.finance_type.value) 

    def test_aid_type(self):
        transaction = parse.transactions(ET.XML(self.codelists))[0]
        self.assertEquals(u'B01', transaction.aid_type.value) 

    def test_tied_status(self):
        transaction = parse.transactions(ET.XML(self.codelists))[0]
        self.assertEquals(u'5', transaction.tied_status.value) 

    def test_disbursement_channel(self):
        transaction = parse.transactions(ET.XML(self.codelists))[0]
        self.assertEquals(u'2', transaction.disbursement_channel.value) 

class TestBudget(TestCase):
    def parse_budget(self):
        return parse.budgets(ET.XML("""
            <wrapper>
            <budget type="1">
                <period-end iso-date="2010-03-31" />
                <value currency="USD">1840852</value>
            </budget>
            </wrapper>
        """))[0]

    def test_budget_type(self):
        budget = self.parse_budget()
        self.assertEquals(budget.type, cl.BudgetType.original)

    def test_budget_type_looser(self):
        budget = parse.budgets(ET.XML("""
            <wrapper>
            <budget type="Original">
                <period-end iso-date="2010-03-31" />
                <value currency="USD">1840852</value>
            </budget>
            </wrapper>
        """))[0]
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

    def test_iso_date_with_z(self):
        self.assertEquals(
            datetime.date(2010, 1, 2),
            parse.iati_date("2010-01-02Z"))


class TestValue(TestCase):
    def test_thousand_sep(self):
        self.assertEquals(20026, parse.iati_int(u"20,026"))

    def test_sign(self):
        self.assertEquals(-20026, parse.iati_int(u"-20026"))

    def test_decimal_thousand_sep(self):
        self.assertEquals(Decimal('20026'), parse.iati_decimal(u"20,026"))

    def test_decimal_sign(self):
        self.assertEquals(Decimal('-20026'), parse.iati_decimal(u"-20026"))

    def test_decimal(self):
        self.assertEquals(Decimal('42479.4'), parse.iati_decimal(u"42479.4"))

class TestXVal(TestCase):
    def test_missing_val(self):
        with self.assertRaises(parse.MissingValue):
            parse.xval(ET.XML(u"<foo />"), "bar")

    def test_default_val(self):
        self.assertEquals(
            None,
            parse.xval(ET.XML(u"<foo />"), "bar", None))

