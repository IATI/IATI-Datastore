from iatilib.model import *
import unittest
import tempfile
import iatilib.parser
import iso8601
from datetime import datetime
from iatilib import session

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

class CaseParser(unittest.TestCase):
    def setUp(self):
        assert len( list(session.query(CodelistSector)) )==0
        session.add( CodelistSector(code=999013) )
        assert len( list(session.query(IndexedResource)) )==0
        session.add( IndexedResource(id=u'999999') )
        session.commit()
    def tearDown(self):
        session.query(CodelistSector).delete()
        session.query(IndexedResource).delete()
        session.commit()
        assert len( list(session.query(IndexedResource)) )==0
        assert len( list(session.query(CodelistSector)) )==0

    def test_fixture_xml(self):
        activity, errors = iatilib.parser.parse(_fixture_xml)
        assert len(errors)==0
        assert len(activity.activitydate)==1, len(activity.activitydate)
        assert len(activity.sector)==1, len(activity.sector)
        assert len(activity.contactinfo)==1, len(activity.contactinfo)
        assert len(activity.participatingorg)==1, len(activity.participatingorg)
        ## Assertions: Activity object
        assert activity.version == 999001.01, obj_dict['activity'].version 
        assert activity.last_updated_datetime == datetime(year=2012,month=1,day=14,hour=15,minute=16,second=17,tzinfo=iso8601.iso8601.UTC), obj_dict['activity'].last_updated_datetime 
        assert activity.lang == 'fixture_lang', obj_dict['activity'].lang 
        assert activity.default_currency == 'fixture_default_currency', obj_dict['activity'].default_currency 
        assert activity.hierarchy == 999002.02, obj_dict['activity'].hierarchy 
        assert activity.linked_data_uri == 'fixture_linked_data_uri', obj_dict['activity'].linked_data_uri 
        assert activity.activity_website__text == 'fixture_activity_website__text', obj_dict['activity'].activity_website__text 
        assert activity.reporting_org__text == 'fixture_reporting_org__text', obj_dict['activity'].reporting_org__text 
        assert activity.reporting_org__ref == 'fixture_reporting_org__ref', obj_dict['activity'].reporting_org__ref 
        assert activity.reporting_org__type == 'fixture_reporting_org__type', obj_dict['activity'].reporting_org__type 
        assert activity.reporting_org__lang == 'fixture_reporting_org__lang', obj_dict['activity'].reporting_org__lang 
        assert activity.recipient_country__text == 'fixture_recipient_country__text', obj_dict['activity'].recipient_country__text 
        assert activity.recipient_country__code == 'fixture_recipient_country__code', obj_dict['activity'].recipient_country__code 
        assert activity.recipient_country__percentage == 999003.03, obj_dict['activity'].recipient_country__percentage 
        assert activity.recipient_country__lang == 'fixture_recipient_country__lang', obj_dict['activity'].recipient_country__lang 
        assert activity.recipient_region__text == 'fixture_recipient_region__text', obj_dict['activity'].recipient_region__text 
        assert activity.recipient_region__code == 'fixture_recipient_region__code', obj_dict['activity'].recipient_region__code 
        assert activity.recipient_region__percentage == 999004.04, obj_dict['activity'].recipient_region__percentage 
        assert activity.recipient_region__lang == 'fixture_recipient_region__lang', obj_dict['activity'].recipient_region__lang 
        assert activity.collaboration_type__text == 'fixture_collaboration_type__text', obj_dict['activity'].collaboration_type__text 
        assert activity.collaboration_type__code == 'fixture_collaboration_type__code', obj_dict['activity'].collaboration_type__code 
        assert activity.collaboration_type__lang == 'fixture_collaboration_type__lang', obj_dict['activity'].collaboration_type__lang 
        assert activity.default_flow_type__text == 'fixture_default_flow_type__text', obj_dict['activity'].default_flow_type__text 
        assert activity.default_flow_type__code == 'fixture_default_flow_type__code', obj_dict['activity'].default_flow_type__code 
        assert activity.default_flow_type__lang == 'fixture_default_flow_type__lang', obj_dict['activity'].default_flow_type__lang 
        assert activity.default_aid_type__text == 'fixture_default_aid_type__text', obj_dict['activity'].default_aid_type__text 
        assert activity.default_aid_type__code == 'fixture_default_aid_type__code', obj_dict['activity'].default_aid_type__code 
        assert activity.default_aid_type__lang == 'fixture_default_aid_type__lang', obj_dict['activity'].default_aid_type__lang 
        assert activity.default_finance_type__text == 'fixture_default_finance_type__text', obj_dict['activity'].default_finance_type__text 
        assert activity.default_finance_type__code == 'fixture_default_finance_type__code', obj_dict['activity'].default_finance_type__code 
        assert activity.default_finance_type__lang == 'fixture_default_finance_type__lang', obj_dict['activity'].default_finance_type__lang 
        assert activity.iati_identifier__text == 'fixture_iati_identifier__text', obj_dict['activity'].iati_identifier__text 
        assert activity.other_identifier__text == 'fixture_other_identifier__text', obj_dict['activity'].other_identifier__text 
        assert activity.other_identifier__owner_ref == 'fixture_other_identifier__owner_ref', obj_dict['activity'].other_identifier__owner_ref 
        assert activity.other_identifier__owner_name == 'fixture_other_identifier__owner_name', obj_dict['activity'].other_identifier__owner_name 
        assert activity.title__text == 'fixture_title__text', obj_dict['activity'].title__text 
        assert activity.title__lang == 'fixture_title__lang', obj_dict['activity'].title__lang 
        assert activity.description__text == 'fixture_description__text', obj_dict['activity'].description__text 
        assert activity.description__type == 'fixture_description__type', obj_dict['activity'].description__type 
        assert activity.description__lang == 'fixture_description__lang', obj_dict['activity'].description__lang 
        assert activity.activity_status__text == 'fixture_activity_status__text', obj_dict['activity'].activity_status__text 
        assert activity.activity_status__code == 'fixture_activity_status__code', obj_dict['activity'].activity_status__code 
        assert activity.activity_status__lang == 'fixture_activity_status__lang', obj_dict['activity'].activity_status__lang 
        assert activity.default_tied_status__text == 'fixture_default_tied_status__text', obj_dict['activity'].default_tied_status__text 
        assert activity.default_tied_status__code == 'fixture_default_tied_status__code', obj_dict['activity'].default_tied_status__code 
        assert activity.default_tied_status__lang == 'fixture_default_tied_status__lang', obj_dict['activity'].default_tied_status__lang 
        assert activity.policy_marker__text == 'fixture_policy_marker__text', obj_dict['activity'].policy_marker__text 
        assert activity.policy_marker__code == 'fixture_policy_marker__code', obj_dict['activity'].policy_marker__code 
        assert activity.policy_marker__vocabulary == 'fixture_policy_marker__vocabulary', obj_dict['activity'].policy_marker__vocabulary 
        assert activity.policy_marker__significance == 'fixture_policy_marker__significance', obj_dict['activity'].policy_marker__significance 
        assert activity.policy_marker__lang == 'fixture_policy_marker__lang', obj_dict['activity'].policy_marker__lang 
        assert activity.location__percentage == 999005.05, obj_dict['activity'].location__percentage 
        assert activity.location__location_type__text == 'fixture_location__location_type__text', obj_dict['activity'].location__location_type__text 
        assert activity.location__location_type__code == 'fixture_location__location_type__code', obj_dict['activity'].location__location_type__code 
        assert activity.location__location_type__lang == 'fixture_location__location_type__lang', obj_dict['activity'].location__location_type__lang 
        assert activity.location__name__text == 'fixture_location__name__text', obj_dict['activity'].location__name__text 
        assert activity.location__name__lang == 'fixture_location__name__lang', obj_dict['activity'].location__name__lang 
        assert activity.location__description__text == 'fixture_location__description__text', obj_dict['activity'].location__description__text 
        assert activity.location__description__lang == 'fixture_location__description__lang', obj_dict['activity'].location__description__lang 
        assert activity.location__administrative__text == 'fixture_location__administrative__text', obj_dict['activity'].location__administrative__text 
        assert activity.location__administrative__country == 'fixture_location__administrative__country', obj_dict['activity'].location__administrative__country 
        assert activity.location__administrative__adm1 == 'fixture_location__administrative__adm1', obj_dict['activity'].location__administrative__adm1 
        assert activity.location__administrative__adm2 == 'fixture_location__administrative__adm2', obj_dict['activity'].location__administrative__adm2 
        assert activity.location__coordinates__latitude == 999006.06, obj_dict['activity'].location__coordinates__latitude 
        assert activity.location__coordinates__longitude == 999007.07, obj_dict['activity'].location__coordinates__longitude 
        assert activity.location__coordinates__precision == 'fixture_location__coordinates__precision', obj_dict['activity'].location__coordinates__precision 
        assert activity.location__gazetteer_entry__text == 'fixture_location__gazetteer_entry__text', obj_dict['activity'].location__gazetteer_entry__text 
        assert activity.location__gazetteer_entry__gazetteer_ref == 'fixture_location__gazetteer_entry__gazetteer_ref', obj_dict['activity'].location__gazetteer_entry__gazetteer_ref 
        assert activity.result__type == 'fixture_result__type', obj_dict['activity'].result__type 
        assert activity.result__aggregation_status == True, obj_dict['activity'].result__aggregation_status 
        assert activity.result__title__text == 'fixture_result__title__text', obj_dict['activity'].result__title__text 
        assert activity.result__title__lang == 'fixture_result__title__lang', obj_dict['activity'].result__title__lang 
        assert activity.result__description__text == 'fixture_result__description__text', obj_dict['activity'].result__description__text 
        assert activity.result__description__type == 'fixture_result__description__type', obj_dict['activity'].result__description__type 
        assert activity.result__description__lang == 'fixture_result__description__lang', obj_dict['activity'].result__description__lang 
        assert activity.result__indicator__measure == 'fixture_result__indicator__measure', obj_dict['activity'].result__indicator__measure 
        assert activity.result__indicator__ascending == True, obj_dict['activity'].result__indicator__ascending 
        assert activity.result__indicator__title__text == 'fixture_result__indicator__title__text', obj_dict['activity'].result__indicator__title__text 
        assert activity.result__indicator__title__lang == 'fixture_result__indicator__title__lang', obj_dict['activity'].result__indicator__title__lang 
        assert activity.result__indicator__description__text == 'fixture_result__indicator__description__text', obj_dict['activity'].result__indicator__description__text 
        assert activity.result__indicator__description__type == 'fixture_result__indicator__description__type', obj_dict['activity'].result__indicator__description__type 
        assert activity.result__indicator__description__lang == 'fixture_result__indicator__description__lang', obj_dict['activity'].result__indicator__description__lang 
        assert activity.result__indicator__baseline__year == 1999, obj_dict['activity'].result__indicator__baseline__year 
        assert activity.result__indicator__baseline__value == 'fixture_result__indicator__baseline__value', obj_dict['activity'].result__indicator__baseline__value 
        assert activity.result__indicator__baseline__comment__text == 'fixture_result__indicator__baseline__comment__text', obj_dict['activity'].result__indicator__baseline__comment__text 
        assert activity.result__indicator__baseline__comment__lang == 'fixture_result__indicator__baseline__comment__lang', obj_dict['activity'].result__indicator__baseline__comment__lang 
        assert activity.result__indicator__period__period_start__text == 'fixture_result__indicator__period__period_start__text', obj_dict['activity'].result__indicator__period__period_start__text 
        assert activity.result__indicator__period__period_start__iso_date == datetime(year=2001,month=2,day=3,hour=4,minute=5,second=6,tzinfo=iso8601.iso8601.UTC), obj_dict['activity'].result__indicator__period__period_start__iso_date 
        assert activity.result__indicator__period__period_end__text == 'fixture_result__indicator__period__period_end__text', obj_dict['activity'].result__indicator__period__period_end__text 
        assert activity.result__indicator__period__period_end__iso_date == datetime(year=2002,month=3,day=4,hour=5,minute=6,second=7,tzinfo=iso8601.iso8601.UTC), obj_dict['activity'].result__indicator__period__period_end__iso_date 
        assert activity.result__indicator__period__target__value == 'fixture_result__indicator__period__target__value', obj_dict['activity'].result__indicator__period__target__value 
        assert activity.result__indicator__period__target__comment__text == 'fixture_result__indicator__period__target__comment__text', obj_dict['activity'].result__indicator__period__target__comment__text 
        assert activity.result__indicator__period__target__comment__lang == 'fixture_result__indicator__period__target__comment__lang', obj_dict['activity'].result__indicator__period__target__comment__lang 
        assert activity.result__indicator__period__actual__value == 'fixture_result__indicator__period__actual__value', obj_dict['activity'].result__indicator__period__actual__value 
        assert activity.result__indicator__period__actual__comment__text == 'fixture_result__indicator__period__actual__comment__text', obj_dict['activity'].result__indicator__period__actual__comment__text 
        assert activity.result__indicator__period__actual__comment__lang == 'fixture_result__indicator__period__actual__comment__lang', obj_dict['activity'].result__indicator__period__actual__comment__lang 
        assert activity.conditions__attached == True, obj_dict['activity'].conditions__attached 
        assert activity.conditions__condition__text == 'fixture_conditions__condition__text', obj_dict['activity'].conditions__condition__text 
        assert activity.conditions__condition__type == 'fixture_conditions__condition__type', obj_dict['activity'].conditions__condition__type 
        assert activity.budget__type == 'fixture_budget__type', obj_dict['activity'].budget__type 
        assert activity.budget__period_start__text == 'fixture_budget__period_start__text', obj_dict['activity'].budget__period_start__text 
        assert activity.budget__period_start__iso_date == datetime(year=2003,month=4,day=5,hour=6,minute=7,second=8,tzinfo=iso8601.iso8601.UTC), obj_dict['activity'].budget__period_start__iso_date 
        assert activity.budget__period_end__text == 'fixture_budget__period_end__text', obj_dict['activity'].budget__period_end__text 
        assert activity.budget__period_end__iso_date == datetime(year=2004,month=5,day=6,hour=7,minute=8,second=9,tzinfo=iso8601.iso8601.UTC), obj_dict['activity'].budget__period_end__iso_date 
        assert activity.budget__value__text == 999009.09, obj_dict['activity'].budget__value__text 
        assert activity.budget__value__currency == 'fixture_budget__value__currency', obj_dict['activity'].budget__value__currency 
        assert activity.budget__value__value_date == datetime(year=2005,month=6,day=7,hour=8,minute=9,second=10,tzinfo=iso8601.iso8601.UTC), obj_dict['activity'].budget__value__value_date 
        assert activity.planned_disbursement__updated == 'fixture_planned_disbursement__updated', obj_dict['activity'].planned_disbursement__updated 
        assert activity.planned_disbursement__period_start__text == 'fixture_planned_disbursement__period_start__text', obj_dict['activity'].planned_disbursement__period_start__text 
        assert activity.planned_disbursement__period_start__iso_date == datetime(year=2006,month=7,day=8,hour=9,minute=10,second=11,tzinfo=iso8601.iso8601.UTC), obj_dict['activity'].planned_disbursement__period_start__iso_date 
        assert activity.planned_disbursement__period_end__text == 'fixture_planned_disbursement__period_end__text', obj_dict['activity'].planned_disbursement__period_end__text 
        assert activity.planned_disbursement__period_end__iso_date == datetime(year=2007,month=8,day=9,hour=10,minute=11,second=12,tzinfo=iso8601.iso8601.UTC), obj_dict['activity'].planned_disbursement__period_end__iso_date 
        assert activity.planned_disbursement__value__text == 999010.1, obj_dict['activity'].planned_disbursement__value__text 
        assert activity.planned_disbursement__value__currency == 'fixture_planned_disbursement__value__currency', obj_dict['activity'].planned_disbursement__value__currency 
        assert activity.planned_disbursement__value__value_date == datetime(year=2008,month=9,day=10,hour=11,minute=12,second=13,tzinfo=iso8601.iso8601.UTC), obj_dict['activity'].planned_disbursement__value__value_date 
        assert activity.related_activity__text == 'fixture_related_activity__text', obj_dict['activity'].related_activity__text 
        assert activity.related_activity__ref == 'fixture_related_activity__ref', obj_dict['activity'].related_activity__ref 
        assert activity.related_activity__type == 'fixture_related_activity__type', obj_dict['activity'].related_activity__type 
        assert activity.related_activity__lang == 'fixture_related_activity__lang', obj_dict['activity'].related_activity__lang 
        assert activity.document_link__url == 'fixture_document_link__url', obj_dict['activity'].document_link__url 
        assert activity.document_link__format == 'fixture_document_link__format', obj_dict['activity'].document_link__format 
        assert activity.document_link__title__text == 'fixture_document_link__title__text', obj_dict['activity'].document_link__title__text 
        assert activity.document_link__title__lang == 'fixture_document_link__title__lang', obj_dict['activity'].document_link__title__lang 
        assert activity.document_link__category__text == 'fixture_document_link__category__text', obj_dict['activity'].document_link__category__text 
        assert activity.document_link__category__code == 'fixture_document_link__category__code', obj_dict['activity'].document_link__category__code 
        assert activity.document_link__category__lang == 'fixture_document_link__category__lang', obj_dict['activity'].document_link__category__lang 
        assert activity.document_link__language__text == 'fixture_document_link__language__text', obj_dict['activity'].document_link__language__text 
        assert activity.document_link__language__code == 'fixture_document_link__language__code', obj_dict['activity'].document_link__language__code 
        assert activity.document_link__language__lang == 'fixture_document_link__language__lang', obj_dict['activity'].document_link__language__lang 
        assert activity.legacy_data__text == 'fixture_legacy_data__text', obj_dict['activity'].legacy_data__text 
        assert activity.legacy_data__name == 'fixture_legacy_data__name', obj_dict['activity'].legacy_data__name 
        assert activity.legacy_data__value == 'fixture_legacy_data__value', obj_dict['activity'].legacy_data__value 
        assert activity.legacy_data__iati_equivalent == 'fixture_legacy_data__iati_equivalent', obj_dict['activity'].legacy_data__iati_equivalent 
        ## Assertions: Transaction object
        assert len(activity.transaction)==1, len(activity.transaction)
        assert activity.transaction[0].ref == 'fixture_ref', obj_dict['transaction'].ref 
        assert activity.transaction[0].description__text == 'fixture_description__text', obj_dict['transaction'].description__text 
        assert activity.transaction[0].description__lang == 'fixture_description__lang', obj_dict['transaction'].description__lang 
        assert activity.transaction[0].transaction_type__text == 'fixture_transaction_type__text', obj_dict['transaction'].transaction_type__text 
        assert activity.transaction[0].transaction_type__code == 'fixture_transaction_type__code', obj_dict['transaction'].transaction_type__code 
        assert activity.transaction[0].transaction_type__lang == 'fixture_transaction_type__lang', obj_dict['transaction'].transaction_type__lang 
        assert activity.transaction[0].provider_org__text == 'fixture_provider_org__text', obj_dict['transaction'].provider_org__text 
        assert activity.transaction[0].provider_org__ref == 'fixture_provider_org__ref', obj_dict['transaction'].provider_org__ref 
        assert activity.transaction[0].provider_org__provider_activity_id == 'fixture_provider_org__provider_activity_id', obj_dict['transaction'].provider_org__provider_activity_id 
        assert activity.transaction[0].receiver_org__text == 'fixture_receiver_org__text', obj_dict['transaction'].receiver_org__text 
        assert activity.transaction[0].receiver_org__ref == 'fixture_receiver_org__ref', obj_dict['transaction'].receiver_org__ref 
        assert activity.transaction[0].receiver_org__receiver_activity_id == 'fixture_receiver_org__receiver_activity_id', obj_dict['transaction'].receiver_org__receiver_activity_id 
        assert activity.transaction[0].transaction_date__text == 'fixture_transaction_date__text', obj_dict['transaction'].transaction_date__text 
        assert activity.transaction[0].transaction_date__iso_date == datetime(year=2010,month=11,day=12,hour=13,minute=14,second=15,tzinfo=iso8601.iso8601.UTC), obj_dict['transaction'].transaction_date__iso_date 
        assert activity.transaction[0].flow_type__text == 'fixture_flow_type__text', obj_dict['transaction'].flow_type__text 
        assert activity.transaction[0].flow_type__code == 'fixture_flow_type__code', obj_dict['transaction'].flow_type__code 
        assert activity.transaction[0].flow_type__lang == 'fixture_flow_type__lang', obj_dict['transaction'].flow_type__lang 
        assert activity.transaction[0].aid_type__text == 'fixture_aid_type__text', obj_dict['transaction'].aid_type__text 
        assert activity.transaction[0].aid_type__code == 'fixture_aid_type__code', obj_dict['transaction'].aid_type__code 
        assert activity.transaction[0].aid_type__lang == 'fixture_aid_type__lang', obj_dict['transaction'].aid_type__lang 
        assert activity.transaction[0].finance_type__text == 'fixture_finance_type__text', obj_dict['transaction'].finance_type__text 
        assert activity.transaction[0].finance_type__code == 'fixture_finance_type__code', obj_dict['transaction'].finance_type__code 
        assert activity.transaction[0].finance_type__lang == 'fixture_finance_type__lang', obj_dict['transaction'].finance_type__lang 
        assert activity.transaction[0].tied_status__text == 'fixture_tied_status__text', obj_dict['transaction'].tied_status__text 
        assert activity.transaction[0].tied_status__code == 'fixture_tied_status__code', obj_dict['transaction'].tied_status__code 
        assert activity.transaction[0].tied_status__lang == 'fixture_tied_status__lang', obj_dict['transaction'].tied_status__lang 
        assert activity.transaction[0].disbursement_channel__text == 'fixture_disbursement_channel__text', obj_dict['transaction'].disbursement_channel__text 
        assert activity.transaction[0].disbursement_channel__code == 'fixture_disbursement_channel__code', obj_dict['transaction'].disbursement_channel__code 
        assert activity.transaction[0].disbursement_channel__lang == 'fixture_disbursement_channel__lang', obj_dict['transaction'].disbursement_channel__lang 
        assert len(activity.transaction[0].transaction_value)==1
        assert activity.transaction[0].transaction_value[0].text == 999011.11, obj_dict['transaction'].value__text 
        assert activity.transaction[0].transaction_value[0].currency == 'fixture_value__currency', obj_dict['transaction'].value__currency 
        assert activity.transaction[0].transaction_value[0].value_date == datetime(year=2009,month=10,day=11,hour=12,minute=13,second=14,tzinfo=iso8601.iso8601.UTC), obj_dict['transaction'].value__value_date 
        ## Assertions: Sector object
        assert activity.sector[0].text == 'fixture_text', obj_dict['sector'].text 
        assert activity.sector[0].code == 999013, obj_dict['sector'].code 
        assert activity.sector[0].vocabulary == 'fixture_vocabulary', obj_dict['sector'].vocabulary 
        assert activity.sector[0].percentage == 999012.12, obj_dict['sector'].percentage 
        assert activity.sector[0].lang == 'fixture_lang', obj_dict['sector'].lang 
        ## Assertions: ActivityDate object
        assert activity.activitydate[0].text == 'fixture_text', obj_dict['activitydate'].text 
        assert activity.activitydate[0].type == 'fixture_type', obj_dict['activitydate'].type 
        assert activity.activitydate[0].iso_date == datetime(year=2011,month=12,day=13,hour=14,minute=15,second=16,tzinfo=iso8601.iso8601.UTC), obj_dict['activitydate'].iso_date 
        assert activity.activitydate[0].lang == 'fixture_lang', obj_dict['activitydate'].lang 
        ## Assertions: ContactInfo object
        assert activity.contactinfo[0].organisation__text == 'fixture_organisation__text', obj_dict['contactinfo'].organisation__text 
        assert activity.contactinfo[0].person_name__text == 'fixture_person_name__text', obj_dict['contactinfo'].person_name__text 
        assert activity.contactinfo[0].telephone__text == 'fixture_telephone__text', obj_dict['contactinfo'].telephone__text 
        assert activity.contactinfo[0].email__text == 'fixture_email__text', obj_dict['contactinfo'].email__text 
        assert activity.contactinfo[0].mailing_address__text == 'fixture_mailing_address__text', obj_dict['contactinfo'].mailing_address__text 
        ## Assertions: ParticipatingOrg object
        assert activity.participatingorg[0].text == 'fixture_text', obj_dict['participatingorg'].text 
        assert activity.participatingorg[0].ref == 'fixture_ref', obj_dict['participatingorg'].ref 
        assert activity.participatingorg[0].type == 'fixture_type', obj_dict['participatingorg'].type 
        assert activity.participatingorg[0].role == 'fixture_role', obj_dict['participatingorg'].role 
        assert activity.participatingorg[0].lang == 'fixture_lang', obj_dict['participatingorg'].lang 

    def test_commit_to_db(self):
        xmlblob = RawXmlBlob(raw_xml = _fixture_xml, parent_id=u'999999')
        session.add(xmlblob)
        session.commit()
        activity, errors = iatilib.parser.parse(xmlblob.raw_xml)
        xmlblob.activity = activity
        assert len(errors)==0, len(errors)
        session.commit()
        assert session.query(Activity).count()==1
        assert session.query(Transaction).count()==1
        session.delete(xmlblob.activity)
        session.commit()
        assert session.query(Activity).count()==0
        assert session.query(Transaction).count()==0
        assert xmlblob.activity is None
        session.delete(xmlblob)
        session.commit()
        assert session.query(RawXmlBlob).count()==0

    def test_double_commit_to_db(self):
        xmlblob = RawXmlBlob(raw_xml = _fixture_xml,parent_id=u'999999') 
        xmlblob.activity,errors = iatilib.parser.parse(xmlblob.raw_xml)
        session.add(xmlblob)
        session.commit()
        assert session.query(Activity).count()==1
        assert session.query(Transaction).count()==1
        session.delete(xmlblob.activity)
        xmlblob.activity,errors = iatilib.parser.parse(xmlblob.raw_xml)
        session.commit()
        assert session.query(Activity).count()==1
        assert session.query(Transaction).count()==1
        session.delete(xmlblob)
        session.commit()
        assert session.query(RawXmlBlob).count()==0
        assert session.query(Activity).count()==0
        assert session.query(Transaction).count()==0
