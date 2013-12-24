import os
import datetime
import logging
from decimal import Decimal, InvalidOperation
from functools import partial
from collections import namedtuple
from StringIO import StringIO

from lxml import etree as ET
from dateutil.parser import parse as parse_date
from requests.packages import charade

from . import db
from iatilib.model import (
    Activity, Budget, CountryPercentage, Transaction, Organisation,
    Participation, PolicyMarker, RegionPercentage, RelatedActivity,
    SectorPercentage)
from iatilib import codelists as cl
from iatilib import loghandlers
from iatilib.loghandlers import DatasetMessage as _

log = logging.getLogger("parser")
sqlalchemyLog = loghandlers.SQLAlchemyHandler()
sqlalchemyLog.setLevel(logging.WARNING)
log.addHandler(sqlalchemyLog)
log.propagate = False

NODEFAULT = object()
no_resource = namedtuple('DummyResource', 'url dataset_id')('no_url', 'no_dataset')



class ParserError(Exception):
    pass

class XMLError(ParserError):
    # Errors raised by XML parser
    pass


class SpecError(ParserError):
    # Errors raised by spec violations
    pass

class MissingValue(SpecError):
    pass

class InvalidDateError(SpecError):
    pass


def xval(ele, xpath, default=NODEFAULT):
    try:
        val = ele.xpath(xpath)[0]
        if isinstance(val, str):
            return val.decode("utf-8")
        if isinstance(val, unicode):
            return val
        raise TypeError("val is not a basestring")
    except IndexError:
        if default is NODEFAULT:
            raise MissingValue("Missing %r from %s" % (xpath, ele.tag))
        return default

def xval_date(xpath, xml, resource=None):
    iso_date = xval(xml, xpath + "/text()", None) or xval(xml, xpath + "/@iso-date", None)
    return iati_date(iso_date)

def xpath_date(xpath, xml, resource=None):
    iso_date = xval(xml, xpath, default=None)
    return iati_date(iso_date)

def iati_date(iso_date):
    if iso_date:
        try:
            return parse_date(iso_date.rstrip('Z')).date()
        except ValueError:
            raise InvalidDateError('could not parse {0} as date'.format(iso_date))
    else:
        return None 

def iati_int(text):
    return int(text.replace(",", ""))


def iati_decimal(text):
    return Decimal(text.replace(",", ""))

def xpath_decimal(xpath, xml, resource=None):
    decimal_value = xval(xml, xpath, None)
    if decimal_value:
        return iati_decimal(decimal_value)
    else:
        return None

def parse_org(xml, resource=no_resource):
    data = {
        "ref": xval(xml, "@ref", u""),
        "name": xval(xml, 'text()', u""),
    }
    try:
        data['type'] = cl.OrganisationType.from_string(xval(xml, "@type"))
    except (MissingValue, ValueError):
        data['type'] = None
    return Organisation.as_unique(db.session, **data)

def reporting_org(element, resource=no_resource):
    xml = element.xpath("./reporting-org")[0]
    data = {
        "ref": xval(xml, "@ref"),
        "name": xval(xml, 'text()', u""),
    }
    try:
        data.update({
            "type": cl.OrganisationType.from_string(xval(xml, "@type"))
        })
    except (MissingValue, ValueError) as exe:
        data['type'] = None
        iati_identifier = xval(xml, "/iati-identifier/text()", 'no_identifier')
        log.warn(
            _("Failed to import a valid reporting-org.type in activity {0}, error was: {1}".format(
                iati_identifier, exe),
            logger='activity_importer', dataset=resource.dataset_id, resource=resource.url),
            exc_info=exe
        )

    return Organisation.as_unique(db.session, **data)


def participating_orgs(xml, resource=None):
    ret = []
    seen = set()
    for ele in [e for e in xml.xpath("./participating-org") if e.xpath("@ref")]:
        try:
            role = cl.OrganisationRole.from_string(xval(ele, "@role").title())
            organisation = parse_org(ele)
            if not (role, organisation.ref) in seen:
                seen.add((role, organisation.ref))
                ret.append(Participation(role=role, organisation=organisation))
        except ValueError as e:
            iati_identifier = xval(xml, "/iati-activity/iati-identifier/text()", 'no_identifier')
            log.warn(
                _("Failed to import a valid sector percentage:{0} in activity {1}, error was: {2}".format(
                    'organisation_role', iati_identifier, e),
                logger='activity_importer', dataset=resource.dataset_id, resource=resource.url),
                exc_info=e
            )
    return ret


def websites(xml, resource=None):
    return [xval(ele, "text()") for ele in xml.xpath("./activity-website") if xval(ele, "text()", None) ]

def recipient_country_percentages(element, resource=no_resource):
    xml = element.xpath("./recipient-country")
    results = []
    for ele in xml:
        name = xval(ele, "text()", None)
        code = from_codelist(cl.Country, "@code", ele, resource)
        results.append(CountryPercentage(name=name, country=code))
    return results

def recipient_region_percentages(element, resource=no_resource):
    xml = element.xpath("./recipient-region")
    results = []
    for ele in xml:
        name=xval(ele, "text()", None)
        region=from_codelist(cl.Region, "@code", ele, resource)
        if region:
            results.append(RegionPercentage(name=name, region=region))
    return results

def currency(path, xml, resource=None):
    code = xval(xml, path, None)
    if code:
        return cl.Currency.from_string(code)
    else:
        return None
        

def transactions(xml, resource=no_resource):
    def from_cl(code, codelist):
        return codelist.from_string(code) if code is not None else None

    def from_org(path, ele, resource=None):
        organisation = ele.xpath(path)
        if organisation:
            return parse_org(organisation[0])
        #return Organisation.as_unique(db.session, ref=org) if org else Nonejk

    def process(ele):
        data = {
            'description' : xval(ele, "description/text()", None),
            'provider_org_text' : xval(ele, "provider-org/text()", None),
            'provider_org_activity_id' : xval(
                                ele, "provider-org/@provider-activity-id", None),
            'receiver_org_text' : xval(ele, "receiver-org/text()", None),
            'receiver_org_activity_id' : xval(ele, "receiver-org/@receiver-activity-id", None),
            'ref' : xval(ele, "@ref", None),
        }

        field_functions = {
            'date' : partial(xpath_date, "transaction-date/@iso-date"),
            'flow_type' : partial(from_codelist, cl.FlowType, "./flow-type/@code"),
            'finance_type' : partial(from_codelist, cl.FinanceType, "./finance-type/@code"),
            'aid_type' : partial(from_codelist, cl.AidType, "./aid-type/@code"),
            'tied_status' : partial(from_codelist, cl.TiedStatus, "./tied-status/@code"),
            'disbursement_channel' : partial(from_codelist, cl.DisbursementChannel, "./disbursement-channel/@code"),
            'provider_org' : partial(from_org, "./provider-org"),
            'receiver_org' : partial(from_org, "./receiver-org"),
            'type' : partial(from_codelist, cl.TransactionType, "./transaction-type/@code"),
            'value_currency' : partial(currency, "value/@currency"),
            'value_date' : partial(xpath_date, "value/@value-date"),
            'value_amount' : partial(xpath_decimal, "value/text()"),
        }

        for field, function in field_functions.items():
            try:
                data[field] = function(ele, resource)
            except (MissingValue, InvalidDateError, ValueError, InvalidOperation), exe:
                data[field] = None
                iati_identifier = xval(xml, "/iati-activity/iati-identifier/text()", 'no_identifier')
                log.warn(
                    _("Failed to import a valid {0} in activity {1}, error was: {2}".format(
                        field, iati_identifier, exe),
                    logger='activity_importer', dataset=resource.dataset_id, resource=resource.url),
                    exc_info=exe
                )
        
        return Transaction(**data)

    ret = []
    for ele in xml.xpath("./transaction"):
        try:
            ret.append(process(ele))
        except MissingValue as exe:
            iati_identifier = xval(xml, "/iati-identifier/text()", 'no_identifier')
            log.warn(
                _("Failed to import a valid transaction in activity {0}, error was: {1}".format(
                    iati_identifier, exe),
                logger='activity_importer', dataset=resource.dataset_id, resource=resource.url),
                exc_info=exe
            )
    return ret


def sector_percentages(xml, resource=no_resource):
    ret = []
    for ele in xml.xpath("./sector"):
        sp = SectorPercentage()
        field_functions = {
            'sector' : partial(from_codelist, cl.Sector, "@code"),
            'vocabulary' : partial(from_codelist, cl.Vocabulary, "@vocabulary"),
        }

        for field, function in field_functions.items():
            try:
                setattr(sp, field, function(ele, resource))
            except (MissingValue, ValueError), exe:
                iati_identifier = xval(xml, "/iati-activity/iati-identifier/text()", 'no_identifier')
                log.warn(
                    _("Failed to import a valid {0} in activity {1}, error was: {2}".format(
                        field, iati_identifier, exe),
                    logger='activity_importer', dataset=resource.dataset_id, resource=resource.url),
                    exc_info=exe
                )
        
        if ele.xpath("@percentage"):
            try:
                sp.percentage = int(xval(ele, "@percentage"))
            except ValueError:
                sp.percentage = None
        if ele.xpath("text()"):
            sp.text = xval(ele, "text()")
        if any(getattr(sp, attr) for attr in "sector vocabulary percentage".split()):
            ret.append(sp)
    return ret


def budgets(xml, resource=no_resource):
    def budget_type(ele, resource=None):
        typestr = xval(ele, "@type", None)
        if typestr:
            try:
                return cl.BudgetType.from_string(typestr)
            except ValueError:
                return getattr(cl.BudgetType, typestr.lower())
        else:
            return None

    def process(ele):
        field_functions = {
            'type' : budget_type,
            'value_currency' : partial(currency, "value/@currency"),
            'value_amount' : partial(xpath_decimal, "value/text()"),
            'period_start' : partial(xpath_date, "period-start/@iso-date"),
            'period_end' : partial(xpath_date, "period-end/@iso-date"),
        }
        data = {}
        for field, function in field_functions.items():
            try:
                data[field] = function(ele, resource)
            except (MissingValue, InvalidDateError, ValueError, InvalidOperation) as exe:
                data[field] = None
                iati_identifier = xval(xml, "/iati-activity/iati-identifier/text()", 'no_identifier')
                log.warn(
                    _("Failed to import a valid budget:{0} in activity {1}, error was: {2}".format(
                        field, iati_identifier, exe),
                    logger='activity_importer', dataset=resource.dataset_id, resource=resource.url),
                    exc_info=exe
                )

        return Budget(**data)

    ret = []
    for ele in xml.xpath("./budget"):
        ret.append(process(ele))
    return ret


def policy_markers(xml, resource=no_resource):
    element = xml.xpath("./policy-marker")
    return [ PolicyMarker(
                code=from_codelist(cl.PolicyMarker, "@code", ele, resource),
                text=xval(ele, "text()", None),
             ) for ele in element ]

def related_activities(xml, resource=no_resource):
    element = xml.xpath("./related-activity")
    results = []
    for ele in element:
        text=xval(ele, "text()", None)
        try:
            ref = xval(ele, "@ref")
            results.append(RelatedActivity(ref=ref, text=text))
        except MissingValue as e:
            iati_identifier = xval(xml, "/iati-activity/iati-identifier/text()", 'no_identifier')
            log.warn(
                _("Failed to import a valid related-activity in activity {0}, error was: {1}".format(
                    iati_identifier, e),
                logger='activity_importer', dataset=resource.dataset_id, resource=resource.url),
                exc_info=e
            )
    return results

def hierarchy(xml, resource=None):
    xml_value = xval(xml, "@hierarchy", None)
    if xml_value:
        return cl.RelatedActivityType.from_string(xml_value)
    return None

def last_updated_datetime(xml, resource=None):
    xml_value = xval(xml, "@last-updated-datetime", None)
    return iati_date(xml_value)

def default_language(xml, resource=None):
    xml_value = xval(xml, "@xml:lang", None)
    try:
        return cl.Language.from_string(xml_value)
    except ValueError:
        return None

def _open_resource(xml_resource, detect_encoding=False):
    if isinstance(xml_resource, basestring):
        if detect_encoding:
            encoding = charade.detect(xml_resource)['encoding']
            if encoding in ('UTF-16LE', 'UTF-16BE'):
                xml_resource = xml_resource.decode('UTF-16').encode('utf-8')

        if os.path.exists(xml_resource):
            #https://bugzilla.redhat.com/show_bug.cgi?id=874546
            f = open(xml_resource)
            lines = f.read()
            xmlfile = StringIO(lines)
        else:
            xmlfile = StringIO(xml_resource)
    else:
        # so it's a xml literal, probably from a test. It shouldn't be
        # big enough that a round trip through the serializer is a problem
        xmlfile = StringIO(ET.tostring(xml_resource))
    return xmlfile


def from_codelist(codelist, path, xml, resource=no_resource):
    code = xval(xml, path, None)
    if code:
        try:
            return codelist.from_string(code)
        except (MissingValue, ValueError) as e:
            iati_identifier = xval(xml, "/iati-activity/iati-identifier/text()",
                'no_identifier')

            log.warn(
                _(("Failed to import a valid {0} in activity"
                   "{1}, error was: {2}".format(codelist, iati_identifier, e)),
                   logger='activity_importer',
                   dataset=resource.dataset_id,
                   resource=resource.url
                ),
                exc_info=e
            )
    return None

start_planned = partial(xval_date, "./activity-date[@type='start-planned']")
end_planned = partial(xval_date, "./activity-date[@type='end-planned']")
start_actual = partial(xval_date, "./activity-date[@type='start-actual']")
end_actual = partial(xval_date, "./activity-date[@type='end-actual']")

activity_status = partial(from_codelist, cl.ActivityStatus, "./activity-status/@code")
collaboration_type = partial(from_codelist, cl.CollaborationType, "./collaboration-type/@code")
default_finance_type = partial(from_codelist, cl.FinanceType, "./default-finance-type/@code")
default_flow_type = partial(from_codelist, cl.FlowType, "./default-flow-type/@code")
default_aid_type = partial(from_codelist, cl.AidType, "./default-aid-type/@code")
default_tied_status = partial(from_codelist, cl.TiedStatus, "./default-tied-status/@code")

def activity(xml_resource, resource=no_resource):

    xml = ET.parse(_open_resource(xml_resource))

    data = {
        "iati_identifier": xval(xml.getroot(), "./iati-identifier/text()"),
        "title": xval(xml, "./title/text()", u""),
        "description": xval(xml, "./description/text()", u""),
        "raw_xml": ET.tostring(xml, encoding=unicode)
    }

    field_functions = {
        "default_currency" : partial(currency, "@default-currency"),
        "hierarchy": hierarchy,
        "last_updated_datetime" : last_updated_datetime,
        "default_language" : default_language,
        "reporting_org": reporting_org,
        "websites": websites,
        "participating_orgs": participating_orgs,
        "recipient_country_percentages": recipient_country_percentages,
        "recipient_region_percentages": recipient_region_percentages,
        "transactions": transactions,
        "start_planned": start_planned,
        "end_planned": end_planned,
        "start_actual": start_actual,
        "end_actual": end_actual,
        "sector_percentages": sector_percentages,
        "budgets": budgets,
        "policy_markers": policy_markers,
        "related_activities": related_activities,
        'activity_status' : activity_status,
        'collaboration_type' : collaboration_type,
        'default_finance_type' : default_finance_type,
        'default_flow_type' : default_flow_type,
        'default_aid_type' : default_aid_type,
        'default_tied_status' : default_tied_status,
    }

    for field, function in field_functions.items():
        try:
            data[field] = function(xml, resource)
        except (MissingValue, InvalidDateError, ValueError, InvalidOperation), exe:
            data[field] = None
            log.warn(
                _("Failed to import a valid {0} in activity {1}, error was: {2}".format(
                    field, data['iati_identifier'], exe),
                logger='activity_importer', dataset=resource.dataset_id, resource=resource.url),
                exc_info=exe
            )
    return Activity(**data)


def document(xml_resource, resource=no_resource):
    try:
        return activities(_open_resource(xml_resource), resource) 
    except UnicodeDecodeError:
        return activities(_open_resource(xml_resource, detect_encoding=True), resource) 


def activities(xmlfile, resource=no_resource):
    try:
        for event, elem in ET.iterparse(xmlfile):
            if elem.tag == 'iati-activity':
                try:
                    yield activity(elem, resource=resource)
                except MissingValue, exe:
                    log.error(_("Failed to import a valid Activity error was: {0}".format(exe),
                            logger='failed_activity', dataset=resource.dataset_id, resource=resource.url),
                            exc_info=exe)
                elem.clear()
    except ET.XMLSyntaxError, exe:
        raise XMLError()

def document_metadata(xml_resource):
    version = None
    for event, elem in ET.iterparse(_open_resource(xml_resource)):
        if elem.tag == 'iati-activities':
            version = elem.get('version')
        elem.clear()
    return version
