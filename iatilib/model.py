import datetime
from collections import namedtuple

import sqlalchemy as sa
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.postgresql import ARRAY


from . import db
from . import codelists


# The "Unique Object" pattern
# http://www.sqlalchemy.org/trac/wiki/UsageRecipes/UniqueObject
def _unique(session, cls, hashfunc, queryfunc, constructor, arg, kw):
    cache = getattr(session, '_unique_cache', None)
    if cache is None:
        session._unique_cache = cache = {}

    key = (cls, hashfunc(*arg, **kw))
    if key in cache:
        return cache[key]
    else:
        with session.no_autoflush:
            q = session.query(cls)
            q = queryfunc(q, *arg, **kw)
            obj = q.first()
            if not obj:
                obj = constructor(*arg, **kw)
                session.add(obj)
        cache[key] = obj
        return obj


class UniqueMixin(object):
    @classmethod
    def unique_hash(cls, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def unique_filter(cls, query, *arg, **kw):
        raise NotImplementedError()

    @classmethod
    def as_unique(cls, session, *arg, **kw):
        return _unique(
            session,
            cls,
            cls.unique_hash,
            cls.unique_filter,
            cls,
            arg, kw
        )


class TransactionType(object):
    def __init__(self, type_code):
        self.type_code = type_code

    def __get__(self, obj, type=None):
        return [t for t in obj.transactions if t.type == self.type_code]


class Participation(db.Model):
    __tablename__ = "participation"
    activity_identifier = sa.Column(
        sa.ForeignKey("activity.iati_identifier"),
        primary_key=True)
    organisation_ref = sa.Column(
        sa.ForeignKey("organisation.ref"),
        primary_key=True)
    role = sa.Column(
        codelists.OrganisationRole.db_type(),
        primary_key=True)
    organisation = sa.orm.relationship("Organisation")


class Activity(db.Model, UniqueMixin):
    __tablename__ = "activity"
    iati_identifier = sa.Column(sa.Unicode, primary_key=True, nullable=False)
    resource_url = sa.Column(
        sa.ForeignKey("resource.url"),
        index=True,
        nullable=True)
    reporting_org_ref = sa.Column(
        sa.ForeignKey("organisation.ref"),
        nullable=False,
        index=True)
    start_planned = sa.Column(sa.Date, nullable=True)
    start_actual = sa.Column(sa.Date, nullable=True)
    end_planned = sa.Column(sa.Date, nullable=True)
    end_actual = sa.Column(sa.Date, nullable=True)
    title = sa.Column(sa.Unicode, default=u"", nullable=False)
    description = sa.Column(sa.Unicode, default=u"", nullable=False)
    default_currency = sa.Column(codelists.Currency.db_type())
    raw_xml = sa.orm.deferred(sa.Column(
        sa.UnicodeText,
        nullable=False))

    commitments = TransactionType(codelists.TransactionType.commitment)
    disbursements = TransactionType(codelists.TransactionType.disbursement)
    expenditures = TransactionType(codelists.TransactionType.expenditure)
    incoming_funds = TransactionType(codelists.TransactionType.incoming_funds)
    interest_repayment = TransactionType(codelists.TransactionType.interest_repayment)
    loan_repayments = TransactionType(codelists.TransactionType.loan_repayment)
    reembursements = TransactionType(codelists.TransactionType.reimbursement)

    reporting_org = sa.orm.relationship("Organisation", uselist=False)
    activity_websites = sa.orm.relationship("ActivityWebsite")
    websites = association_proxy(
        "activity_websites",
        "url",
        creator=lambda url: ActivityWebsite(url=url))
    participating_orgs = sa.orm.relationship("Participation")
    recipient_country_percentages = sa.orm.relationship("CountryPercentage")
    transactions = sa.orm.relationship("Transaction")
    sector_percentages = sa.orm.relationship("SectorPercentage")
    budgets = sa.orm.relationship("Budget")

    @classmethod
    def unique_hash(cls, iati_identifier, **kw):
        return iati_identifier

    @classmethod
    def unique_filter(cls, query, iati_identifier, **kw):
        return query.filter(cls.iati_identifier == iati_identifier)


class Organisation(db.Model, UniqueMixin):
    __tablename__ = "organisation"
    ref = sa.Column(sa.Unicode, primary_key=True, nullable=False)
    name = sa.Column(sa.Unicode, default=u"", nullable=False)

    @classmethod
    def unique_hash(cls, ref):
        return ref

    @classmethod
    def unique_filter(cls, query, ref):
        return query.filter(cls.ref == ref)

    def __repr__(self):
        return "Organisation(ref=%r)" % self.ref

    def __unicode__(self):
        return u"Organisation ref='%s'" % self.ref


class ActivityWebsite(db.Model):
    __tablename__ = "website"
    id = sa.Column(
        sa.Integer,
        primary_key=True)
    activity_id = sa.Column(
        sa.ForeignKey("activity.iati_identifier"),
        nullable=False,
        index=True)
    url = sa.Column(sa.Unicode)
    activity = sa.orm.relationship("Activity")


class CountryPercentage(db.Model):
    __tablename__ = "country_percentage"
    id = sa.Column(sa.Integer, primary_key=True)
    activity_id = sa.Column(
        sa.ForeignKey("activity.iati_identifier"),
        nullable=False,
        index=True)
    country = sa.Column(
        codelists.Country.db_type(),
        nullable=False,
        index=True)
    percentage = sa.Column(sa.Integer, nullable=True)


class TransactionValue(namedtuple("TransactionValue", "date amount currency")):
    def __composite_values__(self):
        return self.date, self.amount, self.currency


class Transaction(db.Model):
    __tablename__ = "transaction"
    id = sa.Column(sa.Integer, primary_key=True)
    activity_id = sa.Column(
        sa.ForeignKey("activity.iati_identifier"))
    type = sa.Column(codelists.TransactionType.db_type(), nullable=False)
    date = sa.Column(sa.Date, nullable=False)
    value_date = sa.Column(sa.Date, nullable=False)
    value_amount = sa.Column(sa.BigInteger, nullable=False)
    value_currency = sa.Column(codelists.Currency.db_type(), nullable=False)
    value = sa.orm.composite(TransactionValue, value_date, value_amount, value_currency)
    activity = sa.orm.relationship("Activity")

    def __unicode__(self):
        return u"%s: %s/%s" % (
            self.activity.iati_identifier,
            self.type.description,
            self.value_amount)

    def __repr__(self):
        return u"Transaction(id=%d)" % self.id


class SectorPercentage(db.Model):
    __tablename__ = "sector_percentage"
    id = sa.Column(sa.Integer, primary_key=True)
    activity_id = sa.Column(
        sa.ForeignKey("activity.iati_identifier"))
    sector = sa.Column(codelists.Sector.db_type(), nullable=True)
    vocabulary = sa.Column(
        codelists.Vocabulary.db_type(),
        default=codelists.Vocabulary.oecd_development_assistance_committee,
        nullable=False)
    percentage = sa.Column(sa.Integer, nullable=True)
    activity = sa.orm.relationship("Activity")


class Budget(db.Model):
    __tablename__ = "budget"
    id = sa.Column(sa.Integer, primary_key=True)
    activity_id = sa.Column(
        sa.ForeignKey("activity.iati_identifier"))
    type = sa.Column(codelists.BudgetType.db_type())
    period_end = sa.Column(sa.Date, nullable=True)
    period_start = sa.Column(sa.Date, nullable=True)
    value_currency = sa.Column(codelists.Currency.db_type())
    value_amount = sa.Column(sa.Integer)
    activity = sa.orm.relationship("Activity")


class Dataset(db.Model):
    __tablename__ = "dataset"
    name = sa.Column(sa.Unicode, primary_key=True)
    first_seen = sa.Column(
        sa.DateTime,
        nullable=False,
        default=sa.func.now())
    last_seen = sa.Column(
        sa.DateTime,
        nullable=False,
        default=sa.func.now())
    last_modified = sa.Column(sa.DateTime, nullable=True)
    resources = sa.orm.relationship("Resource")
    resource_urls = association_proxy(
        "resources",
        "url",
        creator=lambda url: Resource(url=url))


class Resource(db.Model):
    __tablename__ = "resource"
    url = sa.Column(sa.Unicode, primary_key=True)
    dataset_id = sa.Column(sa.ForeignKey("dataset.name"))
    last_fetch = sa.Column(sa.DateTime)
    last_status_code = sa.Column(sa.Integer)
    last_succ = sa.Column(sa.DateTime)
    last_parsed = sa.Column(sa.DateTime)
    last_parse_error = sa.Column(sa.Unicode)
    document = sa.Column(sa.LargeBinary)
    etag = sa.Column(sa.Unicode)
    activities = sa.orm.relationship("Activity")