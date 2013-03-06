import uuid

import factory

from iatilib.frontend import db
from iatilib.model import (
    Activity, ActivityDate, IndexedResource, RawXmlBlob, Sector,
    RecipientCountry, ReportingOrg, IatiIdentifier, Title, Description,
    TransactionType, Transaction, TransactionValue)


def sa_creation(model, **kw):
    instance = model(**kw)
    db.session.add(instance)
    db.session.commit()
    db.session.refresh(instance)
    return instance

factory.Factory.set_creation_function(sa_creation)


class IndexedResourceFactory(factory.Factory):
    id = factory.LazyAttribute(lambda i: uuid.uuid4().hex.decode('ascii'))
    url = u"http://test"


class RawXmlBlobFactory(factory.Factory):
    indexedresource = factory.SubFactory(IndexedResourceFactory)
    parsed = False


def create_activity(_commit=True, **args):
    # map param name to db date type col-value
    date_names = {
        "start_planned": u"start-planned",
        "end_planned": u"end-planned",
        "start_actual": u"start-actual",
        "end_actual": u"end-actual",
    }

    defaults = {
        "recipient_country__code": u"TST",
        "recipient_country__text": u"Test",
        "reporting_org__ref": u"T RO REF",
        "reporting_org__text": u"RO-TEXT",
        "iatiidentifier__text": u"iati id",
        "title__text": u"title test",
        "parent__raw_xml": u"<test />",
        "description__text": u"test desc",
        }
    data = dict(defaults, **args)

    if _commit:
        ir = IndexedResource.query.filter_by(id=u"TEST").first()
    if not _commit or not ir:
        ir = IndexedResource(id=u"TEST")

    act = Activity()
    act.reportingorg = [ReportingOrg(
        ref=data["reporting_org__ref"],
        text=data["reporting_org__text"]
        )]
    act.iatiidentifier = [IatiIdentifier(text=data["iatiidentifier__text"])]
    act.title = [Title(text=data["title__text"])]
    act.description = [Description(text=data["description__text"])]
    act.parent = RawXmlBlob(
        parent=ir,
        raw_xml=data["parent__raw_xml"]
        )

    for dparam in date_names:
        if dparam in data:
            act.date.append(ActivityDate(
                type=date_names[dparam],
                iso_date=data[dparam],
                parent_id=act.id,
            ))
    if _commit:
        db.session.add(act.parent)
        db.session.commit()
        act.parent_id = act.parent.id
        db.session.add(act)
        db.session.commit()
        db.session.refresh(act)
        db.session.add(RecipientCountryFactory.build(
            code=data["recipient_country__code"],
            text=data["recipient_country__text"],
            parent_id=act.id
            ))
        db.session.commit()
    return act


class ActivityFactory(factory.Factory):
    pass


class RecipientCountryFactory(factory.Factory):
    code = u"TST"
    text = u"test country"
    percentage = 100


class SectorFactory(factory.Factory):
    code = u"TST"


class TransactionTypeFactory(factory.Factory):
    code = u"TST"


class TransactionValueFactory(factory.Factory):
    pass


class TransactionFactory(factory.Factory):
    type = factory.SubFactory(TransactionTypeFactory)
    value = factory.SubFactory(TransactionValueFactory)
    activity = factory.SubFactory(ActivityFactory)
