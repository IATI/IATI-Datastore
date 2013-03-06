import datetime

from defusedxml import lxml as ET

from . import db
from iatilib.model import (
    Activity, Organisation, Participation, CountryPercentage, Transaction,
    SectorPercentage)
from iatilib import codelists as cl


def xval(ele, xpath):
    return ele.xpath(xpath)[0].decode("utf-8")


def iati_date(str):
    return datetime.datetime.strptime(str, "%Y-%m-%d").date()


def reporting_org(xml):
    data = {
        "ref": xval(xml, "@ref")
    }
    return Organisation.as_unique(db.session, **data)


def participating_orgs(xml):
    return [Participation(
            role=cl.OrganisationRole.from_string(ele.xpath("@role")[0]),
            organisation=Organisation.as_unique(db.session, ref=xval(ele, "@ref"))
            )
            for ele in xml if ele.xpath("@ref")]


def websites(xml):
    return [xval(ele, "text()") for ele in xml]


def recipient_country_percentages(xml):
    return [CountryPercentage(
            country=cl.Country.from_string(xval(ele, "@code")),
            )
            for ele in xml]


def transactions(xml):
    return [Transaction(
            type=cl.TransactionType.from_string(
                xval(ele, "transaction-type/@code")),
            date=iati_date(xval(ele, "transaction-date/@iso-date")),
            value_date=iati_date(xval(ele, "value/@value-date")),
            value_amount=int(xval(ele, "value/text()")),
            value_currency=cl.Currency.from_string(
                xval(ele, "../@default-currency"))
            ) for ele in xml]


def sector_percentages(xml):
    return [SectorPercentage(
            sector=cl.Sector.from_string(xval(ele, "@code")),
            vocabulary=cl.Vocabulary.from_string(xval(ele, "@vocabulary")),
            percentage=int(xval(ele, "@percentage")),
            )
            for ele in xml
            if ele.xpath("@code") and xval(ele, "@code") in cl.Sector.values()]


def activity(xmlstr):
    if isinstance(xmlstr, basestring):
        xml = ET.fromstring(xmlstr)
    else:
        xml = xmlstr
    data = {
        "iati_identifier": xval(xml, "./iati-identifier/text()"),
        "reporting_org": reporting_org(xml.xpath("./reporting-org")[0]),
        "websites": websites(xml.xpath("./activity-website")),
        "participating_orgs": participating_orgs(
            xml.xpath("./participating-org")),
        "recipient_country_percentages": recipient_country_percentages(
            xml.xpath("./recipient-country")),
        "transactions": transactions(xml.xpath("./transaction")),
        "start_actual": iati_date(
            xval(xml, "./activity-date[@type='start-actual']/@iso-date")),
        "sector_percentages": sector_percentages(xml.xpath("./sector")),
        "raw_xml": ET.tostring(xml, encoding=unicode)
    }
    return Activity(**data)


def document(xmlstr):
    xml = ET.fromstring(xmlstr)
    for act in xml.xpath("./iati-activity"):
        yield activity(act)
