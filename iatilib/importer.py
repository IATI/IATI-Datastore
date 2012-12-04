from lxml import etree
import os
import sys
import traceback
from model import *
from . import Session

class Importer:
    def __init__(self,log):
        self.log = log

    def read_number(self, x):
        if x is None: return 0.0
        assert type(x) is str, type(x)
        x = x.replace(',','')
        return float(x)

    def nodecpy(self, out, node, name, attrs={}, convert=unicode):
        """TODO understand & document"""
        if ((node is None) or (node.text is None)):
            return
        if node.text:
            out[name] = convert(node.text)
        for k, v in attrs.items():
            out[name + '_' + v] = node.get(k)

    def import_transaction(self, activityiatiid,tx,file_name):
        """Read a transaction from the XML tree and generate a model of it."""
        temp = {}
        value = tx.find('value')
        if value is not None:
            temp['value_date'] = value.get('value-date')
            temp['value_currency'] = value.get('currency')
            temp['value'] = self.read_number(value.text)
        if tx.findtext('description'):
            temp['description'] = tx.findtext('description')
        self.nodecpy(temp, tx.find('activity-type'), 'transaction_type', {'code': 'code'})
        self.nodecpy(temp, tx.find('transaction-type'), 'transaction_type', {'code': 'code'})
        self.nodecpy(temp, tx.find('flow-type'), 'flow_type', {'code': 'code'})
        self.nodecpy(temp, tx.find('finance-type'), 'finance_type', {'code': 'code'})
        self.nodecpy(temp, tx.find('tied-status'), 'tied_status', {'code': 'code'})
        self.nodecpy(temp, tx.find('aid-type'), 'aid_type', {'code':'code'})
        for date in tx.findall('transaction-date'):
            try:
                # for some (WB) projects, the date is not set even though the tag exists...
                temp['transaction_date_iso'] = self.import_date_value(date)
            except ValueError:
                pass
        if not (temp.has_key('transaction_date_iso')):
            temp['transaction_date_iso'] = temp['value_date']
        self.nodecpy(temp, tx.find('disembursement-channel'), 'disembursement_channel', {'code': 'code'})
        self.nodecpy(temp, tx.find('provider-org'), 'provider_org', {'ref': 'ref'})
        self.nodecpy(temp, tx.find('receiver-org'), 'receiver_org', {'ref': 'ref'})
        temp['iati_identifier'] = activityiatiid
        # Create a model of the transaction
        self.clean_object_dict(temp, Transaction, file_name)
        return Transaction(**temp)


    def import_date_key(self, date):
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


    def import_date_value(self, date):
        """Read a date from the XML tree and distill it down to a date_value"""
        if date is None:
            raise ValueError('No date!!')
        date_iso_date = date.get('iso-date')
        if (date_iso_date is not None):
            return (date_iso_date)
        # for some (WB) projects, the date is not set even though the tag exists...
        temp = {}
        self.nodecpy(temp, date,
            'date',
            {'type': 'type', 'iso-date': 'iso-date'})
        if (temp.has_key('date')):
            return (temp['date'])
        raise ValueError('No iso_date or sub-key date defined.')


    def import_sector(self, activityiatiid, sector, file_name):
        """Read a sector from the XML tree and generate a model of it."""
        temp = {}
        self.nodecpy(temp, sector,
            'sector',
            {'vocabulary': 'vocabulary', 'percentage': 'percentage', 'code': 'code'})
         
        vocab = temp.get('sector_vocabulary', 'DAC')
        if not ('sector_percentage' in temp) or (temp['sector_percentage'] is None) or (temp['sector_percentage']==''):
            percentage = 100
        else:
            percentage = int( temp['sector_percentage'] )
        if not ('sector' in temp and 'sector_code' in temp):
            raise ValueError('Source file fails to declare "sector" or "sector_code" key in %s' % file_name)
        tsector = {
            'activity_iati_identifier': activityiatiid,
            'name': temp['sector'],
            'code': temp['sector_code'],
            'percentage': percentage,
            'vocabulary': vocab
        }
        self.clean_object_dict(tsector, Sector, file_name)
        return Sector(**tsector)

    def import_relatedactivity(self, activityiatiid, ra, file_name):
        """Read a Related Activity from the XML tree and generate a model of it."""
        related_activity = {
            'activity_id': activityiatiid,
            'relref': ra.get('ref'),
            'reltype': ra.get('type')                    
            }
        self.clean_object_dict(related_activity, RelatedActivity, file_name)
        return RelatedActivity(**related_activity)

    def parse_activity(self, activity, file_name):
        """TODO understand & document"""
        out = {}
        out['source_file'] = file_name
        out['default_currency'] = activity.get("default-currency")
        self.nodecpy(out, activity.find('reporting-org'), 'reporting_org', {'ref': 'ref', 'type': 'type'})
        
        out['iati_identifier'] = activity.findtext('iati-identifier')
        if activity.findtext('activity-website'):
            out['activity_website'] = activity.findtext('activity-website')
        out['title'] = activity.findtext('title')
        if activity.findtext('description'):
            out['description'] = activity.findtext('description')
        if activity.findtext('recipient-region'):
            out['recipient_region'] = activity.findtext('recipient-region')
            out['recipient_region_code'] = activity.find('recipient-region').get('code')
        self.nodecpy(out, activity.find('recipient-country'), 'recipient_country', {'code': 'code'})
        self.nodecpy(out, activity.find('collaboration_type'), 'collaboration_type', {'code': 'code'})
        self.nodecpy(out, activity.find('default-flow-type'), 'flow_type', {'code': 'code'})
        self.nodecpy(out, activity.find('default-finance-type'), 'finance_type', {'code': 'code'})
        self.nodecpy(out, activity.find('default-tied-status'), 'tied_status', {'code': 'code'})
        self.nodecpy(out, activity.find('default-aid-type'), 'aid_type', {'code':'code'})
        self.nodecpy(out, activity.find('activity-status'), 'status', {'code':'code'})
        _activity_status = activity.find('activity-status')
        assert _activity_status is not None, 'No value of "activity-status" found on this activity.'
        out['status_code'] = _activity_status.get('code')
        self.nodecpy(out, activity.find('legacy-data'), 'legacy', {'name': 'name', 'value': 'value'})
        
        self.nodecpy(out, activity.find('participating-org[@role="Funding"]'), 'funding_org', {'ref': 'ref', 'type': 'type'})
        self.nodecpy(out, activity.find('participating-org[@role="Extending"]'), 'extending_org', {'ref': 'ref', 'type': 'type'})
        self.nodecpy(out, activity.find('participating-org[@role="Implementing"]'), 'implementing_org', {'ref': 'ref', 'type': 'type'})
       
        self.nodecpy(out, activity.find('participating-org[@role="funding"]'), 'funding_org', {'ref': 'ref', 'type': 'type'})
        self.nodecpy(out, activity.find('participating-org[@role="extending"]'), 'extending_org', {'ref': 'ref', 'type': 'type'})
        self.nodecpy(out, activity.find('participating-org[@role="implementing"]'), 'implementing_org', {'ref': 'ref', 'type': 'type'})
     
        for date in activity.findall('activity-date'):
            try:
                date_key = self.import_date_key(date)
                date_value = self.import_date_value(date)
                out[date_key] = date_value
            except ValueError:
                pass
        self.nodecpy(out, activity.find('contact-info/organisation'), 'contact_organisation', {})
        self.nodecpy(out, activity.find('contact-info/mailing-address'), 'contact_mailing_address', {})
        self.nodecpy(out, activity.find('contact-info/telephone'), 'contact_telephone', {})
        self.nodecpy(out, activity.find('contact-info/email'), 'contact_email', {})
        
        # SLIGHTLY HACKY:
        """snd_level = 0
        for policy_marker in activity.findall('policy-marker'):
            try:
                sign = int(policy_marker.get('significance'))
                if sign == 0:
                    continue
                if sign == 2:
                    snd_level += 1
                self.nodecpy(out, policy_marker,
                    'policy_marker_' + policy_marker.get('code'), 
                    {'vocabulary': 'vocabulary', 'significance': 'significance'})
            except ValueError:
                pass
        """
        for sector in activity.findall('sector'):
            try:
                sector = self.import_sector(out['iati_identifier'],sector,file_name)
                #Session.add(sector)
            except ValueError:
                pass
        for ra in activity.findall('related-activity'):
            try:
                rela = self.import_relatedactivity(out['iati_identifier'],ra,file_name)
                #Session.add(rela)
            except ValueError:
                pass
        for tx in activity.findall("transaction"):
            transaction = self.import_transaction(out['iati_identifier'],tx,file_name)
            #Session.add(transaction)
        self.clean_object_dict(out, Activity, file_name)
        x = Activity(**out) 
        #Session.add(x)

    def clean_object_dict(self, dict_, model_class, file_name):
        # Remove dictionary keys which don't appear on the model
        # Inner loop method: Try to be efficient
        table_keys = model_class.__table__.c.keys()
        delete = []
        for k,v in dict_.iteritems():
            if not k in table_keys:
                self.log.write("  Extra field in %s:\t%s %s" % (file_name, str(model_class.__name__), k))
                delete.append(k)
            elif type(v) is str:
                dict_[k] = unicode(v)
        for k in delete:
            del dict_[k]

    def load_file(self, file_name):
        """Read an IATI-XML file and write it into the database."""
        try:
            doc = etree.parse(file_name)
        except etree.XMLSyntaxError as e:
            self.log.write('Not valid XML: %s - %s' % (file_name,str(e)))
            return -1
        num_activities = 0
        for activity in doc.findall("iati-activity"):
            try:
                self.parse_activity(activity, file_name)
                num_activities += 1
            except (ValueError,AssertionError) as e:
                self.log.write_traceback()
                self.log.write('Error in file: %s - %s' % (file_name, str(e)))
        sys.stdout.flush()
        #Session.commit()
        return num_activities


    def load_directory(self, path):
        """Read a directory full of IATI-XML files and write them all to the database."""
        if not path[-1]=='/': 
            path += '/'
        listing = os.listdir(path)
        totalfiles = len(listing)
        self.log.write('Found %d files' % totalfiles)
        filecount = 0
        max_filecount = 50
        for infile in listing:
            filecount += 1
            percentage = str(round(((float(filecount)/float(totalfiles))*100),2))
            file_name = path + infile
            num_activities = self.load_file(file_name)
            status = '[skipped]' if num_activities<0 else '%d activities' % num_activities
            self.log.write('[%d/%d]\t(%s%% done)\t%s\t%s' % (filecount,totalfiles,percentage,status,file_name))

            if filecount>max_filecount: return
