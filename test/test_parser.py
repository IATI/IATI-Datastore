from iatilib.model import *
import unittest
import tempfile
import iatilib.parser
import iso8601
from datetime import datetime

# Hand-generated XML used to test the parser
_fixture_xml = """
<iati-activities>
    <iati-activity 
      version="999001.01" 
      hierarchy="999002.02" 
      default-currency="fixture_default_currency" 
      xml:lang="fixture_lang" 
      linked-data-uri="fixture_linked_data_uri"
      last-updated-datetime="2011-10-17T14:13:17">
        <iati-identifier>
            fixture_iati_identifier__text
        </iati-identifier>
        <activity-website>
            fixture_activity_website__text
        </activity-website>
        <reporting-org 
          ref="fixture_reporting_org__ref" 
          type="fixture_reporting_org__type"
          xml:lang="fixture_reporting_org__lang">
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
                    <period-start iso-date="fixture_result__indicator__period__period_start__iso_date">
                        fixture_result__indicator__period__period_start__text
                    </period-start>
                    <period-end iso-date="fixture_result__indicator__period__period_end__iso_date">
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
            <period-start iso-date="fixture_budget__period_start__iso_date">
                fixture_budget__period_start__text
            </period-start>
            <period-end iso-date="fixture_budget__period_end__iso_date">
                fixture_budget__period_end__text
            </period-end>
            <value currency="fixture_budget__value__currency" value-date="fixture_budget__value__value_date">
                999009.09
            </value>
        </budget>
        <planned-disbursement updated="fixture_planned_disbursement__updated">
            <period-start iso-date="fixture_planned_disbursement__period_start__iso_date">
                fixture_planned_disbursement__period_start__text
            </period-start>
            <period-end iso-date="fixture_planned_disbursement__period_end__iso_date">
                fixture_planned_disbursement__period_end__text
            </period-end>
            <value currency="fixture_planned_disbursement__value__currency" value-date="fixture_planned_disbursement__value__value_date">
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
            <value currency="fixture_value__currency" value-date="fixture_value__value_date">
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
            <transaction-date iso-date="fixture_transaction_date__iso_date">
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
        <sector code="fixture_code" vocabulary="fixture_vocabulary" percentage="999012.12" xml:lang="fixture_lang">
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
        <activity-date type="fixture_type" iso-date="fixture_iso_date" xml:lang="fixture_lang">
            fixture_text
        </activity-date>
    </iati-activity>
</iati-activities>
"""

class CaseParser(unittest.TestCase):
    def test_fixture_xml(self):
        temp = tempfile.NamedTemporaryFile()
        temp.write( _fixture_xml )
        temp.flush()
        url = 'file://%s' % temp.name
        objects = iatilib.parser.parse(url)
        temp.close()
        assert len(objects)>0, 'Parse error'
        # Analyse all objects
        obj_dict = { x.__tablename__ : x for x in objects }
        assert len(obj_dict)==len(objects), 'Expected one of each top-level element, %s' % ( ','.join([x.__tablename__ for x in objects]) )
        expected_keys = set(['sector','transaction','activity','activitydate','participatingorg','contactinfo'])
        found_keys = set( obj_dict.keys() )
        assert found_keys==expected_keys, 'Missing objects: %s ' % ','.join(list(expected_keys-found_keys))
        ## Assertions: Activity object
        assert obj_dict['activity'].version == 999001.01, obj_dict['activity'].version 
        assert obj_dict['activity'].last_updated_datetime == datetime(year=2011,month=10,day=17,hour=14,minute=13,second=17,tzinfo=iso8601.iso8601.UTC), obj_dict['activity'].last_updated_datetime 
        assert obj_dict['activity'].lang == 'fixture_lang', obj_dict['activity'].lang 
        assert obj_dict['activity'].default_currency == 'fixture_default_currency', obj_dict['activity'].default_currency 
        assert obj_dict['activity'].hierarchy == 999002.02, obj_dict['activity'].hierarchy 
        assert obj_dict['activity'].linked_data_uri == 'fixture_linked_data_uri', obj_dict['activity'].linked_data_uri 
        assert obj_dict['activity'].activity_website__text == 'fixture_activity_website__text', obj_dict['activity'].activity_website__text 
        assert obj_dict['activity'].reporting_org__text == 'fixture_reporting_org__text', obj_dict['activity'].reporting_org__text 
        assert obj_dict['activity'].reporting_org__ref == 'fixture_reporting_org__ref', obj_dict['activity'].reporting_org__ref 
        assert obj_dict['activity'].reporting_org__type == 'fixture_reporting_org__type', obj_dict['activity'].reporting_org__type 
        assert obj_dict['activity'].reporting_org__lang == 'fixture_reporting_org__lang', obj_dict['activity'].reporting_org__lang 
        assert obj_dict['activity'].recipient_country__text == 'fixture_recipient_country__text', obj_dict['activity'].recipient_country__text 
        assert obj_dict['activity'].recipient_country__code == 'fixture_recipient_country__code', obj_dict['activity'].recipient_country__code 
        assert obj_dict['activity'].recipient_country__percentage == 999003.03, obj_dict['activity'].recipient_country__percentage 
        assert obj_dict['activity'].recipient_country__lang == 'fixture_recipient_country__lang', obj_dict['activity'].recipient_country__lang 
        assert obj_dict['activity'].recipient_region__text == 'fixture_recipient_region__text', obj_dict['activity'].recipient_region__text 
        assert obj_dict['activity'].recipient_region__code == 'fixture_recipient_region__code', obj_dict['activity'].recipient_region__code 
        assert obj_dict['activity'].recipient_region__percentage == 999004.04, obj_dict['activity'].recipient_region__percentage 
        assert obj_dict['activity'].recipient_region__lang == 'fixture_recipient_region__lang', obj_dict['activity'].recipient_region__lang 
        assert obj_dict['activity'].collaboration_type__text == 'fixture_collaboration_type__text', obj_dict['activity'].collaboration_type__text 
        assert obj_dict['activity'].collaboration_type__code == 'fixture_collaboration_type__code', obj_dict['activity'].collaboration_type__code 
        assert obj_dict['activity'].collaboration_type__lang == 'fixture_collaboration_type__lang', obj_dict['activity'].collaboration_type__lang 
        assert obj_dict['activity'].default_flow_type__text == 'fixture_default_flow_type__text', obj_dict['activity'].default_flow_type__text 
        assert obj_dict['activity'].default_flow_type__code == 'fixture_default_flow_type__code', obj_dict['activity'].default_flow_type__code 
        assert obj_dict['activity'].default_flow_type__lang == 'fixture_default_flow_type__lang', obj_dict['activity'].default_flow_type__lang 
        assert obj_dict['activity'].default_aid_type__text == 'fixture_default_aid_type__text', obj_dict['activity'].default_aid_type__text 
        assert obj_dict['activity'].default_aid_type__code == 'fixture_default_aid_type__code', obj_dict['activity'].default_aid_type__code 
        assert obj_dict['activity'].default_aid_type__lang == 'fixture_default_aid_type__lang', obj_dict['activity'].default_aid_type__lang 
        assert obj_dict['activity'].default_finance_type__text == 'fixture_default_finance_type__text', obj_dict['activity'].default_finance_type__text 
        assert obj_dict['activity'].default_finance_type__code == 'fixture_default_finance_type__code', obj_dict['activity'].default_finance_type__code 
        assert obj_dict['activity'].default_finance_type__lang == 'fixture_default_finance_type__lang', obj_dict['activity'].default_finance_type__lang 
        assert obj_dict['activity'].iati_identifier__text == 'fixture_iati_identifier__text', obj_dict['activity'].iati_identifier__text 
        assert obj_dict['activity'].other_identifier__text == 'fixture_other_identifier__text', obj_dict['activity'].other_identifier__text 
        assert obj_dict['activity'].other_identifier__owner_ref == 'fixture_other_identifier__owner_ref', obj_dict['activity'].other_identifier__owner_ref 
        assert obj_dict['activity'].other_identifier__owner_name == 'fixture_other_identifier__owner_name', obj_dict['activity'].other_identifier__owner_name 
        assert obj_dict['activity'].title__text == 'fixture_title__text', obj_dict['activity'].title__text 
        assert obj_dict['activity'].title__lang == 'fixture_title__lang', obj_dict['activity'].title__lang 
        assert obj_dict['activity'].description__text == 'fixture_description__text', obj_dict['activity'].description__text 
        assert obj_dict['activity'].description__type == 'fixture_description__type', obj_dict['activity'].description__type 
        assert obj_dict['activity'].description__lang == 'fixture_description__lang', obj_dict['activity'].description__lang 
        assert obj_dict['activity'].activity_status__text == 'fixture_activity_status__text', obj_dict['activity'].activity_status__text 
        assert obj_dict['activity'].activity_status__code == 'fixture_activity_status__code', obj_dict['activity'].activity_status__code 
        assert obj_dict['activity'].activity_status__lang == 'fixture_activity_status__lang', obj_dict['activity'].activity_status__lang 
        assert obj_dict['activity'].default_tied_status__text == 'fixture_default_tied_status__text', obj_dict['activity'].default_tied_status__text 
        assert obj_dict['activity'].default_tied_status__code == 'fixture_default_tied_status__code', obj_dict['activity'].default_tied_status__code 
        assert obj_dict['activity'].default_tied_status__lang == 'fixture_default_tied_status__lang', obj_dict['activity'].default_tied_status__lang 
        assert obj_dict['activity'].policy_marker__text == 'fixture_policy_marker__text', obj_dict['activity'].policy_marker__text 
        assert obj_dict['activity'].policy_marker__code == 'fixture_policy_marker__code', obj_dict['activity'].policy_marker__code 
        assert obj_dict['activity'].policy_marker__vocabulary == 'fixture_policy_marker__vocabulary', obj_dict['activity'].policy_marker__vocabulary 
        assert obj_dict['activity'].policy_marker__significance == 'fixture_policy_marker__significance', obj_dict['activity'].policy_marker__significance 
        assert obj_dict['activity'].policy_marker__lang == 'fixture_policy_marker__lang', obj_dict['activity'].policy_marker__lang 
        assert obj_dict['activity'].location__percentage == 999005.05, obj_dict['activity'].location__percentage 
        assert obj_dict['activity'].location__location_type__text == 'fixture_location__location_type__text', obj_dict['activity'].location__location_type__text 
        assert obj_dict['activity'].location__location_type__code == 'fixture_location__location_type__code', obj_dict['activity'].location__location_type__code 
        assert obj_dict['activity'].location__location_type__lang == 'fixture_location__location_type__lang', obj_dict['activity'].location__location_type__lang 
        assert obj_dict['activity'].location__name__text == 'fixture_location__name__text', obj_dict['activity'].location__name__text 
        assert obj_dict['activity'].location__name__lang == 'fixture_location__name__lang', obj_dict['activity'].location__name__lang 
        assert obj_dict['activity'].location__description__text == 'fixture_location__description__text', obj_dict['activity'].location__description__text 
        assert obj_dict['activity'].location__description__lang == 'fixture_location__description__lang', obj_dict['activity'].location__description__lang 
        assert obj_dict['activity'].location__administrative__text == 'fixture_location__administrative__text', obj_dict['activity'].location__administrative__text 
        assert obj_dict['activity'].location__administrative__country == 'fixture_location__administrative__country', obj_dict['activity'].location__administrative__country 
        assert obj_dict['activity'].location__administrative__adm1 == 'fixture_location__administrative__adm1', obj_dict['activity'].location__administrative__adm1 
        assert obj_dict['activity'].location__administrative__adm2 == 'fixture_location__administrative__adm2', obj_dict['activity'].location__administrative__adm2 
        assert obj_dict['activity'].location__coordinates__latitude == 999006.06, obj_dict['activity'].location__coordinates__latitude 
        assert obj_dict['activity'].location__coordinates__longitude == 999007.07, obj_dict['activity'].location__coordinates__longitude 
        assert obj_dict['activity'].location__coordinates__precision == 'fixture_location__coordinates__precision', obj_dict['activity'].location__coordinates__precision 
        assert obj_dict['activity'].location__gazetteer_entry__text == 'fixture_location__gazetteer_entry__text', obj_dict['activity'].location__gazetteer_entry__text 
        assert obj_dict['activity'].location__gazetteer_entry__gazetteer_ref == 'fixture_location__gazetteer_entry__gazetteer_ref', obj_dict['activity'].location__gazetteer_entry__gazetteer_ref 
        assert obj_dict['activity'].result__type == 'fixture_result__type', obj_dict['activity'].result__type 
        assert obj_dict['activity'].result__aggregation_status == True, obj_dict['activity'].result__aggregation_status 
        assert obj_dict['activity'].result__title__text == 'fixture_result__title__text', obj_dict['activity'].result__title__text 
        assert obj_dict['activity'].result__title__lang == 'fixture_result__title__lang', obj_dict['activity'].result__title__lang 
        assert obj_dict['activity'].result__description__text == 'fixture_result__description__text', obj_dict['activity'].result__description__text 
        assert obj_dict['activity'].result__description__type == 'fixture_result__description__type', obj_dict['activity'].result__description__type 
        assert obj_dict['activity'].result__description__lang == 'fixture_result__description__lang', obj_dict['activity'].result__description__lang 
        assert obj_dict['activity'].result__indicator__measure == 'fixture_result__indicator__measure', obj_dict['activity'].result__indicator__measure 
        assert obj_dict['activity'].result__indicator__ascending == True, obj_dict['activity'].result__indicator__ascending 
        assert obj_dict['activity'].result__indicator__title__text == 'fixture_result__indicator__title__text', obj_dict['activity'].result__indicator__title__text 
        assert obj_dict['activity'].result__indicator__title__lang == 'fixture_result__indicator__title__lang', obj_dict['activity'].result__indicator__title__lang 
        assert obj_dict['activity'].result__indicator__description__text == 'fixture_result__indicator__description__text', obj_dict['activity'].result__indicator__description__text 
        assert obj_dict['activity'].result__indicator__description__type == 'fixture_result__indicator__description__type', obj_dict['activity'].result__indicator__description__type 
        assert obj_dict['activity'].result__indicator__description__lang == 'fixture_result__indicator__description__lang', obj_dict['activity'].result__indicator__description__lang 
        assert obj_dict['activity'].result__indicator__baseline__year == 1999, obj_dict['activity'].result__indicator__baseline__year 
        assert obj_dict['activity'].result__indicator__baseline__value == 'fixture_result__indicator__baseline__value', obj_dict['activity'].result__indicator__baseline__value 
        assert obj_dict['activity'].result__indicator__baseline__comment__text == 'fixture_result__indicator__baseline__comment__text', obj_dict['activity'].result__indicator__baseline__comment__text 
        assert obj_dict['activity'].result__indicator__baseline__comment__lang == 'fixture_result__indicator__baseline__comment__lang', obj_dict['activity'].result__indicator__baseline__comment__lang 
        assert obj_dict['activity'].result__indicator__period__period_start__text == 'fixture_result__indicator__period__period_start__text', obj_dict['activity'].result__indicator__period__period_start__text 
        assert obj_dict['activity'].result__indicator__period__period_start__iso_date == 'fixture_result__indicator__period__period_start__iso_date', obj_dict['activity'].result__indicator__period__period_start__iso_date 
        assert obj_dict['activity'].result__indicator__period__period_end__text == 'fixture_result__indicator__period__period_end__text', obj_dict['activity'].result__indicator__period__period_end__text 
        assert obj_dict['activity'].result__indicator__period__period_end__iso_date == 'fixture_result__indicator__period__period_end__iso_date', obj_dict['activity'].result__indicator__period__period_end__iso_date 
        assert obj_dict['activity'].result__indicator__period__target__value == 'fixture_result__indicator__period__target__value', obj_dict['activity'].result__indicator__period__target__value 
        assert obj_dict['activity'].result__indicator__period__target__comment__text == 'fixture_result__indicator__period__target__comment__text', obj_dict['activity'].result__indicator__period__target__comment__text 
        assert obj_dict['activity'].result__indicator__period__target__comment__lang == 'fixture_result__indicator__period__target__comment__lang', obj_dict['activity'].result__indicator__period__target__comment__lang 
        assert obj_dict['activity'].result__indicator__period__actual__value == 'fixture_result__indicator__period__actual__value', obj_dict['activity'].result__indicator__period__actual__value 
        assert obj_dict['activity'].result__indicator__period__actual__comment__text == 'fixture_result__indicator__period__actual__comment__text', obj_dict['activity'].result__indicator__period__actual__comment__text 
        assert obj_dict['activity'].result__indicator__period__actual__comment__lang == 'fixture_result__indicator__period__actual__comment__lang', obj_dict['activity'].result__indicator__period__actual__comment__lang 
        assert obj_dict['activity'].conditions__attached == True, obj_dict['activity'].conditions__attached 
        assert obj_dict['activity'].conditions__condition__text == 'fixture_conditions__condition__text', obj_dict['activity'].conditions__condition__text 
        assert obj_dict['activity'].conditions__condition__type == 'fixture_conditions__condition__type', obj_dict['activity'].conditions__condition__type 
        assert obj_dict['activity'].budget__type == 'fixture_budget__type', obj_dict['activity'].budget__type 
        assert obj_dict['activity'].budget__period_start__text == 'fixture_budget__period_start__text', obj_dict['activity'].budget__period_start__text 
        assert obj_dict['activity'].budget__period_start__iso_date == 'fixture_budget__period_start__iso_date', obj_dict['activity'].budget__period_start__iso_date 
        assert obj_dict['activity'].budget__period_end__text == 'fixture_budget__period_end__text', obj_dict['activity'].budget__period_end__text 
        assert obj_dict['activity'].budget__period_end__iso_date == 'fixture_budget__period_end__iso_date', obj_dict['activity'].budget__period_end__iso_date 
        assert obj_dict['activity'].budget__value__text == 999009.09, obj_dict['activity'].budget__value__text 
        assert obj_dict['activity'].budget__value__currency == 'fixture_budget__value__currency', obj_dict['activity'].budget__value__currency 
        assert obj_dict['activity'].budget__value__value_date == 'fixture_budget__value__value_date', obj_dict['activity'].budget__value__value_date 
        assert obj_dict['activity'].planned_disbursement__updated == 'fixture_planned_disbursement__updated', obj_dict['activity'].planned_disbursement__updated 
        assert obj_dict['activity'].planned_disbursement__period_start__text == 'fixture_planned_disbursement__period_start__text', obj_dict['activity'].planned_disbursement__period_start__text 
        assert obj_dict['activity'].planned_disbursement__period_start__iso_date == 'fixture_planned_disbursement__period_start__iso_date', obj_dict['activity'].planned_disbursement__period_start__iso_date 
        assert obj_dict['activity'].planned_disbursement__period_end__text == 'fixture_planned_disbursement__period_end__text', obj_dict['activity'].planned_disbursement__period_end__text 
        assert obj_dict['activity'].planned_disbursement__period_end__iso_date == 'fixture_planned_disbursement__period_end__iso_date', obj_dict['activity'].planned_disbursement__period_end__iso_date 
        assert obj_dict['activity'].planned_disbursement__value__text == 999010.1, obj_dict['activity'].planned_disbursement__value__text 
        assert obj_dict['activity'].planned_disbursement__value__currency == 'fixture_planned_disbursement__value__currency', obj_dict['activity'].planned_disbursement__value__currency 
        assert obj_dict['activity'].planned_disbursement__value__value_date == 'fixture_planned_disbursement__value__value_date', obj_dict['activity'].planned_disbursement__value__value_date 
        assert obj_dict['activity'].related_activity__text == 'fixture_related_activity__text', obj_dict['activity'].related_activity__text 
        assert obj_dict['activity'].related_activity__ref == 'fixture_related_activity__ref', obj_dict['activity'].related_activity__ref 
        assert obj_dict['activity'].related_activity__type == 'fixture_related_activity__type', obj_dict['activity'].related_activity__type 
        assert obj_dict['activity'].related_activity__lang == 'fixture_related_activity__lang', obj_dict['activity'].related_activity__lang 
        assert obj_dict['activity'].document_link__url == 'fixture_document_link__url', obj_dict['activity'].document_link__url 
        assert obj_dict['activity'].document_link__format == 'fixture_document_link__format', obj_dict['activity'].document_link__format 
        assert obj_dict['activity'].document_link__title__text == 'fixture_document_link__title__text', obj_dict['activity'].document_link__title__text 
        assert obj_dict['activity'].document_link__title__lang == 'fixture_document_link__title__lang', obj_dict['activity'].document_link__title__lang 
        assert obj_dict['activity'].document_link__category__text == 'fixture_document_link__category__text', obj_dict['activity'].document_link__category__text 
        assert obj_dict['activity'].document_link__category__code == 'fixture_document_link__category__code', obj_dict['activity'].document_link__category__code 
        assert obj_dict['activity'].document_link__category__lang == 'fixture_document_link__category__lang', obj_dict['activity'].document_link__category__lang 
        assert obj_dict['activity'].document_link__language__text == 'fixture_document_link__language__text', obj_dict['activity'].document_link__language__text 
        assert obj_dict['activity'].document_link__language__code == 'fixture_document_link__language__code', obj_dict['activity'].document_link__language__code 
        assert obj_dict['activity'].document_link__language__lang == 'fixture_document_link__language__lang', obj_dict['activity'].document_link__language__lang 
        assert obj_dict['activity'].legacy_data__text == 'fixture_legacy_data__text', obj_dict['activity'].legacy_data__text 
        assert obj_dict['activity'].legacy_data__name == 'fixture_legacy_data__name', obj_dict['activity'].legacy_data__name 
        assert obj_dict['activity'].legacy_data__value == 'fixture_legacy_data__value', obj_dict['activity'].legacy_data__value 
        assert obj_dict['activity'].legacy_data__iati_equivalent == 'fixture_legacy_data__iati_equivalent', obj_dict['activity'].legacy_data__iati_equivalent 
        ## Assertions: Transaction object
        assert obj_dict['transaction'].ref == 'fixture_ref', obj_dict['transaction'].ref 
        assert obj_dict['transaction'].value__text == 999011.11, obj_dict['transaction'].value__text 
        assert obj_dict['transaction'].value__currency == 'fixture_value__currency', obj_dict['transaction'].value__currency 
        assert obj_dict['transaction'].value__value_date == 'fixture_value__value_date', obj_dict['transaction'].value__value_date 
        assert obj_dict['transaction'].description__text == 'fixture_description__text', obj_dict['transaction'].description__text 
        assert obj_dict['transaction'].description__lang == 'fixture_description__lang', obj_dict['transaction'].description__lang 
        assert obj_dict['transaction'].transaction_type__text == 'fixture_transaction_type__text', obj_dict['transaction'].transaction_type__text 
        assert obj_dict['transaction'].transaction_type__code == 'fixture_transaction_type__code', obj_dict['transaction'].transaction_type__code 
        assert obj_dict['transaction'].transaction_type__lang == 'fixture_transaction_type__lang', obj_dict['transaction'].transaction_type__lang 
        assert obj_dict['transaction'].provider_org__text == 'fixture_provider_org__text', obj_dict['transaction'].provider_org__text 
        assert obj_dict['transaction'].provider_org__ref == 'fixture_provider_org__ref', obj_dict['transaction'].provider_org__ref 
        assert obj_dict['transaction'].provider_org__provider_activity_id == 'fixture_provider_org__provider_activity_id', obj_dict['transaction'].provider_org__provider_activity_id 
        assert obj_dict['transaction'].receiver_org__text == 'fixture_receiver_org__text', obj_dict['transaction'].receiver_org__text 
        assert obj_dict['transaction'].receiver_org__ref == 'fixture_receiver_org__ref', obj_dict['transaction'].receiver_org__ref 
        assert obj_dict['transaction'].receiver_org__receiver_activity_id == 'fixture_receiver_org__receiver_activity_id', obj_dict['transaction'].receiver_org__receiver_activity_id 
        assert obj_dict['transaction'].transaction_date__text == 'fixture_transaction_date__text', obj_dict['transaction'].transaction_date__text 
        assert obj_dict['transaction'].transaction_date__iso_date == 'fixture_transaction_date__iso_date', obj_dict['transaction'].transaction_date__iso_date 
        assert obj_dict['transaction'].flow_type__text == 'fixture_flow_type__text', obj_dict['transaction'].flow_type__text 
        assert obj_dict['transaction'].flow_type__code == 'fixture_flow_type__code', obj_dict['transaction'].flow_type__code 
        assert obj_dict['transaction'].flow_type__lang == 'fixture_flow_type__lang', obj_dict['transaction'].flow_type__lang 
        assert obj_dict['transaction'].aid_type__text == 'fixture_aid_type__text', obj_dict['transaction'].aid_type__text 
        assert obj_dict['transaction'].aid_type__code == 'fixture_aid_type__code', obj_dict['transaction'].aid_type__code 
        assert obj_dict['transaction'].aid_type__lang == 'fixture_aid_type__lang', obj_dict['transaction'].aid_type__lang 
        assert obj_dict['transaction'].finance_type__text == 'fixture_finance_type__text', obj_dict['transaction'].finance_type__text 
        assert obj_dict['transaction'].finance_type__code == 'fixture_finance_type__code', obj_dict['transaction'].finance_type__code 
        assert obj_dict['transaction'].finance_type__lang == 'fixture_finance_type__lang', obj_dict['transaction'].finance_type__lang 
        assert obj_dict['transaction'].tied_status__text == 'fixture_tied_status__text', obj_dict['transaction'].tied_status__text 
        assert obj_dict['transaction'].tied_status__code == 'fixture_tied_status__code', obj_dict['transaction'].tied_status__code 
        assert obj_dict['transaction'].tied_status__lang == 'fixture_tied_status__lang', obj_dict['transaction'].tied_status__lang 
        assert obj_dict['transaction'].disbursement_channel__text == 'fixture_disbursement_channel__text', obj_dict['transaction'].disbursement_channel__text 
        assert obj_dict['transaction'].disbursement_channel__code == 'fixture_disbursement_channel__code', obj_dict['transaction'].disbursement_channel__code 
        assert obj_dict['transaction'].disbursement_channel__lang == 'fixture_disbursement_channel__lang', obj_dict['transaction'].disbursement_channel__lang 
        ## Assertions: Sector object
        assert obj_dict['sector'].text == 'fixture_text', obj_dict['sector'].text 
        assert obj_dict['sector'].code == 'fixture_code', obj_dict['sector'].code 
        assert obj_dict['sector'].vocabulary == 'fixture_vocabulary', obj_dict['sector'].vocabulary 
        assert obj_dict['sector'].percentage == 999012.12, obj_dict['sector'].percentage 
        assert obj_dict['sector'].lang == 'fixture_lang', obj_dict['sector'].lang 
        ## Assertions: ActivityDate object
        assert obj_dict['activitydate'].text == 'fixture_text', obj_dict['activitydate'].text 
        assert obj_dict['activitydate'].type == 'fixture_type', obj_dict['activitydate'].type 
        assert obj_dict['activitydate'].iso_date == 'fixture_iso_date', obj_dict['activitydate'].iso_date 
        assert obj_dict['activitydate'].lang == 'fixture_lang', obj_dict['activitydate'].lang 
        ## Assertions: ContactInfo object
        assert obj_dict['contactinfo'].organisation__text == 'fixture_organisation__text', obj_dict['contactinfo'].organisation__text 
        assert obj_dict['contactinfo'].person_name__text == 'fixture_person_name__text', obj_dict['contactinfo'].person_name__text 
        assert obj_dict['contactinfo'].telephone__text == 'fixture_telephone__text', obj_dict['contactinfo'].telephone__text 
        assert obj_dict['contactinfo'].email__text == 'fixture_email__text', obj_dict['contactinfo'].email__text 
        assert obj_dict['contactinfo'].mailing_address__text == 'fixture_mailing_address__text', obj_dict['contactinfo'].mailing_address__text 
        ## Assertions: ParticipatingOrg object
        assert obj_dict['participatingorg'].text == 'fixture_text', obj_dict['participatingorg'].text 
        assert obj_dict['participatingorg'].ref == 'fixture_ref', obj_dict['participatingorg'].ref 
        assert obj_dict['participatingorg'].type == 'fixture_type', obj_dict['participatingorg'].type 
        assert obj_dict['participatingorg'].role == 'fixture_role', obj_dict['participatingorg'].role 
        assert obj_dict['participatingorg'].lang == 'fixture_lang', obj_dict['participatingorg'].lang 
