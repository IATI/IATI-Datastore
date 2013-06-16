import os
import datetime
import logging
import traceback
from decimal import Decimal
from functools import partial
from StringIO import StringIO

from lxml import etree as ET
from dateutil.parser import parse as parse_date
from requests.packages import charade

from . import db
from iatilib.model import (
    Activity, Budget,  CountryPercentage, Log, Transaction, Organisation,
    Participation, PolicyMarker, RegionPercentage, RelatedActivity,
    SectorPercentage)
from iatilib import codelists as cl

log = logging.getLogger("parser")

NODEFAULT = object()


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

class InvalidDateError(ParserError):
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

def xval_date(xpath, xml):
    iso_date = xval(xml, xpath + "/text()", None) or xval(xml, xpath + "/@iso-date", None)
    return iati_date(iso_date)

def iati_date(iso_date):
    if iso_date:
        try:
            return parse_date(iso_date).date()
        except ValueError:
            raise InvalidDateError('could not parse {0} as date'.format(str))
    else:
        return None 

def iati_int(str):
    return int(str.replace(",", ""))


def iati_decimal(str):
    return Decimal(str.replace(",", ""))

def parse_org(xml):
    data = {
        "ref": xval(xml, "@ref"),
        "name": xval(xml, 'text()', u""),
    }
    try:
        data['type'] = cl.OrganisationType.from_string(xval(xml, "@type"))
    except (MissingValue, ValueError):
        data['type'] = None
    return Organisation.as_unique(db.session, **data)

def reporting_org(element):
    xml = element.xpath("./reporting-org")[0]
    data = {
        "ref": xval(xml, "@ref"),
        "name": xval(xml, 'text()', u""),
    }
    try:
        data.update({
            "type": cl.OrganisationType.from_string(xval(xml, "@type"))
        })
    except MissingValue:
        data['type'] = None
    return Organisation.as_unique(db.session, **data)


def participating_orgs(xml):
    ret = []
    seen = set()
    for ele in [e for e in xml.xpath("./participating-org") if e.xpath("@ref")]:
        role = cl.OrganisationRole.from_string(xval(ele, "@role").title())
        organisation = parse_org(ele)
        if not (role, organisation.ref) in seen:
            seen.add((role, organisation.ref))
            ret.append(Participation(role=role, organisation=organisation))
    return ret


def websites(xml):
    return [xval(ele, "text()") for ele in xml.xpath("./activity-website") ]


def recipient_country_percentages(element):
    xml = element.xpath("./recipient-country")
    return [CountryPercentage(
            name=xval(ele, "text()", None),
            country=cl.Country.from_string(xval(ele, "@code")),
            )
            for ele in xml]

def recipient_region_percentages(element):
    xml = element.xpath("./recipient-region")
    return [RegionPercentage(
            name=xval(ele, "text()", None),
            region=cl.Region.from_string(xval(ele, "@code")),
            )
            for ele in xml]


        

def transactions(xml):
    def from_cl(code, codelist):
        return codelist.from_string(code) if code is not None else None

    def from_org(ele, path):
        organisation = ele.xpath(path)
        if organisation:
            try:
                return parse_org(organisation[0])
            except MissingValue:
                return None
        #return Organisation.as_unique(db.session, ref=org) if org else Nonejk

    def process(ele):
        return Transaction(
            date=iati_date(xval(ele, "transaction-date/@iso-date")),
            description=xval(ele, "description/text()", None),
            flow_type=from_cl(xval(ele, "flow-type/@code", None), cl.FlowType),
            finance_type=from_cl(xval(ele, "finance-type/@code", None),
                                 cl.FinanceType),
            aid_type=from_cl(xval(ele, "aid-type/@code", None),cl.AidType),
            tied_status=from_cl(xval(ele, "tied-status/@code", None), cl.TiedStatus),
            disbursement_channel=from_cl(xval(ele,"disbursement-channel/@code",
                                       None), cl.DisbursementChannel),

            provider_org=from_org(ele, "provider-org"),
            provider_org_text=xval(ele, "provider-org/text()", None),
            provider_org_activity_id=xval(
                                ele, "provider-org/@provider-activity-id", None),
            receiver_org=from_org(ele, "receiver-org"),
            receiver_org_text=xval(ele, "receiver-org/text()", None),
            receiver_org_activity_id=xval(
                                ele, "receiver-org/@receiver-activity-id", None),
            ref = xval(ele, "@ref", default=None),
            type=cl.TransactionType.from_string(
                                xval(ele, "transaction-type/@code")),
            value_date=iati_date(xval(ele, "value/@value-date")),
            value_amount=iati_decimal(xval(ele, "value/text()")),
            value_currency=from_cl(xval(ele, "../@default-currency", None), cl.Currency),
        )

    ret = []
    for ele in xml.xpath("./transaction"):
        try:
            ret.append(process(ele))
        except MissingValue:
            pass
    return ret


def sector_percentages(xml):
    ret = []
    for ele in xml.xpath("./sector"):
        sp = SectorPercentage()
        if ele.xpath("@code") and xval(ele, "@code") in cl.Sector.values():
            sp.sector = cl.Sector.from_string(xval(ele, "@code"))
        if ele.xpath("@vocabulary"):
            sp.vocabulary = cl.Vocabulary.from_string(xval(ele, "@vocabulary"))
        if ele.xpath("@percentage"):
            sp.percentage = int(xval(ele, "@percentage"))
        if ele.xpath("text()"):
            sp.text = xval(ele, "text()")
        if any(getattr(sp, attr) for attr in "sector vocabulary percentage".split()):
            ret.append(sp)
    return ret


def budgets(xml):
    def budget_type(ele):
        typestr = xval(ele, "@type")
        try:
            return cl.BudgetType.from_string(typestr)
        except ValueError:
            return getattr(cl.BudgetType, typestr.lower())

    def process(ele):
        return Budget(
            type=budget_type(ele),
            value_currency=cl.Currency.from_string(xval(ele, "value/@currency")),
            value_amount=iati_decimal(xval(ele, "value/text()")),
            period_start=iati_date(xval(ele, "period-start/@iso-date", None)),
            period_end=iati_date(xval(ele, "period-end/@iso-date", None)),
        )

    ret = []
    for ele in xml.xpath("./budget"):
        try:
            ret.append(process(ele))
        except MissingValue:
            pass
    return ret


def policy_markers(xml):
    element = xml.xpath("./policy-marker")
    return [ PolicyMarker(code=cl.PolicyMarker.from_string(xval(ele, "@code")),
                          text=xval(ele, "text()", None),
            ) for ele in element ]

def related_activities(xml):
    element = xml.xpath("./related-activity")
    return [ RelatedActivity(ref=xval(ele, "@ref"),
                             text=xval(ele, "text()", None))
             for ele in element ]

def hierarchy(xml):
    xml_value = xval(xml, "@hierarchy", None)
    try:
        return cl.RelatedActivityType.from_string(xml_value)
    except ValueError:
        return None

def last_updated_datetime(xml):
    xml_value = xval(xml, "@last-updated-datetime", None)
    return iati_date(xml_value)

def default_language(xml):
    xml_value = xval(xml, "@xml:lang", None)
    try:
        return cl.Language.from_string(xml_value)
    except ValueError:
        return None

def _open_resource(xml_resource):
    if isinstance(xml_resource, basestring):
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


def from_codelist(codelist, path, xml):
    element = xml.xpath(path)
    if element:
        code = xval(element[0], "@code", None)
        if code:
            try:
                return codelist.from_string(code)
            except MissingValue:
                pass

    return None

start_planned = partial(xval_date, "./activity-date[@type='start-planned']")
end_planned = partial(xval_date, "./activity-date[@type='end-planned']")
start_actual = partial(xval_date, "./activity-date[@type='start-actual']")
end_actual = partial(xval_date, "./activity-date[@type='end-actual']")

activity_status = partial(from_codelist, cl.ActivityStatus, "./activity-status")
collaboration_type = partial(from_codelist, cl.CollaborationType, "./collaboration-type")
default_finance_type = partial(from_codelist, cl.FinanceType, "./default-finance-type")
default_flow_type = partial(from_codelist, cl.FlowType, "./default-flow-type")
default_aid_type = partial(from_codelist, cl.AidType, "./default-aid-type")
default_tied_status = partial(from_codelist, cl.TiedStatus, "./default-tied-status")

def activity(xml_resource):

    xml = ET.parse(_open_resource(xml_resource))

    data = {
        "iati_identifier": xval(xml, "./iati-identifier/text()"),
        "title": xval(xml, "./title/text()", u""),
        "description": xval(xml, "./description/text()", u""),
        "raw_xml": ET.tostring(xml, encoding=unicode)
    }

    field_functions = {
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
        data[field] = function(xml)

    return Activity(**data)


def document(xml_resource, resource=None):
    xmlfile = _open_resource(xml_resource)
    try:
        for event, elem in ET.iterparse(xmlfile):
            if elem.tag == 'iati-activity':
                iati_identifier = ""
                try:
                    iati_identifier = xval(elem, "./iati-identifier/text()"),
                    yield activity(elem)
                except (MissingValue, InvalidDateError, ValueError), exe:
                    if resource:
                        resource_url = resource.url
                        dataset = resource.dataset_id
                    else:
                        resource_url = ""
                        dataset = ""

                    db.session.add(Log(
                        dataset=dataset,
                        resource=resource_url,
                        logger="activity_importer",
                        msg="Failed to import a valid activity {0}, error was: {1}".format(iati_identifier, exe),
                        level="warn",
                        trace=traceback.format_exc(),
                        created_at=datetime.datetime.now()
                    ))
                    db.session.commit()
                    log.warn("Failed to import a valid activity %r", exe)

                elem.clear()
    except ET.XMLSyntaxError, exe:
        raise XMLError()
