from datetime import datetime
from collections import OrderedDict
import json as jsonlib
import unicodecsv
from StringIO import StringIO
from operator import attrgetter

from sqlalchemy.orm.collections import InstrumentedList

from iatilib import model


def pure_obj(obj):
    keys = [a for a in dir(obj) if not a.startswith("_") and a != "metadata"]
    # Handle child relations
    out = {}
    for key in keys:
        val = getattr(obj, key)
        if type(val) is InstrumentedList:
            out[key] = [pure_obj(x) for x in val]
        elif type(val) in (model.TransactionValue, model.TransactionType):
            out[key] = pure_obj(val)
        elif type(val) is datetime:
            out[key] = val.isoformat()
        elif key in (
            "query", "query_class", "parent", "disbursements", "expenditures",
            "incoming_funds", "interest_repayment", "loan_repayments",
            "reembursements", "activity"
            ):
            pass
        else:
            out[key] = val
    return out


def date(date_type):
    def accessor(activity):
        dates = [d.iso_date for d in activity.date if d.type == date_type]
        if dates and dates[0]:
            return dates[0].strftime("%Y-%m-%d")
        return ""
    return accessor


def first_text(attr):
    def accessor(activity):
        val = getattr(activity, attr)
        if len(val):
            return val[0].text or ""
        return ""
    return accessor


def delim(activity_attr, child_attr):
    def accessor(activity):
        return ";".join("%s" % getattr(c, child_attr)
            for c in getattr(activity, activity_attr))
    return accessor


def total(column):
    def accessor(activity):
        if len(set(t.value.currency for t in getattr(activity, column))) > 1:
            return "!Mixed currency"
        return sum(t.value.amount for t in getattr(activity, column))
    return accessor


def currency(activity):
    if len(set(t.value.currency for t in activity.transactions)) > 1:
        return "!Mixed currency"
    curr = next(iter(set(t.value_currency for t in activity.transactions)), None)
    if curr:
        return curr.value
    return ""


def csv_serialize(fields, data):
    out = StringIO()
    writer = unicodecsv.writer(out, encoding='utf-8')
    writer.writerow(fields.keys())
    for obj in data:
        row = [accessor(obj) for accessor in fields.values()]
        writer.writerow(row)
    return out.getvalue()


def sector_code_a(activity):
    return u";".join(sp.sector.value if sp.sector else u""
                     for sp in activity.sector_percentages)


def sector_desc_a(activity):
    return u";".join(sp.sector.description if sp.sector else u""
                     for sp in activity.sector_percentages)


def csv(query):
    fields = OrderedDict((
        (u"iati-identifier", lambda a: a.iati_identifier),
        (u"reporting-org", lambda a: a.reporting_org.name),
        (u"title", attrgetter(u"title")),
        (u"description", attrgetter(u"description")),
        (u"recipient-country-code",
            lambda a: u";".join(sp.country.value for sp in a.recipient_country_percentages)),
        (u"recipient-country",
            lambda a: u";".join(sp.country.description.title() for sp in a.recipient_country_percentages)),
        (u"recipient-country-percentage",
            lambda a: u";".join(u"%s" % sp.percentage for sp in a.recipient_country_percentages)),
        (u"sector-code", sector_code_a),
        (u"sector", sector_desc_a),
        (u"sector-percentage", delim("sector_percentages", "percentage")),
        (u"currency", currency),
        (u"total-Disbursement", total("disbursements")),
        (u"total-Expenditure", total("expenditures")),
        (u"total-Incoming Funds", total("incoming_funds")),
        (u"total-Interest Repayment", total("interest_repayment")),
        (u"total-Loan Repayment", total("loan_repayments")),
        (u"total-Reimbursement", total("reembursements")),
        (u"start-planned", attrgetter(u"start_planned")),
        (u"end-planned", attrgetter(u"end_planned")),
        (u"start-actual", attrgetter(u"start_actual")),
        (u"end-actual", attrgetter(u"end_actual")),
    ))
    return csv_serialize(fields, query)


def default_currency(transaction):
    if transaction.value_currency:
        return transaction.value_currency.value
    return ""


def transaction_type(transaction):
    return transaction.type.value


def transaction_date(transaction):
    return transaction.date.strftime("%m/%d/%Y") if transaction.date else ""


def transaction_value(transaction):
    return transaction.value.amount


def iati_identifier(transaction):
    return transaction.activity.iati_identifier


def recipient_country_code(transaction):
    return u";".join(
        rcp.country.value
        for rcp in transaction.activity.recipient_country_percentages)


def recipient_country(transaction):
    return u";".join(
        rcp.country.description.title()
        for rcp in transaction.activity.recipient_country_percentages)


def recipient_country_percentage(transaction):
    return u";".join(
        u"%d" % rcp.percentage if rcp.percentage else ""
        for rcp in transaction.activity.recipient_country_percentages)


def sector_code(transaction):
    return u";".join(
        u"%s" % sec.sector.value
        for sec in transaction.activity.sector_percentages)


def sector_percentage(transaction):
    return u";".join(
        u"%d" % sec.percentage if sec.percentage else ""
        for sec in transaction.activity.sector_percentages)


def sector(transaction):
    return u";".join(
        u"%s" % sec.sector.description
        for sec in transaction.activity.sector_percentages)


def title(transaction):
    return transaction.activity.title


def description(transaction):
    return transaction.activity.description


def transaction_csv(query):
    fields = OrderedDict((
        (u'transaction-type', transaction_type),
        (u'transaction-date', transaction_date),
        (u"default-currency", default_currency),
        (u"transaction-value", transaction_value),
        (u"iati-identifier", iati_identifier),
        (u"title", title),
        (u"description", description),
        (u"recipient-country-code", recipient_country_code),
        (u"recipient-country", recipient_country),
        (u"recipient-country-percentage", recipient_country_percentage),
        (u"sector-code", sector_code),
        (u"sector", sector),
        (u"sector-percentage", sector_percentage),
    ))
    return csv_serialize(fields, query)


def xml(items):
    out = u"<result><ok>True</ok><result-activity>"
    for activity in items:
        out += activity.raw_xml
    out += u"</result-activity></result>"
    return out


def json(items):
    return jsonlib.dumps({
        "ok": True,
        "results": []
        })
