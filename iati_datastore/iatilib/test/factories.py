import datetime

import factory

from iatilib import codelists
from iatilib.frontend import db
from iatilib.model import (
    Activity, Transaction, Organisation, SectorPercentage, CountryPercentage,
    Participation, Budget, Resource, RegionPercentage
)


def sa_creation(model, **kw):
    instance = model(**kw)
    db.session.add(instance)
    db.session.commit()
    db.session.refresh(instance)
    return instance

factory.Factory.set_creation_function(sa_creation)


def create_activity():
    raise Exception("create_activity")


class ResourceFactory(factory.Factory):
    url = u"http://test.com"


class CountryPercentageFactory(factory.Factory):
    country = codelists.Country.united_states
    percentage = 0


class RegionPercentageFactory(factory.Factory):
    region = codelists.Region.europe_regional
    percentage = 0


class SectorPercentageFactory(factory.Factory):
    sector = codelists.Sector.teacher_training
    percentage = 0


class OrganisationFactory(factory.Factory):
    ref = factory.Sequence(lambda n: u'test-org-{0}'.format(n))
    name = u"test org"


class ParticipationFactory(factory.Factory):
    organisation = factory.SubFactory(OrganisationFactory)
    role = codelists.OrganisationRole.funding


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
    date = datetime.date(1973, 2, 2)

class BudgetFactory(factory.Factory):
    activity = factory.SubFactory(ActivityFactory)
    type = codelists.BudgetType.original
    value_amount = 0
