from lxml import etree
import os
import sys
import traceback
from model import *
from . import log

class Parser:
    def __init__(self, url, parent_resource_guid):
        self.url = url
        self.source_name = url
        self.parent_resource_guid = parent_resource_guid
        self.objects = []

    def parse(self):
        """Read an IATI-XML file and return a set of objects."""
        # Could throw lots of errors...
        parser = etree.XMLParser(ns_clean=True, recover=True)
        doc = etree.parse(self.url, parser)
        for activity in doc.findall("iati-activity"):
            try:
                self._parse_activity(activity)
            except (ValueError,AssertionError) as e:
                log('warning','Activity skipped in: %s - %s' % (self.source_name, str(e)))
        return self.objects

    def _assert_unicode(self, _dict, tablename):
        return
        for key,value in _dict.iteritems():
            assert type(value) is not str, 'Warning: %s.%s is of type String' % (tablename,key)

    def _read_number(self, x):
        if x is None: return 0.0
        assert (type(x) is str) or (type(x) is unicode), type(x)
        x = x.replace(',','')
        return float(x)

    def _nodecpy(self, out, node, name, attrs=None, convert=unicode):
        """TODO understand & document"""
        if ((node is None) or (node.text is None)):
            return
        out[name] = convert(node.text)
        if attrs:
            for k, v in attrs.iteritems():
                out[name + '_' + v] = unicode(node.get(k))

    def _parse_transaction(self, activityiatiid,tx):
        """Read a transaction from the XML tree and generate a model of it."""
        temp = {}
        # Run a single pass of the XML tree 
        optimised = { }
        for element in tx:
            if element.tag == 'transaction-date':
                # This tag may appear multiple times?
                try:
                    # for some (WB) projects, the date is not set even though the tag exists...
                    temp['transaction_date_iso'] = self._import_date_value(element)
                except ValueError:
                    pass
            else:
                optimised[element.tag] = element
        # Turn the XML content into a data dict
        value = optimised.get('value')
        if value is not None:
            temp['value_date'] = value.get('value-date')
            temp['value_currency'] = value.get('currency')
            temp['value'] = self._read_number(value.text)
        description_tag = optimised.get('description')
        if description_tag is not None:
            temp['description'] = description_tag.text
        self._nodecpy(temp, optimised.get('activity-type'), 'transaction_type', {'code': 'code'})
        self._nodecpy(temp, optimised.get('transaction-type'), 'transaction_type', {'code': 'code'})
        self._nodecpy(temp, optimised.get('flow-type'), 'flow_type', {'code': 'code'})
        self._nodecpy(temp, optimised.get('finance-type'), 'finance_type', {'code': 'code'})
        self._nodecpy(temp, optimised.get('tied-status'), 'tied_status', {'code': 'code'})
        self._nodecpy(temp, optimised.get('aid-type'), 'aid_type', {'code':'code'})
        if not (temp.has_key('transaction_date_iso')):
            temp['transaction_date_iso'] = temp['value_date']
        self._nodecpy(temp, optimised.get('disembursement-channel'), 'disembursement_channel', {'code': 'code'})
        self._nodecpy(temp, optimised.get('provider-org'), 'provider_org', {'ref': 'ref'})
        self._nodecpy(temp, optimised.get('receiver-org'), 'receiver_org', {'ref': 'ref'})
        temp['iati_identifier'] = activityiatiid
        # Create a model of the transaction
        self._assert_unicode(temp,Transaction.__tablename__)
        return Transaction(**temp)


    def _import_date_key(self, date):
        """Read a date from the XML tree and distill it down to a date_type"""
        if date is None:
            raise ValueError('No date!!')
        key = {
            'start-actual': 'date_start_actual',
            'start-planned': 'date_start_planned',
            'end-actual': 'date_end_actual',
            'end-planned': 'date_end_planned'
        }
        date_type = date.get('type')
        if not date_type in key:
            raise ValueError('Unrecognized date type "%s".' % date_type)
        return key[date_type]


    def _import_date_value(self, date):
        """Read a date from the XML tree and distill it down to a date_value"""
        if date is None:
            raise ValueError('No date!!')
        date_iso_date = date.get('iso-date')
        if (date_iso_date is not None):
            return (date_iso_date)
        # for some (WB) projects, the date is not set even though the tag exists...
        temp = {}
        self._nodecpy(temp, date,
            'date',
            {'type': 'type', 'iso-date': 'iso-date'})
        if (temp.has_key('date')):
            return (temp['date'])
        raise ValueError('No iso_date or sub-key date defined.')


    def _parse_sector(self, activityiatiid, sector):
        """Read a sector from the XML tree and generate a model of it."""
        temp = {}
        self._nodecpy(temp, sector,
            'sector',
            {'vocabulary': 'vocabulary', 'percentage': 'percentage', 'code': 'code'})
         
        vocab = temp.get('sector_vocabulary', 'DAC')
        if not ('sector_percentage' in temp) or (temp['sector_percentage'] is None) or (temp['sector_percentage']==''):
            percentage = 100
        else:
            percentage = int( temp['sector_percentage'] )
        if not ('sector' in temp and 'sector_code' in temp):
            raise ValueError('Source file fails to declare "sector" or "sector_code" key in %s' % self.source_name)
        tsector = {
            'activity_iati_identifier': activityiatiid,
            'name': temp['sector'],
            'code': temp['sector_code'],
            'percentage': percentage,
            'vocabulary': vocab
        }
        self._assert_unicode(tsector,Sector.__tablename__)
        return Sector(**tsector)

    def _parse_relatedactivity(self, activityiatiid, ra):
        """Read a Related Activity from the XML tree and generate a model of it."""
        related_activity = {
            'activity_id': activityiatiid,
            'relref': ra.get('ref'),
            'reltype': ra.get('type')                    
            }
        self._assert_unicode(related_activity,RelatedActivity.__tablename__)
        return RelatedActivity(**related_activity)

    def _parse_activity(self, activity):
        """TODO understand & document"""
        out = {}
        optimised = { x.tag : x for x in activity }
        out['parent_resource'] = self.parent_resource_guid
        out['source_file'] = self.source_name
        out['default_currency'] = activity.get("default-currency")
        self._nodecpy(out, optimised.get('reporting-org'), 'reporting_org', {'ref': 'ref', 'type': 'type'})
        
        out['iati_identifier'] = unicode(activity.findtext('iati-identifier'))
        if activity.findtext('activity-website'):
            out['activity_website'] = activity.findtext('activity-website')
        out['title'] = activity.findtext('title')
        if activity.findtext('description'):
            out['description'] = activity.findtext('description')
        if activity.findtext('recipient-region'):
            out['recipient_region'] = activity.findtext('recipient-region')
            out['recipient_region_code'] = activity.find('recipient-region').get('code')
        self._nodecpy(out, optimised.get('recipient-country'), 'recipient_country', {'code': 'code'})
        self._nodecpy(out, optimised.get('collaboration_type'), 'collaboration_type', {'code': 'code'})
        self._nodecpy(out, optimised.get('default-flow-type'), 'flow_type', {'code': 'code'})
        self._nodecpy(out, optimised.get('default-finance-type'), 'finance_type', {'code': 'code'})
        self._nodecpy(out, optimised.get('default-tied-status'), 'tied_status', {'code': 'code'})
        self._nodecpy(out, optimised.get('default-aid-type'), 'aid_type', {'code':'code'})
        self._nodecpy(out, optimised.get('activity-status'), 'status', {'code':'code'})
        _activity_status = optimised.get('activity-status')
        assert _activity_status is not None, 'No value of "activity-status" found on this activity.'
        out['status_code'] = _activity_status.get('code')
        # 'Legacy' properties are not part of the object model
        #self._nodecpy(out, optimised.get('legacy-data'), 'legacy', {'name': 'name', 'value': 'value'})
        
        self._nodecpy(out, activity.find('participating-org[@role="Funding"]'), 'funding_org', {'ref': 'ref', 'type': 'type'})
        self._nodecpy(out, activity.find('participating-org[@role="Extending"]'), 'extending_org', {'ref': 'ref', 'type': 'type'})
        self._nodecpy(out, activity.find('participating-org[@role="Implementing"]'), 'implementing_org', {'ref': 'ref', 'type': 'type'})
       
        self._nodecpy(out, activity.find('participating-org[@role="funding"]'), 'funding_org', {'ref': 'ref', 'type': 'type'})
        self._nodecpy(out, activity.find('participating-org[@role="extending"]'), 'extending_org', {'ref': 'ref', 'type': 'type'})
        self._nodecpy(out, activity.find('participating-org[@role="implementing"]'), 'implementing_org', {'ref': 'ref', 'type': 'type'})
     
        for date in activity.findall('activity-date'):
            try:
                date_key = self._import_date_key(date)
                date_value = self._import_date_value(date)
                out[date_key] = date_value
            except ValueError:
                pass
        self._nodecpy(out, activity.find('contact-info/organisation'), 'contact_organisation', {})
        self._nodecpy(out, activity.find('contact-info/mailing-address'), 'contact_mailing_address', {})
        self._nodecpy(out, activity.find('contact-info/telephone'), 'contact_telephone', {})
        self._nodecpy(out, activity.find('contact-info/email'), 'contact_email', {})
        
        # SLIGHTLY HACKY:
        """snd_level = 0
        for policy_marker in activity.findall('policy-marker'):
            try:
                sign = int(policy_marker.get('significance'))
                if sign == 0:
                    continue
                if sign == 2:
                    snd_level += 1
                self._nodecpy(out, policy_marker,
                    'policy_marker_' + policy_marker.get('code'), 
                    {'vocabulary': 'vocabulary', 'significance': 'significance'})
            except ValueError:
                pass
        """
        for sector in activity.findall('sector'):
            try:
                sector = self._parse_sector(out['iati_identifier'],sector)
                self.objects.append(sector)
            except ValueError:
                pass
        for ra in activity.findall('related-activity'):
            try:
                rela = self._parse_relatedactivity(out['iati_identifier'],ra)
                self.objects.append(rela)
            except ValueError:
                pass
        for tx in activity.findall("transaction"):
            transaction = self._parse_transaction(out['iati_identifier'],tx)
            self.objects.append(transaction)
        self._assert_unicode(out,Activity.__tablename__)
        x = Activity(**out) 
        self.objects.append(x)
