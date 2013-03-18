from collections import OrderedDict
import unicodecsv
from StringIO import StringIO
from operator import attrgetter


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


def sector_code(activity):
    return u";".join(
        u"%s" % sec.sector.value if sec.sector else ""
        for sec in activity.sector_percentages)


def sector_percentage(activity):
    return u";".join(
        u"%d" % sec.percentage if sec.percentage else ""
        for sec in activity.sector_percentages)


def sector(activity):
    return u";".join(
        u"%s" % sec.sector.description if sec.sector else u""
        for sec in activity.sector_percentages)


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


title = attrgetter("title")
description = attrgetter("description")
iati_identifier = attrgetter("iati_identifier")


def recipient_country_code(activity):
    return u";".join(
        rcp.country.value
        for rcp in activity.recipient_country_percentages)


def recipient_country(activity):
    return u";".join(
        rcp.country.description.title()
        for rcp in activity.recipient_country_percentages)


def recipient_country_percentage(activity):
    return u";".join(
        u"%d" % rcp.percentage if rcp.percentage else ""
        for rcp in activity.recipient_country_percentages)


def reporting_org_name(activity):
    return activity.reporting_org.name


def period_start_date(budget):
    if budget.period_start:
        return budget.period_start.strftime("%m/%d/%Y")
    return u""


def period_end_date(budget):
    if budget.period_end:
        return budget.period_end.strftime("%m/%d/%Y")
    return u""


def budget_value(budget):
    return budget.value_amount


def adapt_activity(func):
    "Adapt an accessor to work against object's activtiy attrib"
    def wrapper(obj):
        return func(obj.activity)
    return wrapper


def csv_serialize(fields, data):
    out = StringIO()
    writer = unicodecsv.writer(out, encoding='utf-8')
    writer.writerow(fields.keys())
    for obj in data:
        row = [accessor(obj) for accessor in fields.values()]
        writer.writerow(row)
    return out.getvalue()


def csv(query):
    fields = OrderedDict((
        (u"iati-identifier", iati_identifier),
        (u"reporting-org", reporting_org_name),
        (u"title", title),
        (u"description", description),
        (u"recipient-country-code", recipient_country_code),
        (u"recipient-country", recipient_country),
        (u"recipient-country-percentage", recipient_country_percentage),
        (u"sector-code", sector_code),
        (u"sector", sector),
        (u"sector-percentage", sector_percentage),
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


def csv_activity_by_country(query):
    # example of query:
    # db.session.query(Activity, CountryPercentage).join(CountryPercentage)
    # filter(Activity.iati_identifier == u'4111241002')
    def adapt(func):
        "Adapt an accessor for an activity to accept (Activity, Country)"
        # can't use functools.wraps on attrgetter
        def wrapper(args):
            a, c = args
            return func(a)
        return wrapper

    fields = OrderedDict((
        (u"iati-identifier", adapt(iati_identifier)),
        (u"recipient-country-code", lambda (a, c): c.country.value),
        (u"recipient-country", lambda (a, c): c.country.description.title()),
        (u"recipient-country-percentage", lambda (a, c): c.percentage),
        (u"title", adapt(title)),
        (u"description", adapt(description)),
        (u"sector-code", adapt(sector_code)),
        (u"sector", adapt(sector)),
        (u"sector-percentage", adapt(sector_percentage)),
        (u"currency", adapt(currency)),
        (u"total-Commitment", adapt(total("commitments"))),
        (u"total-Disbursement", adapt(total("disbursements"))),
        (u"total-Expenditure", adapt(total("expenditures"))),
        (u"total-Incoming Funds", adapt(total("incoming_funds"))),
        (u"total-Interest Repayment", adapt(total("interest_repayment"))),
        (u"total-Loan Repayment", adapt(total("loan_repayments"))),
        (u"total-Reimbursement", adapt(total("reembursements"))),
    ))

    return csv_serialize(fields, query)


def transaction_csv(query):
    adapt = adapt_activity
    fields = OrderedDict((
        (u'transaction-type', transaction_type),
        (u'transaction-date', transaction_date),
        (u"default-currency", default_currency),
        (u"transaction-value", transaction_value),
        (u"iati-identifier", adapt(iati_identifier)),
        (u"title", adapt(title)),
        (u"description", adapt(description)),
        (u"recipient-country-code", adapt(recipient_country_code)),
        (u"recipient-country", adapt(recipient_country)),
        (u"recipient-country-percentage", adapt(recipient_country_percentage)),
        (u"sector-code", adapt(sector_code)),
        (u"sector", adapt(sector)),
        (u"sector-percentage", adapt(sector_percentage)),
    ))
    return csv_serialize(fields, query)


def budget_csv(query):
    adapt = adapt_activity
    fields = OrderedDict((
        (u'budget-period-start-date', period_start_date),
        (u'budget-period-end-date', period_end_date),
        (u"budget-value", budget_value),
        (u"iati-identifier", adapt(iati_identifier)),
        (u"title", adapt(title)),
        (u"description", adapt(description)),
        (u"recipient-country-code", adapt(recipient_country_code)),
        (u"recipient-country", adapt(recipient_country)),
        (u"recipient-country-percentage", adapt(recipient_country_percentage)),
        (u"sector-code", adapt(sector_code)),
        (u"sector", adapt(sector)),
        (u"sector-percentage", adapt(sector_percentage)),
    ))
    return csv_serialize(fields, query)
