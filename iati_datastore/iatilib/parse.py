import os
import datetime
import logging
from StringIO import StringIO

from lxml import etree as ET
from dateutil.parser import parse as parse_date

from . import db
from iatilib.model import (
    Activity, Organisation, Participation, CountryPercentage, Transaction,
    SectorPercentage, Budget)
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


def iati_date(str):
    if str is None:
        return None
    return parse_date(str).date()


def iati_int(str):
    return int(str.replace(",", ""))


def reporting_org(xml):
    data = {
        "ref": xval(xml, "@ref"),
        "name": xval(xml, 'text()', u""),
    }
    try:
        data.update({
            "type": cl.OrganisationType.from_string(xval(xml, "@type"))
        })
    except MissingValue:
        pass
    return Organisation.as_unique(db.session, **data)


def participating_orgs(xml):
    ret = []
    seen = set()
    for ele in [e for e in xml if e.xpath("@ref")]:
        role = cl.OrganisationRole.from_string(xval(ele, "@role").title())
        organisation = Organisation.as_unique(db.session, ref=xval(ele, "@ref"))
        if not (role, organisation.ref) in seen:
            seen.add((role, organisation.ref))
            ret.append(Participation(role=role, organisation=organisation))
    return ret


def websites(xml):
    return [xval(ele, "text()") for ele in xml]


def recipient_country_percentages(xml):
    return [CountryPercentage(
            country=cl.Country.from_string(xval(ele, "@code")),
            )
            for ele in xml]


def transactions(xml):
    def currency(code):
        return cl.Currency.from_string(code) if code is not None else None

    def process(ele):
        return Transaction(
            ref = xval(ele, "@ref", default=None),
            type=cl.TransactionType.from_string(
                xval(ele, "transaction-type/@code")),
            date=iati_date(xval(ele, "transaction-date/@iso-date")),
            value_date=iati_date(xval(ele, "value/@value-date")),
            value_amount=iati_int(xval(ele, "value/text()")),
            value_currency=currency(xval(ele, "../@default-currency", None))
        )

    ret = []
    for ele in xml:
        try:
            ret.append(process(ele))
        except MissingValue:
            pass
    return ret


def sector_percentages(xml):
    ret = []
    for ele in xml:
        sp = SectorPercentage()
        if ele.xpath("@code") and xval(ele, "@code") in cl.Sector.values():
            sp.sector = cl.Sector.from_string(xval(ele, "@code"))
        if ele.xpath("@vocabulary"):
            sp.vocabulary = cl.Vocabulary.from_string(xval(ele, "@vocabulary"))
        if ele.xpath("@percentage"):
            sp.percentage = int(xval(ele, "@percentage"))
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
            value_amount=iati_int(xval(ele, "value/text()")),
            period_start=iati_date(xval(ele, "period-start/@iso-date", None)),
            period_end=iati_date(xval(ele, "period-end/@iso-date", None)),
        )

    ret = []
    for ele in xml:
        try:
            ret.append(process(ele))
        except MissingValue:
            pass
    return ret


def _open_resource(xml_resource):
    if isinstance(xml_resource, basestring):
        if os.path.exists(xml_resource):
            xmlfile = open(xml_resource)
        else:
            xmlfile = StringIO(xml_resource)
    else:
        # so it's a xml literal, probably from a test. It shouldn't be
        # big enough that a round trip through the serializer is a problem
        xmlfile = StringIO(ET.tostring(xml_resource))
    return xmlfile


def activity(xml_resource):
    xml = ET.parse(_open_resource(xml_resource))
    data = {
        "iati_identifier": xval(xml, "./iati-identifier/text()"),
        "title": xval(xml, "./title/text()", u""),
        "description": xval(xml, "./description/text()", u""),
        "reporting_org": reporting_org(xml.xpath("./reporting-org")[0]),
        "websites": websites(xml.xpath("./activity-website")),
        "participating_orgs": participating_orgs(
            xml.xpath("./participating-org")),
        "recipient_country_percentages": recipient_country_percentages(
            xml.xpath("./recipient-country")),
        "transactions": transactions(xml.xpath("./transaction")),
        "start_actual": iati_date(
            xval(xml, "./activity-date[@type='start-actual']/@iso-date", None)),
        "sector_percentages": sector_percentages(xml.xpath("./sector")),
        "budgets": budgets(xml.xpath("./budget")),
        "raw_xml": ET.tostring(xml, encoding=unicode)
    }
    return Activity(**data)


def document(xml_resource):
    xmlfile = _open_resource(xml_resource)
    try:
        for event, elem in ET.iterparse(xmlfile):
            if elem.tag == 'iati-activity':
                try:
                    yield activity(elem)
                except Exception, exe:
                    log.warn("Failed to parse activity %r", exe)
                elem.clear()
    except ET.XMLSyntaxError, exe:
        raise XMLError(exe.msg)


