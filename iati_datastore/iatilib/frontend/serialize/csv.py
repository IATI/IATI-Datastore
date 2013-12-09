from collections import OrderedDict
from functools import partial
import unicodecsv

from StringIO import StringIO
from operator import attrgetter
from iatilib import codelists


def total(column):
    def accessor(activity):
        if len(set(t.value.currency for t in getattr(activity, column))) > 1:
            return "!Mixed currency"
        return sum(t.value.amount for t in getattr(activity, column) if t.value.amount)
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


def codelist_code(column_name, activity):
    column = getattr(activity, column_name)
    if column:
        return column.value
    else:
        return ""

def activity_status(activity):
    return activity.activity_status.description if activity.activity_status else ""


def collaboration_type(activity):
    return activity.collaboration_type.description if activity.collaboration_type else ""


def sector_percentage(activity):
    return u";".join(
        u"%d" % sec.percentage if sec.percentage else ""
        for sec in activity.sector_percentages)


def sector(activity):
    return u";".join(
        u"%s" % sec.sector.description if sec.sector else u""
        for sec in activity.sector_percentages)


def sector_vocabulary(activity):
    return u";".join(
        u"%s" % sec.vocabulary.description if sec.vocabulary else u""
        for sec in activity.sector_percentages)


def default_currency(transaction):
    return activity_default_currency(transaction.activity)

def transaction_type(transaction):
    return transaction.type.value


def transaction_date(transaction):
    return transaction.date.strftime("%Y-%m-%d") if transaction.date else ""


def transaction_value(transaction):
    return transaction.value.amount

def transaction_flow_type(transaction):
    return transaction.flow_type.value if transaction.flow_type else ""

def transaction_aid_type(transaction):
    return transaction.aid_type.value if transaction.aid_type else ""

def transaction_finance_type(transaction):
    return transaction.finance_type.value if transaction.finance_type else ""

def transaction_tied_status(transaction):
    return transaction.tied_status.value if transaction.tied_status else ""

def transaction_disbursement_channel(transaction):
    if transaction.disbursement_channel:
        return transaction.disbursement_channel.value 
    return ""

def transaction_org(field, transaction):
    organisation = getattr(transaction, field)
    if organisation:
        return organisation.ref
    else:
        return ""
provider_org = partial(transaction_org, 'provider_org')
receiver_org = partial(transaction_org, 'receiver_org')

title = attrgetter("title")
description = attrgetter("description")
iati_identifier = attrgetter("iati_identifier")


def recipient_country_code(activity):
    return u";".join(
        rcp.country.value if rcp.country else "none"
        for rcp in activity.recipient_country_percentages)


def recipient_country(activity):
    return u";".join(
        rcp.country.description.title() if rcp.country else ""
        for rcp in activity.recipient_country_percentages)


def recipient_country_percentage(activity):
    return u";".join(
        u"%d" % rcp.percentage if rcp.percentage else ""
        for rcp in activity.recipient_country_percentages)

def recipient_region_code(activity):
    return u";".join(
        rrp.region.value
        for rrp in activity.recipient_region_percentages)


def recipient_region(activity):
    return u";".join(
        rrp.region.description
        for rrp in activity.recipient_region_percentages)

def recipient_region_percentage(activity):
    return u";".join(
        u"%d" % rrp.percentage if rrp.percentage else ""
        for rrp in activity.recipient_region_percentages)

def reporting_org_ref(activity):
    return activity.reporting_org.ref

def reporting_org_name(activity):
    return activity.reporting_org.name

def reporting_org_type(activity):
    try:
        return activity.reporting_org.type.description
    except AttributeError:
        return ""

def participating_org(attr, role, activity):
    activity_by_role = dict(
            [(a.role, a) for a in activity.participating_orgs])

    participant = activity_by_role.get(role, "")
    if participant:
        return getattr(participant.organisation, attr)
    else:
        return ''

participating_org_name = partial(participating_org, "name")
participating_org_ref = partial(participating_org, "ref")
def participating_org_type(role, activity):
    code=  participating_org( "type", role, activity)
    if code:
        return code.description
    else:
        return ""

def period_start_date(budget):
    if budget.period_start:
        return budget.period_start.strftime("%Y-%m-%d")
    return u""


def period_end_date(budget):
    if budget.period_end:
        return budget.period_end.strftime("%Y-%m-%d")
    return u""


def budget_value(budget):
    return budget.value_amount

def value_currency(transaction):
    if transaction.value_currency:
        return transaction.value_currency.value
    else:
        return u"" 

def activity_default_currency(activity):
    if activity.default_currency:
        return activity.default_currency.value
    else:
        return u""

class FieldDict(OrderedDict):
    common_field = {
        u"iati-identifier": iati_identifier,
        u"hierarchy" :  partial(codelist_code, 'hierarchy'),
        u"last-updated-datetime": attrgetter(u'last_updated_datetime'),
        u"default-language" : partial(codelist_code, 'default_language'),
        u"reporting-org" : reporting_org_name,
        u"reporting-org-ref" : reporting_org_ref,
        u"reporting-org-type" : reporting_org_type,
        u"title": title,
        u"description": description,
        u"activity-status-code" : partial(codelist_code, "activity_status"),
        u"start-planned" : attrgetter(u"start_planned"),
        u"end-planned" : attrgetter(u"end_planned"),
        u"start-actual" : attrgetter(u"start_actual"),
        u"end-actual" : attrgetter(u"end_actual"),
        u"participating-org (Accountable)" : partial(participating_org_name,
                                codelists.OrganisationRole.accountable),
        u"participating-org-ref (Accountable)" : partial(participating_org_ref,
                                codelists.OrganisationRole.accountable),
        u"participating-org-type (Accountable)" : partial(participating_org_type,
                                codelists.OrganisationRole.accountable),
        u"participating-org (Funding)" : partial(participating_org_name,
                                codelists.OrganisationRole.funding),
        u"participating-org-ref (Funding)" : partial(participating_org_ref,
                                codelists.OrganisationRole.funding),
        u"participating-org-type (Funding)" : partial(participating_org_type,
                                codelists.OrganisationRole.funding),
        u"participating-org (Extending)" : partial(participating_org_name,
                                codelists.OrganisationRole.extending),
        u"participating-org-ref (Extending)" : partial(participating_org_ref,
                                codelists.OrganisationRole.extending),
        u"participating-org-type (Extending)" : partial(participating_org_type,
                                codelists.OrganisationRole.extending),
        u"participating-org (Implementing)" : partial(participating_org_name,
                                codelists.OrganisationRole.implementing),
        u"participating-org-ref (Implementing)" : partial(participating_org_ref,
                                codelists.OrganisationRole.implementing),
        u"participating-org-type (Implementing)" : partial(participating_org_type,
                                codelists.OrganisationRole.implementing),
        u"recipient-country-code" : recipient_country_code,
        u"recipient-country" : recipient_country,
        u"recipient-country-percentage" : recipient_country_percentage,
        u"sector-code": sector_code,
        u"sector": sector,
        u"sector-percentage": sector_percentage,
        u"sector-vocabulary": sector_vocabulary,
        u"collaboration-type-code" : partial(codelist_code, "collaboration_type"),
        u"default-finance-type-code" : partial(codelist_code,
            "default_finance_type"),
        u"default-flow-type-code" : partial(codelist_code, "default_flow_type"),
        u"default-aid-type-code" : partial(codelist_code, "default_aid_type"),
        u"default-tied-status-code" : partial(codelist_code, "default_tied_status"),
        u"recipient-country-code": recipient_country_code,
        u"recipient-country": recipient_country,
        u"recipient-country-percentage": recipient_country_percentage,
        u"recipient-region-code": recipient_region_code,
        u"recipient-region": recipient_region,
        u"recipient-region-percentage": recipient_region_percentage,
        u"default-currency": activity_default_currency,
        u"currency": currency,
        u'total-Commitment': total("commitments"),
        u"total-Disbursement": total("disbursements"),
        u"total-Expenditure": total("expenditures"),
        u"total-Incoming Funds": total("incoming_funds"),
        u"total-Interest Repayment": total("interest_repayment"),
        u"total-Loan Repayment": total("loan_repayments"),
        u"total-Reimbursement": total("reembursements"),
    }

    def __init__(self, itr, *args, **kw):
        adapt = kw.pop("adapter", lambda i: i)

        def field_for(i):
            if isinstance(i, basestring):
                cf = (i, self.common_field[i])
                return cf[0], adapt(cf[1])
            elif isinstance(i, tuple):
                return i
            else:
                raise ValueError("%s is not allowed in FieldDict" % type(i))
        super(FieldDict, self).__init__(
            (field_for(i) for i in itr),
            *args,
            **kw
        )


def identity(x):
    return x


class CSVSerializer(object):
    """
    A serializer that outputs the fields in the `fields` param.

    `fields` is a tuple which contains either strings which are
    names  of common fields or 2-tuples of (fieldname, accessor) where
    accessor is a function that will take an item from the query and
    return the field value

    `adaptor` is a function that will be composed with the accessors of
    the common fields to adapt them such that the objects for your query
    are compatible.
    """
    def __init__(self, fields, adapter=identity):
        self.fields = FieldDict(fields, adapter=adapter)

    def __call__(self, data):
        """
        Return a generator of lines of csv
        """
        def line(row):
            out = StringIO()
            writer = unicodecsv.writer(out, encoding='utf-8')
            writer.writerow(row)
            return out.getvalue().decode('utf-8')
        yield line(self.fields.keys())
        for obj in data.items:
            row = [accessor(obj) for accessor in self.fields.values()]
            yield line(row)


csv = CSVSerializer((
    "iati-identifier",
    "hierarchy",
    "last-updated-datetime",
    "default-language",
    "reporting-org",
    "reporting-org-ref",
    "reporting-org-type",
    "title",
    "description",
    "activity-status-code",
    "start-planned",
    "end-planned",
    "start-actual",
    "end-actual",
    "participating-org (Accountable)",
    "participating-org-ref (Accountable)",
    "participating-org-type (Accountable)",
    "participating-org (Funding)",
    "participating-org-ref (Funding)",
    "participating-org-type (Funding)",
    "participating-org (Extending)",
    "participating-org-ref (Extending)",
    "participating-org-type (Extending)",
    "participating-org (Implementing)",
    "participating-org-ref (Implementing)",
    "participating-org-type (Implementing)",
    "recipient-country-code",
    "recipient-country",
    "recipient-country-percentage",
    u"recipient-region-code",
    u"recipient-region",
    u"recipient-region-percentage",
    u"sector-code",
    u"sector",
    u"sector-percentage",
    u"sector-vocabulary",
    u"collaboration-type-code",
    u"default-finance-type-code",
    u"default-flow-type-code",
    u"default-aid-type-code",
    u"default-tied-status-code",
    u"default-currency",
    u"currency",
    u'total-Commitment',
    u"total-Disbursement",
    u"total-Expenditure",
    u"total-Incoming Funds",
    u"total-Interest Repayment",
    u"total-Loan Repayment",
    u"total-Reimbursement",
))


def adapt_activity(func):
    "Adapt an accessor to work against object's activtiy attrib"
    def wrapper(obj):
        return func(obj.activity)
    return wrapper


def adapt_activity_other(func):
    """
    Adapt an accessor for an activity to accept (Activity, other)

    other is Country or Sector, but that param is ignored anyway.
    """
    # can't use functools.wraps on attrgetter
    def wrapper(args):
        a, c = args
        return func(a)
    return wrapper


csv_activity_by_country = CSVSerializer((
    (u"recipient-country-code", lambda (a, c): c.country.value if c.country else ""), 
    (u"recipient-country", lambda (a, c): c.country.description.title() if c.country else ""),
    (u"recipient-country-percentage", lambda (a, c): c.percentage if c.percentage else ""),
    "iati-identifier",
    "hierarchy",
    "last-updated-datetime",
    "default-language",
    "reporting-org",
    "reporting-org-ref",
    "reporting-org-type",
    "title",
    "description",
    "activity-status-code",
    "start-planned",
    "end-planned",
    "start-actual",
    "end-actual",
    "participating-org (Accountable)",
    "participating-org-ref (Accountable)",
    "participating-org-type (Accountable)",
    "participating-org (Funding)",
    "participating-org-ref (Funding)",
    "participating-org-type (Funding)",
    "participating-org (Extending)",
    "participating-org-ref (Extending)",
    "participating-org-type (Extending)",
    "participating-org (Implementing)",
    "participating-org-ref (Implementing)",
    "participating-org-type (Implementing)",
    u"recipient-region-code",
    u"recipient-region",
    u"recipient-region-percentage",
    u"sector-code",
    u"sector",
    u"sector-percentage",
    u"sector-vocabulary",
    u"collaboration-type-code",
    u"default-finance-type-code",
    u"default-flow-type-code",
    u"default-aid-type-code",
    u"default-tied-status-code",
    u"currency",
    u'total-Commitment',
    u"total-Disbursement",
    u"total-Expenditure",
    u"total-Incoming Funds",
    u"total-Interest Repayment",
    u"total-Loan Repayment",
    u"total-Reimbursement",
), adapter=adapt_activity_other)


csv_activity_by_sector = CSVSerializer((
    (u"sector-code", lambda (t, sp): sp.sector.value if sp.sector else ""),
    (u"sector", lambda (t, sp): sp.sector.description.title() if sp.sector else ""),
    (u"sector-percentage", lambda (a, sp): sp.percentage if sp.percentage else ""),
    (u"sector-vocabulary", lambda (a, sp): sp.vocabulary.description if sp.vocabulary else ""),
    "iati-identifier",
    "hierarchy",
    "last-updated-datetime",
    "default-language",
    "reporting-org",
    "reporting-org-ref",
    "reporting-org-type",
    "title",
    "description",
    "activity-status-code",
    "start-planned",
    "end-planned",
    "start-actual",
    "end-actual",
    "participating-org (Accountable)",
    "participating-org-ref (Accountable)",
    "participating-org-type (Accountable)",
    "participating-org (Funding)",
    "participating-org-ref (Funding)",
    "participating-org-type (Funding)",
    "participating-org (Extending)",
    "participating-org-ref (Extending)",
    "participating-org-type (Extending)",
    "participating-org (Implementing)",
    "participating-org-ref (Implementing)",
    "participating-org-type (Implementing)",
    "recipient-country-code",
    "recipient-country",
    "recipient-country-percentage",
    u"recipient-region-code",
    u"recipient-region",
    u"recipient-region-percentage",
    u"collaboration-type-code",
    u"default-finance-type-code",
    u"default-flow-type-code",
    u"default-aid-type-code",
    u"default-tied-status-code",
    u"currency",
    u'total-Commitment',
    u"total-Disbursement",
    u"total-Expenditure",
    u"total-Incoming Funds",
    u"total-Interest Repayment",
    u"total-Loan Repayment",
    u"total-Reimbursement",
    ), adapter=adapt_activity_other)

common_transaction_csv = (
    (u'transaction_ref', lambda t: t.ref),
    (u'transaction_value_currency', value_currency),
    (u'transaction_value_value-date', lambda t: t.value_date),
    (u'transaction_provider-org', lambda t: t.provider_org_text),
    (u'transaction_provider-org_ref', provider_org),
    (u'transaction_provider-org_provider-activity-id',
            lambda t: t.provider_org_activity_id),
    (u'transaction_receiver-org', lambda t: t.receiver_org_text),
    (u'transaction_receiver-org_ref', receiver_org),
    (u'transaction_receiver-org_receiver-activity-id',
            lambda t: t.receiver_org_activity_id),
    (u'transaction_description', lambda t: t.description),
    (u'transaction_flow-type_code', transaction_flow_type),
    (u'transaction_finance-type_code', transaction_finance_type),
    (u'transaction_aid-type_code', transaction_aid_type),
    (u'transaction_tied-status_code', transaction_tied_status),
    (u'transaction_disbursement-channel_code',
            transaction_disbursement_channel),
    #(u'reporting-org', lambda t: t.activity.reporting_org_ref),
)

transaction_csv = CSVSerializer((
    (u'transaction-type', transaction_type),
    (u'transaction-date', transaction_date),
    (u"default-currency", default_currency),
    (u"transaction-value", transaction_value),
    ) + common_transaction_csv +
    ("iati-identifier",
    "hierarchy",
    "last-updated-datetime",
    "default-language",
    "reporting-org",
    "reporting-org-ref",
    "reporting-org-type",
    "title",
    "description",
    "activity-status-code",
    "start-planned",
    "end-planned",
    "start-actual",
    "end-actual",
    "participating-org (Accountable)",
    "participating-org-ref (Accountable)",
    "participating-org-type (Accountable)",
    "participating-org (Funding)",
    "participating-org-ref (Funding)",
    "participating-org-type (Funding)",
    "participating-org (Extending)",
    "participating-org-ref (Extending)",
    "participating-org-type (Extending)",
    "participating-org (Implementing)",
    "participating-org-ref (Implementing)",
    "participating-org-type (Implementing)",
    "recipient-country-code",
    "recipient-country",
    "recipient-country-percentage",
    u"recipient-region-code",
    u"recipient-region",
    u"recipient-region-percentage",
    u"sector-code",
    u"sector",
    u"sector-percentage",
    u"sector-vocabulary",
    u"collaboration-type-code",
    u"default-finance-type-code",
    u"default-flow-type-code",
    u"default-aid-type-code",
    u"default-tied-status-code",
    ), adapter=adapt_activity)


def trans(func):
    def wrapper(args):
        t, c = args
        return func(t)
    return wrapper


def trans_activity(func):
    def wrapper(args):
        t, c = args
        return func(t.activity)
    return wrapper


csv_transaction_by_country = CSVSerializer((
    (u"recipient-country-code", lambda (a, c): c.country.value),
    (u"recipient-country", lambda (a, c): c.country.description.title()),
    (u"recipient-country-percentage", lambda (a, c): c.percentage),
    (u'transaction-type', trans(transaction_type)),
    (u'transaction-date', trans(transaction_date)),
    (u"default-currency", trans(default_currency)),
    (u'transaction-value', trans(transaction_value)),
    ) + tuple([ (i[0], trans(i[1])) for i in common_transaction_csv ]) +
    ("iati-identifier",
    "hierarchy",
    "last-updated-datetime",
    "default-language",
    "reporting-org",
    "reporting-org-ref",
    "reporting-org-type",
    "title",
    "description",
    "activity-status-code",
    "start-planned",
    "end-planned",
    "start-actual",
    "end-actual",
    "participating-org (Accountable)",
    "participating-org-ref (Accountable)",
    "participating-org-type (Accountable)",
    "participating-org (Funding)",
    "participating-org-ref (Funding)",
    "participating-org-type (Funding)",
    "participating-org (Extending)",
    "participating-org-ref (Extending)",
    "participating-org-type (Extending)",
    "participating-org (Implementing)",
    "participating-org-ref (Implementing)",
    "participating-org-type (Implementing)",
    u"recipient-region-code",
    u"recipient-region",
    u"recipient-region-percentage",
    u"sector-code",
    u"sector",
    u"sector-percentage",
    u"sector-vocabulary",
    u"collaboration-type-code",
    u"default-finance-type-code",
    u"default-flow-type-code",
    u"default-aid-type-code",
    u"default-tied-status-code",
    ) ,
    adapter=trans_activity)


csv_transaction_by_sector = CSVSerializer((
    (u"sector-code", lambda (t, sp): sp.sector.value if sp.sector else ""),
    (u"sector", lambda (t, sp): sp.sector.description.title() if sp.sector else ""),
    (u"sector-percentage", lambda (t, sp): sp.percentage),
    (u"sector-vocabulary", lambda (a, sp): sp.vocabulary.description if sp.vocabulary else ""),
    (u'transaction-type', trans(transaction_type)),
    (u'transaction-date', trans(transaction_date)),
    (u"default-currency", trans(default_currency)),
    (u'transaction-value', trans(transaction_value)),
    ) + tuple([ (i[0], trans(i[1])) for i in common_transaction_csv ]) +
    ("iati-identifier",
    "hierarchy",
    "last-updated-datetime",
    "default-language",
    "reporting-org",
    "reporting-org-ref",
    "reporting-org-type",
    "title",
    "description",
    "activity-status-code",
    "start-planned",
    "end-planned",
    "start-actual",
    "end-actual",
    "participating-org (Accountable)",
    "participating-org-ref (Accountable)",
    "participating-org-type (Accountable)",
    "participating-org (Funding)",
    "participating-org-ref (Funding)",
    "participating-org-type (Funding)",
    "participating-org (Extending)",
    "participating-org-ref (Extending)",
    "participating-org-type (Extending)",
    "participating-org (Implementing)",
    "participating-org-ref (Implementing)",
    "participating-org-type (Implementing)",
    "recipient-country-code",
    "recipient-country",
    "recipient-country-percentage",
    u"recipient-region-code",
    u"recipient-region",
    u"recipient-region-percentage",
    u"collaboration-type-code",
    u"default-finance-type-code",
    u"default-flow-type-code",
    u"default-aid-type-code",
    u"default-tied-status-code",
    ),
    adapter=trans_activity)


budget_csv = CSVSerializer((
    (u'budget-period-start-date', period_start_date),
    (u'budget-period-end-date', period_end_date),
    (u"budget-value", budget_value),
    u"iati-identifier",
    u"title",
    u"description",
    u"recipient-country-code",
    u"recipient-country",
    u"recipient-country-percentage",
    u"sector-code",
    u"sector",
    u"sector-percentage",
), adapter=adapt_activity)


csv_budget_by_country = CSVSerializer((
    (u"recipient-country-code", lambda (b, c): c.country.value),
    (u"recipient-country", lambda (b, c): c.country.description.title()),
    (u"recipient-country-percentage", lambda (b, c): c.percentage),
    (u'budget-period-start-date', trans(period_start_date)),
    (u'budget-period-end-date', trans(period_end_date)),
    (u"budget-value", trans(budget_value)),
    u"iati-identifier",
    u"title",
    u"description",
    u"sector-code",
    u"sector",
    u"sector-percentage",
), adapter=trans_activity)


csv_budget_by_sector = CSVSerializer((
    (u"sector-code", lambda (t, sp): sp.sector.value if sp.sector else ""),
    (u"sector", lambda (t, sp): sp.sector.description.title() if sp.sector else ""),
    (u"sector-percentage", lambda (t, sp): sp.percentage),
    (u'budget-period-start-date', trans(period_start_date)),
    (u'budget-period-end-date', trans(period_end_date)),
    (u"budget-value", trans(budget_value)),
    u"iati-identifier",
    u"title",
    u"description",
), adapter=trans_activity)
