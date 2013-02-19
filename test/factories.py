from iatilib.frontend import db
from iatilib.model import (
    Activity, ActivityDate, IndexedResource, RawXmlBlob,
    RecipientCountry, ReportingOrg, IatiIdentifier, Title)


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
        }
    data = dict(defaults, **args)

    if _commit:
        ir = IndexedResource.query.filter_by(id=u"TEST").first()
    if not _commit or not ir:
        ir = IndexedResource(id=u"TEST")
    blob = RawXmlBlob(
        parent=ir,
            raw_xml=u"<test />")

    if _commit:
        db.session.add(blob)
        db.session.commit()
        db.session.refresh(blob)

    act = Activity(parent_id=blob.id)
    act.reportingorg = [ReportingOrg(
        ref=data["reporting_org__ref"],
        text=data["reporting_org__text"]
        )]
    act.iatiidentifier = [IatiIdentifier(text=data["iatiidentifier__text"])]
    act.title = [Title(text=data["title__text"])]
    for dparam in date_names:
        if dparam in data:
            act.date.append(ActivityDate(
                type=date_names[dparam],
                iso_date=data[dparam],
                parent_id=act.id,
            ))
    if _commit:
        db.session.add(act)
        db.session.commit()
        db.session.refresh(act)
        db.session.add(RecipientCountry(
            code=data["recipient_country__code"],
            text=data["recipient_country__text"],
            parent_id=act.id
            ))
        db.session.commit()
    return act
