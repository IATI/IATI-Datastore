from iatilib.model import *
import unittest
import tempfile
import iatilib.parser
import iso8601
from datetime import datetime
from iatilib import db

from . import AppTestCase

# Hand-generated XML used to test the parser
_fixture_xml = u"""
<iati-activity
  version="999001.01"
  hierarchy="999002.02"
  default-currency="fixture_default_currency"
  xml:lang="fixture_lang"
  linked-data-uri="fixture_linked_data_uri"
  last-updated-datetime="2012-01-14 15:16:17">
    <iati-identifier>
        fixture_iati_identifier__text
    </iati-identifier>
    <activity-website>
        fixture_activity_website__text
    </activity-website>
    <reporting-org ref="fixture_reporting_org__ref" type="fixture_reporting_org__type" xml:lang="fixture_reporting_org__lang">
        fixture_reporting_org__text
    </reporting-org>
    <recipient-country code="fixture_recipient_country__code" percentage="999003.03" xml:lang="fixture_recipient_country__lang">
        fixture_recipient_country__text
    </recipient-country>
    <recipient-region code="fixture_recipient_region__code" percentage="999004.04" xml:lang="fixture_recipient_region__lang">
        fixture_recipient_region__text
    </recipient-region>
    <title xml:lang="fixture_title__lang">
        fixture_title__text
    </title>
    <description type="fixture_description__type" xml:lang="fixture_description__lang">
        fixture_description__text
    </description>
    <activity-status code="fixture_activity_status__code" xml:lang="fixture_activity_status__lang">
        fixture_activity_status__text
    </activity-status>
    <collaboration-type code="fixture_collaboration_type__code" xml:lang="fixture_collaboration_type__lang">
        fixture_collaboration_type__text
    </collaboration-type>
    <default-flow-type code="fixture_default_flow_type__code" xml:lang="fixture_default_flow_type__lang">
        fixture_default_flow_type__text
    </default-flow-type>
    <default-aid-type code="fixture_default_aid_type__code" xml:lang="fixture_default_aid_type__lang">
        fixture_default_aid_type__text
    </default-aid-type>
    <default-finance-type code="fixture_default_finance_type__code" xml:lang="fixture_default_finance_type__lang">
        fixture_default_finance_type__text
    </default-finance-type>
    <default-tied-status code="fixture_default_tied_status__code" xml:lang="fixture_default_tied_status__lang">
        fixture_default_tied_status__text
    </default-tied-status>
    <policy-marker code="fixture_policy_marker__code" significance="fixture_policy_marker__significance" vocabulary="fixture_policy_marker__vocabulary" xml:lang="fixture_policy_marker__lang">
        fixture_policy_marker__text
    </policy-marker>
    <location percentage="999005.05">
        <location-type code="fixture_location__location_type__code" xml:lang="fixture_location__location_type__lang">fixture_location__location_type__text</location-type>
        <name xml:lang="fixture_location__name__lang">fixture_location__name__text</name>
        <description xml:lang="fixture_location__description__lang">fixture_location__description__text</description>
        <administrative country="fixture_location__administrative__country" adm1="fixture_location__administrative__adm1" adm2="fixture_location__administrative__adm2">fixture_location__administrative__text</administrative>
        <coordinates latitude="999006.06" longitude="999007.07" precision="fixture_location__coordinates__precision" />
        <gazetteer-entry gazetteer-ref="fixture_location__gazetteer_entry__gazetteer_ref">fixture_location__gazetteer_entry__text</gazetteer-entry>
    </location>
    <other-identifier owner-ref="fixture_other_identifier__owner_ref" owner-name="fixture_other_identifier__owner_name">
        fixture_other_identifier__text
    </other-identifier>
    <result type="fixture_result__type" aggregation-status="true">
        <title xml:lang="fixture_result__title__lang">
            fixture_result__title__text
        </title>
        <description type="fixture_result__description__type" xml:lang="fixture_result__description__lang">
            fixture_result__description__text
        </description>
        <indicator measure="fixture_result__indicator__measure" ascending="true">
            <title xml:lang="fixture_result__indicator__title__lang">
                fixture_result__indicator__title__text
            </title>
            <description type="fixture_result__indicator__description__type" xml:lang="fixture_result__indicator__description__lang">
                fixture_result__indicator__description__text
            </description>
            <baseline year="1999" value="fixture_result__indicator__baseline__value">
                <comment xml:lang="fixture_result__indicator__baseline__comment__lang">
                    fixture_result__indicator__baseline__comment__text
                </comment>
            </baseline>
            <period>
                <period-start iso-date="2001-02-03 04:05:06">
                    fixture_result__indicator__period__period_start__text
                </period-start>
                <period-end iso-date="2002-03-04 05:06:07">
                    fixture_result__indicator__period__period_end__text
                </period-end>
                <target value="fixture_result__indicator__period__target__value">
                    <comment xml:lang="fixture_result__indicator__period__target__comment__lang">
                        fixture_result__indicator__period__target__comment__text
                    </comment>
                </target>
                <actual value="fixture_result__indicator__period__actual__value">
                    <comment xml:lang="fixture_result__indicator__period__actual__comment__lang">
                        fixture_result__indicator__period__actual__comment__text
                    </comment>
                </actual>
            </period>
        </indicator>
    </result>
    <conditions attached="true">
        <condition type="fixture_conditions__condition__type">
            fixture_conditions__condition__text
        </condition>
    </conditions>
    <budget type="fixture_budget__type">
        <period-start iso-date="2003-04-05 06:07:08">
            fixture_budget__period_start__text
        </period-start>
        <period-end iso-date="2004-05-06 07:08:09">
            fixture_budget__period_end__text
        </period-end>
        <value currency="fixture_budget__value__currency" value-date="2005-06-07 08:09:10">
            999009.09
        </value>
    </budget>
    <planned-disbursement updated="fixture_planned_disbursement__updated">
        <period-start iso-date="2006-07-08 09:10:11">
            fixture_planned_disbursement__period_start__text
        </period-start>
        <period-end iso-date="2007-08-09 10:11:12">
            fixture_planned_disbursement__period_end__text
        </period-end>
        <value currency="fixture_planned_disbursement__value__currency" value-date="2008-09-10 11:12:13">
            999010.10
        </value>
    </planned-disbursement>
    <related-activity ref="fixture_related_activity__ref" type="fixture_related_activity__type" xml:lang="fixture_related_activity__lang">
        fixture_related_activity__text
    </related-activity>
    <document-link url="fixture_document_link__url" format="fixture_document_link__format">
        <title xml:lang="fixture_document_link__title__lang">
            fixture_document_link__title__text
        </title>
        <category code="fixture_document_link__category__code" xml:lang="fixture_document_link__category__lang">
            fixture_document_link__category__text
        </category>
        <language code="fixture_document_link__language__code" xml:lang="fixture_document_link__language__lang">
            fixture_document_link__language__text
        </language>
    </document-link>
    <legacy-data name="fixture_legacy_data__name" value="fixture_legacy_data__value" iati-equivalent="fixture_legacy_data__iati_equivalent">
        fixture_legacy_data__text
    </legacy-data>
    <transaction ref="fixture_ref">
        <value currency="fixture_value__currency" value-date="2009-10-11 12:13:14">
            999011.11
        </value>
        <description xml:lang="fixture_description__lang">
            fixture_description__text
        </description>
        <transaction-type code="fixture_transaction_type__code" xml:lang="fixture_transaction_type__lang">
            fixture_transaction_type__text
        </transaction-type>
        <provider-org ref="fixture_provider_org__ref" provider-activity-id="fixture_provider_org__provider_activity_id">
            fixture_provider_org__text
        </provider-org>
        <receiver-org ref="fixture_receiver_org__ref" receiver-activity-id="fixture_receiver_org__receiver_activity_id">
            fixture_receiver_org__text
        </receiver-org>
        <transaction-date iso-date="2010-11-12 13:14:15">
            fixture_transaction_date__text
        </transaction-date>
        <flow-type code="fixture_flow_type__code" xml:lang="fixture_flow_type__lang">
            fixture_flow_type__text
        </flow-type>
        <aid-type code="fixture_aid_type__code" xml:lang="fixture_aid_type__lang">
            fixture_aid_type__text
        </aid-type>
        <finance-type code="fixture_finance_type__code" xml:lang="fixture_finance_type__lang">
            fixture_finance_type__text
        </finance-type>
        <tied-status code="fixture_tied_status__code" xml:lang="fixture_tied_status__lang">
            fixture_tied_status__text
        </tied-status>
        <disbursement-channel code="fixture_disbursement_channel__code" xml:lang="fixture_disbursement_channel__lang">
            fixture_disbursement_channel__text
        </disbursement-channel>
    </transaction>
    <sector code="999013" vocabulary="fixture_vocabulary" percentage="999012.12" xml:lang="fixture_lang">
      fixture_text
    </sector>
    <participating-org ref="fixture_ref" type="fixture_type" role="fixture_role" xml:lang="fixture_lang">
      fixture_text
    </participating-org>
    <contact-info>
        <organisation>fixture_organisation__text</organisation>
        <person-name>fixture_person_name__text</person-name>
        <telephone>fixture_telephone__text</telephone>
        <email>fixture_email__text</email>
        <mailing-address>fixture_mailing_address__text</mailing-address>
    </contact-info>
    <activity-date type="fixture_type" iso-date="2011-12-13 14:15:16" xml:lang="fixture_lang">
        fixture_text
    </activity-date>
</iati-activity>
"""

class CaseParser(AppTestCase):
    def setUp(self):
        super(CaseParser, self).setUp()
        assert len( list(db.session.query(CodelistSector)) )==0
        db.session.add( CodelistSector(code=999013) )
        assert len( list(db.session.query(IndexedResource)) )==0
        db.session.add( IndexedResource(id=u'999999') )
        db.session.commit()
    def tearDown(self):
        db.session.query(CodelistSector).delete()
        db.session.query(IndexedResource).delete()
        db.session.commit()
        assert len( list(db.session.query(IndexedResource)) )==0
        assert len( list(db.session.query(CodelistSector)) )==0

    def test_fixture_xml(self):
        activity, errors = iatilib.parser.parse(_fixture_xml)
        assert len(errors)==0
        ## Assertions: Activity object
        assert activity.version == 999001.01
        assert activity.last_updated_datetime == datetime(year=2012,month=1,day=14,hour=15,minute=16,second=17,tzinfo=iso8601.iso8601.UTC), obj_dict['activity'].last_updated_datetime
        assert activity.lang == 'fixture_lang'
        assert activity.default_currency == 'fixture_default_currency'
        assert activity.hierarchy == 999002.02
        assert activity.linked_data_uri == 'fixture_linked_data_uri'
        assert len(activity.website)==1
        assert activity.website[0].text == 'fixture_activity_website__text'
        assert len(activity.reportingorg)==1
        assert activity.reportingorg[0].text == 'fixture_reporting_org__text'
        assert activity.reportingorg[0].ref == 'fixture_reporting_org__ref'
        assert activity.reportingorg[0].type == 'fixture_reporting_org__type'
        assert activity.reportingorg[0].lang == 'fixture_reporting_org__lang'
        assert len(activity.recipientcountry)==1
        assert activity.recipientcountry[0].text == 'fixture_recipient_country__text'
        assert activity.recipientcountry[0].code == 'fixture_recipient_country__code'
        assert activity.recipientcountry[0].percentage == 999003.03
        assert activity.recipientcountry[0].lang == 'fixture_recipient_country__lang'
        assert len(activity.recipientregion)==1
        assert activity.recipientregion[0].text == 'fixture_recipient_region__text'
        assert activity.recipientregion[0].code == 'fixture_recipient_region__code'
        assert activity.recipientregion[0].percentage == 999004.04
        assert activity.recipientregion[0].lang == 'fixture_recipient_region__lang'
        assert len(activity.collaborationtype)==1
        assert activity.collaborationtype[0].text == 'fixture_collaboration_type__text'
        assert activity.collaborationtype[0].code == 'fixture_collaboration_type__code'
        assert activity.collaborationtype[0].lang == 'fixture_collaboration_type__lang'
        assert len(activity.defaultflowtype)==1
        assert activity.defaultflowtype[0].text == 'fixture_default_flow_type__text'
        assert activity.defaultflowtype[0].code == 'fixture_default_flow_type__code'
        assert activity.defaultflowtype[0].lang == 'fixture_default_flow_type__lang'
        assert len(activity.defaultaidtype)==1
        assert activity.defaultaidtype[0].text == 'fixture_default_aid_type__text'
        assert activity.defaultaidtype[0].code == 'fixture_default_aid_type__code'
        assert activity.defaultaidtype[0].lang == 'fixture_default_aid_type__lang'
        assert len(activity.defaultfinancetype)==1
        assert activity.defaultfinancetype[0].text == 'fixture_default_finance_type__text'
        assert activity.defaultfinancetype[0].code == 'fixture_default_finance_type__code'
        assert activity.defaultfinancetype[0].lang == 'fixture_default_finance_type__lang'
        assert len(activity.iatiidentifier)==1
        assert activity.iatiidentifier[0].text == 'fixture_iati_identifier__text'
        assert len(activity.otheridentifier)==1
        assert activity.otheridentifier[0].text == 'fixture_other_identifier__text'
        assert activity.otheridentifier[0].owner_ref == 'fixture_other_identifier__owner_ref'
        assert activity.otheridentifier[0].owner_name == 'fixture_other_identifier__owner_name'
        assert len(activity.title)==1
        assert activity.title[0].text == 'fixture_title__text'
        assert activity.title[0].lang == 'fixture_title__lang'
        assert len(activity.description)==1
        assert activity.description[0].text == 'fixture_description__text'
        assert activity.description[0].type == 'fixture_description__type'
        assert activity.description[0].lang == 'fixture_description__lang'
        assert len(activity.status)==1
        assert activity.status[0].text == 'fixture_activity_status__text'
        assert activity.status[0].code == 'fixture_activity_status__code'
        assert activity.status[0].lang == 'fixture_activity_status__lang'
        assert len(activity.defaulttiedstatus)==1
        assert activity.defaulttiedstatus[0].text == 'fixture_default_tied_status__text'
        assert activity.defaulttiedstatus[0].code == 'fixture_default_tied_status__code'
        assert activity.defaulttiedstatus[0].lang == 'fixture_default_tied_status__lang'
        assert len(activity.policymarker)==1
        assert activity.policymarker[0].text == 'fixture_policy_marker__text'
        assert activity.policymarker[0].code == 'fixture_policy_marker__code'
        assert activity.policymarker[0].vocabulary == 'fixture_policy_marker__vocabulary'
        assert activity.policymarker[0].significance == 'fixture_policy_marker__significance'
        assert activity.policymarker[0].lang == 'fixture_policy_marker__lang'
        assert len(activity.location)==1
        assert activity.location[0].percentage == 999005.05
        assert len(activity.location[0].type)==1
        assert activity.location[0].type[0].text == 'fixture_location__location_type__text'
        assert activity.location[0].type[0].code == 'fixture_location__location_type__code'
        assert activity.location[0].type[0].lang == 'fixture_location__location_type__lang'
        assert len(activity.location[0].name)==1
        assert activity.location[0].name[0].text == 'fixture_location__name__text'
        assert activity.location[0].name[0].lang == 'fixture_location__name__lang'
        assert len(activity.location[0].description)==1
        assert activity.location[0].description[0].text == 'fixture_location__description__text'
        assert activity.location[0].description[0].lang == 'fixture_location__description__lang'
        assert len(activity.location[0].administrative)==1
        assert activity.location[0].administrative[0].text == 'fixture_location__administrative__text'
        assert activity.location[0].administrative[0].country == 'fixture_location__administrative__country'
        assert activity.location[0].administrative[0].adm1 == 'fixture_location__administrative__adm1'
        assert activity.location[0].administrative[0].adm2 == 'fixture_location__administrative__adm2'
        assert len(activity.location[0].coordinates)==1
        assert activity.location[0].coordinates[0].latitude == 999006.06
        assert activity.location[0].coordinates[0].longitude == 999007.07
        assert activity.location[0].coordinates[0].precision == 'fixture_location__coordinates__precision'
        assert len(activity.location[0].gazetteerentry)==1
        assert activity.location[0].gazetteerentry[0].text == 'fixture_location__gazetteer_entry__text'
        assert activity.location[0].gazetteerentry[0].gazetteer_ref == 'fixture_location__gazetteer_entry__gazetteer_ref'
        ## Results are deeply nested XML objects
        assert len(activity.result)==1
        assert len(activity.result[0].title)==1
        assert len(activity.result[0].description)==1
        assert len(activity.result[0].indicator)==1
        assert len(activity.result[0].indicator[0].title)==1
        assert len(activity.result[0].indicator[0].description)==1
        assert len(activity.result[0].indicator[0].baseline)==1
        assert len(activity.result[0].indicator[0].period)==1
        assert len(activity.result[0].indicator[0].period[0].start)==1
        assert len(activity.result[0].indicator[0].period[0].end)==1
        assert len(activity.result[0].indicator[0].period[0].target)==1
        assert len(activity.result[0].indicator[0].period[0].target[0].comment)==1
        assert len(activity.result[0].indicator[0].period[0].actual)==1
        assert len(activity.result[0].indicator[0].period[0].actual[0].comment)==1
        assert activity.result[0].type == 'fixture_result__type'
        assert activity.result[0].aggregation_status == True
        assert activity.result[0].title[0].text == 'fixture_result__title__text'
        assert activity.result[0].title[0].lang == 'fixture_result__title__lang'
        assert activity.result[0].description[0].text == 'fixture_result__description__text'
        assert activity.result[0].description[0].type == 'fixture_result__description__type'
        assert activity.result[0].description[0].lang == 'fixture_result__description__lang'
        assert activity.result[0].indicator[0].measure == 'fixture_result__indicator__measure'
        assert activity.result[0].indicator[0].ascending == True
        assert activity.result[0].indicator[0].title[0].text == 'fixture_result__indicator__title__text'
        assert activity.result[0].indicator[0].title[0].lang == 'fixture_result__indicator__title__lang'
        assert activity.result[0].indicator[0].description[0].text == 'fixture_result__indicator__description__text'
        assert activity.result[0].indicator[0].description[0].type == 'fixture_result__indicator__description__type'
        assert activity.result[0].indicator[0].description[0].lang == 'fixture_result__indicator__description__lang'
        assert activity.result[0].indicator[0].baseline[0].year == 1999
        assert activity.result[0].indicator[0].baseline[0].value == 'fixture_result__indicator__baseline__value'
        assert activity.result[0].indicator[0].baseline[0].comment[0].text == 'fixture_result__indicator__baseline__comment__text'
        assert activity.result[0].indicator[0].baseline[0].comment[0].lang == 'fixture_result__indicator__baseline__comment__lang'
        assert activity.result[0].indicator[0].period[0].start[0].text == 'fixture_result__indicator__period__period_start__text'
        assert activity.result[0].indicator[0].period[0].start[0].iso_date == datetime(year=2001,month=2,day=3,hour=4,minute=5,second=6,tzinfo=iso8601.iso8601.UTC)
        assert activity.result[0].indicator[0].period[0].end[0].text == 'fixture_result__indicator__period__period_end__text'
        assert activity.result[0].indicator[0].period[0].end[0].iso_date == datetime(year=2002,month=3,day=4,hour=5,minute=6,second=7,tzinfo=iso8601.iso8601.UTC)
        assert activity.result[0].indicator[0].period[0].target[0].value == 'fixture_result__indicator__period__target__value'
        assert activity.result[0].indicator[0].period[0].target[0].comment[0].text == 'fixture_result__indicator__period__target__comment__text'
        assert activity.result[0].indicator[0].period[0].target[0].comment[0].lang == 'fixture_result__indicator__period__target__comment__lang'
        assert activity.result[0].indicator[0].period[0].actual[0].value == 'fixture_result__indicator__period__actual__value'
        assert activity.result[0].indicator[0].period[0].actual[0].comment[0].text == 'fixture_result__indicator__period__actual__comment__text'
        assert activity.result[0].indicator[0].period[0].actual[0].comment[0].lang == 'fixture_result__indicator__period__actual__comment__lang'

        assert len(activity.conditions)==1
        assert len(activity.budget)==1
        assert len(activity.budget[0].period_start)==1
        assert len(activity.budget[0].period_end)==1
        assert len(activity.budget[0].value)==1
        assert len(activity.planned_disbursement)==1
        assert len(activity.planned_disbursement[0].period_start)==1
        assert len(activity.planned_disbursement[0].period_end)==1
        assert len(activity.planned_disbursement[0].value)==1
        assert len(activity.related_activity)==1
        assert len(activity.document_link)==1
        assert len(activity.document_link[0].title)==1
        assert len(activity.document_link[0].category)==1
        assert len(activity.document_link[0].language)==1
        assert len(activity.legacy_data)==1
        assert activity.conditions[0].attached == True
        assert activity.conditions[0].condition[0].text == 'fixture_conditions__condition__text'
        assert activity.conditions[0].condition[0].type == 'fixture_conditions__condition__type'
        assert activity.budget[0].type == 'fixture_budget__type'
        assert activity.budget[0].period_start[0].text == 'fixture_budget__period_start__text'
        assert activity.budget[0].period_start[0].iso_date == datetime(year=2003,month=4,day=5,hour=6,minute=7,second=8,tzinfo=iso8601.iso8601.UTC)
        assert activity.budget[0].period_end[0].text == 'fixture_budget__period_end__text'
        assert activity.budget[0].period_end[0].iso_date == datetime(year=2004,month=5,day=6,hour=7,minute=8,second=9,tzinfo=iso8601.iso8601.UTC)
        assert activity.budget[0].value[0].text == 999009.09
        assert activity.budget[0].value[0].currency == 'fixture_budget__value__currency'
        assert activity.budget[0].value[0].value_date == datetime(year=2005,month=6,day=7,hour=8,minute=9,second=10,tzinfo=iso8601.iso8601.UTC)
        assert activity.planned_disbursement[0].updated == 'fixture_planned_disbursement__updated'
        assert activity.planned_disbursement[0].period_start[0].text == 'fixture_planned_disbursement__period_start__text'
        assert activity.planned_disbursement[0].period_start[0].iso_date == datetime(year=2006,month=7,day=8,hour=9,minute=10,second=11,tzinfo=iso8601.iso8601.UTC)
        assert activity.planned_disbursement[0].period_end[0].text == 'fixture_planned_disbursement__period_end__text'
        assert activity.planned_disbursement[0].period_end[0].iso_date == datetime(year=2007,month=8,day=9,hour=10,minute=11,second=12,tzinfo=iso8601.iso8601.UTC)
        assert activity.planned_disbursement[0].value[0].text == 999010.1
        assert activity.planned_disbursement[0].value[0].currency == 'fixture_planned_disbursement__value__currency'
        assert activity.planned_disbursement[0].value[0].value_date == datetime(year=2008,month=9,day=10,hour=11,minute=12,second=13,tzinfo=iso8601.iso8601.UTC)
        assert activity.related_activity[0].text == 'fixture_related_activity__text'
        assert activity.related_activity[0].ref == 'fixture_related_activity__ref'
        assert activity.related_activity[0].type == 'fixture_related_activity__type'
        assert activity.related_activity[0].lang == 'fixture_related_activity__lang'
        assert activity.document_link[0].url == 'fixture_document_link__url'
        assert activity.document_link[0].format == 'fixture_document_link__format'
        assert activity.document_link[0].title[0].text == 'fixture_document_link__title__text'
        assert activity.document_link[0].title[0].lang == 'fixture_document_link__title__lang'
        assert activity.document_link[0].category[0].text == 'fixture_document_link__category__text'
        assert activity.document_link[0].category[0].code == 'fixture_document_link__category__code'
        assert activity.document_link[0].category[0].lang == 'fixture_document_link__category__lang'
        assert activity.document_link[0].language[0].text == 'fixture_document_link__language__text'
        assert activity.document_link[0].language[0].code == 'fixture_document_link__language__code'
        assert activity.document_link[0].language[0].lang == 'fixture_document_link__language__lang'
        assert activity.legacy_data[0].text == 'fixture_legacy_data__text'
        assert activity.legacy_data[0].name == 'fixture_legacy_data__name'
        assert activity.legacy_data[0].value == 'fixture_legacy_data__value'
        assert activity.legacy_data[0].iati_equivalent == 'fixture_legacy_data__iati_equivalent'
        ## Assertions: Transaction object
        assert len(activity.transaction)==1, len(activity.transaction)
        assert activity.transaction[0].ref == 'fixture_ref'
        assert len(activity.transaction[0].description)==1
        assert activity.transaction[0].description[0].text == 'fixture_description__text'
        assert activity.transaction[0].description[0].lang == 'fixture_description__lang'
        assert len(activity.transaction[0].type)==1
        assert activity.transaction[0].type[0].text == 'fixture_transaction_type__text'
        assert activity.transaction[0].type[0].code == 'fixture_transaction_type__code'
        assert activity.transaction[0].type[0].lang == 'fixture_transaction_type__lang'
        assert len(activity.transaction[0].provider_org)==1
        assert activity.transaction[0].provider_org[0].text == 'fixture_provider_org__text'
        assert activity.transaction[0].provider_org[0].ref == 'fixture_provider_org__ref'
        assert activity.transaction[0].provider_org[0].provider_activity_id == 'fixture_provider_org__provider_activity_id'
        assert len(activity.transaction[0].receiver_org)==1
        assert activity.transaction[0].receiver_org[0].text == 'fixture_receiver_org__text'
        assert activity.transaction[0].receiver_org[0].ref == 'fixture_receiver_org__ref'
        assert activity.transaction[0].receiver_org[0].receiver_activity_id == 'fixture_receiver_org__receiver_activity_id'
        assert len(activity.transaction[0].date)==1
        assert activity.transaction[0].date[0].text == 'fixture_transaction_date__text'
        assert activity.transaction[0].date[0].iso_date == datetime(year=2010,month=11,day=12,hour=13,minute=14,second=15,tzinfo=iso8601.iso8601.UTC)
        assert len(activity.transaction[0].flow_type)==1
        assert activity.transaction[0].flow_type[0].text == 'fixture_flow_type__text'
        assert activity.transaction[0].flow_type[0].code == 'fixture_flow_type__code'
        assert activity.transaction[0].flow_type[0].lang == 'fixture_flow_type__lang'
        assert len(activity.transaction[0].aid_type)==1
        assert activity.transaction[0].aid_type[0].text == 'fixture_aid_type__text'
        assert activity.transaction[0].aid_type[0].code == 'fixture_aid_type__code'
        assert activity.transaction[0].aid_type[0].lang == 'fixture_aid_type__lang'
        assert len(activity.transaction[0].finance_type)==1
        assert activity.transaction[0].finance_type[0].text == 'fixture_finance_type__text'
        assert activity.transaction[0].finance_type[0].code == 'fixture_finance_type__code'
        assert activity.transaction[0].finance_type[0].lang == 'fixture_finance_type__lang'
        assert len(activity.transaction[0].tied_status)==1
        assert activity.transaction[0].tied_status[0].text == 'fixture_tied_status__text'
        assert activity.transaction[0].tied_status[0].code == 'fixture_tied_status__code'
        assert activity.transaction[0].tied_status[0].lang == 'fixture_tied_status__lang'
        assert len(activity.transaction[0].disbursement_channel)==1
        assert activity.transaction[0].disbursement_channel[0].text == 'fixture_disbursement_channel__text'
        assert activity.transaction[0].disbursement_channel[0].code == 'fixture_disbursement_channel__code'
        assert activity.transaction[0].disbursement_channel[0].lang == 'fixture_disbursement_channel__lang'
        assert len(activity.transaction[0].value)==1
        assert activity.transaction[0].value[0].text == 999011.11
        assert activity.transaction[0].value[0].currency == 'fixture_value__currency'
        assert activity.transaction[0].value[0].value_date == datetime(year=2009,month=10,day=11,hour=12,minute=13,second=14,tzinfo=iso8601.iso8601.UTC)
        ## Assertions: Sector object
        assert len(activity.sector)==1, len(activity.sector)
        assert activity.sector[0].text == 'fixture_text'
        assert activity.sector[0].code == 999013
        assert activity.sector[0].vocabulary == 'fixture_vocabulary'
        assert activity.sector[0].percentage == 999012.12
        assert activity.sector[0].lang == 'fixture_lang'
        ## Assertions: ActivityDate object
        assert len(activity.date)==1, len(activity.activitydate)
        assert activity.date[0].text == 'fixture_text'
        assert activity.date[0].type == 'fixture_type'
        assert activity.date[0].iso_date == datetime(year=2011,month=12,day=13,hour=14,minute=15,second=16,tzinfo=iso8601.iso8601.UTC)
        assert activity.date[0].lang == 'fixture_lang'
        ## Assertions: ContactInfo object
        assert len(activity.contactinfo)==1, len(activity.contactinfo)
        assert len(activity.contactinfo[0].organisation)==1
        assert activity.contactinfo[0].organisation[0].text == 'fixture_organisation__text'
        assert len(activity.contactinfo[0].person)==1
        assert activity.contactinfo[0].person[0].text == 'fixture_person_name__text'
        assert len(activity.contactinfo[0].telephone)==1
        assert activity.contactinfo[0].telephone[0].text == 'fixture_telephone__text'
        assert len(activity.contactinfo[0].email)==1
        assert activity.contactinfo[0].email[0].text == 'fixture_email__text'
        assert len(activity.contactinfo[0].mail)==1
        assert activity.contactinfo[0].mail[0].text == 'fixture_mailing_address__text'
        ## len(Assertions: ParticipatingOrg object
        assert len(activity.participatingorg)==1, len(activity.participatingorg)
        assert activity.participatingorg[0].text == 'fixture_text'
        assert activity.participatingorg[0].ref == 'fixture_ref'
        assert activity.participatingorg[0].type == 'fixture_type'
        assert activity.participatingorg[0].role == 'fixture_role'
        assert activity.participatingorg[0].lang == 'fixture_lang'

    def test_commit_to_db(self):
        xmlblob = RawXmlBlob(raw_xml = _fixture_xml, parent_id=u'999999')
        db.session.add(xmlblob)
        db.session.commit()
        activity, errors = iatilib.parser.parse(xmlblob.raw_xml)
        xmlblob.activity = activity
        assert len(errors)==0, len(errors)
        db.session.commit()
        assert db.session.query(Activity).count()==1
        assert db.session.query(Transaction).count()==1
        db.session.delete(xmlblob.activity)
        db.session.commit()
        assert db.session.query(Activity).count()==0
        assert db.session.query(Transaction).count()==0
        assert xmlblob.activity is None
        db.session.delete(xmlblob)
        db.session.commit()
        assert db.session.query(RawXmlBlob).count()==0

    def test_double_commit_to_db(self):
        xmlblob = RawXmlBlob(raw_xml = _fixture_xml,parent_id=u'999999')
        xmlblob.activity,errors = iatilib.parser.parse(xmlblob.raw_xml)
        db.session.add(xmlblob)
        db.session.commit()
        assert db.session.query(Activity).count()==1
        assert db.session.query(Transaction).count()==1
        db.session.delete(xmlblob.activity)
        xmlblob.activity,errors = iatilib.parser.parse(xmlblob.raw_xml)
        db.session.commit()
        assert db.session.query(Activity).count()==1
        assert db.session.query(Transaction).count()==1
        db.session.delete(xmlblob)
        db.session.commit()
        assert db.session.query(RawXmlBlob).count()==0
        assert db.session.query(Activity).count()==0
        assert db.session.query(Transaction).count()==0
