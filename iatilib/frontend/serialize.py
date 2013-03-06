from datetime import datetime
from collections import OrderedDict
import json as jsonlib
import unicodecsv
from StringIO import StringIO

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
        return sum(t.value.text for t in getattr(activity, column))
    return accessor


def currency(activity):
    if len(set(t.value.currency for t in activity.transaction)) > 1:
        return "!Mixed currency"
    return next(iter(set(t.value.currency for t in activity.transaction)), None)


def csv(query):
    fields = OrderedDict((
        (u"iati-identifier", first_text(u"iatiidentifier")),
        (u"reporting-org", first_text(u"reportingorg")),
        (u"title", first_text(u"title")),
        (u"description", first_text(u"description")),
        (u"recipient-country-code", delim("recipientcountry", "code")),
        (u"recipient-country", delim("recipientcountry", "text")),
        (u"recipient-country-percentage",
            delim("recipientcountry", "percentage")),
        (u"sector-code", delim("sector", "code")),
        (u"sector", delim("sector", "text")),
        (u"sector-percentage", delim("sector", "percentage")),
        (u"currency", currency),
        (u"total-Disbursement", total("disbursements")),
        (u"total-Expenditure", total("expenditures")),
        (u"total-Incoming Funds", total("incoming_funds")),
        (u"total-Interest Repayment", total("interest_repayment")),
        (u"total-Loan Repayment", total("loan_repayments")),
        (u"total-Reimbursement", total("reembursements")),
        (u"start-planned", date(u"start-planned")),
        (u"end-planned", date(u"end-planned")),
        (u"start-actual", date(u"start-actual")),
        (u"end-actual", date(u"end-actual")),
        ))

    out = StringIO()
    writer = unicodecsv.writer(out, encoding='utf-8')
    writer.writerow(fields.keys())
    for activity in query:
        row = [accessor(activity) for accessor in fields.values()]
        writer.writerow(row)
    return out.getvalue()


def default_currency(transaction):
    return transaction.activity.default_currency

def transaction_type(transaction):
    return "D"

def transaction_csv(query):
    fields = OrderedDict((
        (u'transaction-type', transaction_type),
        (u"default-currency", default_currency),
    ))

    out = StringIO()
    writer = unicodecsv.writer(out, encoding='utf-8')
    writer.writerow(fields.keys())
    for activity in query:
        row = [accessor(activity) for accessor in fields.values()]
        writer.writerow(row)
    return out.getvalue()


def xml(items):
    out = u"<result><ok>True</ok><result-activity>"
    for activity in items:
        out += activity.parent.raw_xml
    out += u"</result-activity></result>"
    return out


def json(items):
    return jsonlib.dumps({
        "ok": True,
        "results": [pure_obj(x) for x in items]
        })
