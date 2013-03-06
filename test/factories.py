import datetime

import factory

from iatilib import codelists
from iatilib.frontend import db
from iatilib.model import (
    Activity, Transaction, Organisation, SectorPercentage, CountryPercentage)


def sa_creation(model, **kw):
    instance = model(**kw)
    db.session.add(instance)
    db.session.commit()
    db.session.refresh(instance)
    return instance

factory.Factory.set_creation_function(sa_creation)


def create_activity():
    raise Exception("create_activity")


class CountryPercentageFactory(factory.Factory):
    country = codelists.Country.united_states
    percentage = 0


class SectorPercentageFactory(factory.Factory):
    sector = codelists.Sector.teacher_training
    percentage = 0


class OrganisationFactory(factory.Factory):
    ref = factory.Sequence(lambda n: u'test-org-{0}'.format(n))
    name = u"test org"


class ActivityFactory(factory.Factory):
    iati_identifier = factory.Sequence(lambda n: u'test-act-{0}'.format(n))
    reporting_org = factory.SubFactory(OrganisationFactory)
    raw_xml = u"<test />"


class TransactionFactory(factory.Factory):
    activity = factory.SubFactory(ActivityFactory)
    type = codelists.TransactionType.commitment
    value_currency = codelists.Currency.us_dollar
    value_amount = 0
    value_date = datetime.date(1972, 1, 1)
