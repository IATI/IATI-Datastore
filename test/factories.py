from iatilib.frontend import db
from iatilib.model import (
    Activity, ActivityDate, IndexedResource, RawXmlBlob, RecipientCountry, ReportingOrg)


def create_activity(**args):
    defaults = {
        "recipient_country__code": u"TST",
        "recipient_country__text": u"Test",
        "reporting_org__ref": u"T RO REF",
        }
    data = dict(defaults, **args)

    ir = IndexedResource.query.filter_by(id=u"TEST").first()
    if not ir:
        ir = IndexedResource(id=u"TEST")
    blob = RawXmlBlob(
        parent=ir,
            raw_xml=u"<test />")
    db.session.add(blob)
    db.session.commit()
    db.session.refresh(blob)
    act = Activity(parent_id=blob.id)
    db.session.add(act)
    db.session.commit()
    db.session.refresh(act)
    db.session.add(RecipientCountry(
        code=data["recipient_country__code"],
        text=data["recipient_country__text"],
        parent_id=act.id
        ))
    db.session.add(ReportingOrg(
        ref=data["reporting_org__ref"],
        parent_id=act.id
    ))

    # map param name to db date type col-value
    date_names = {
        "start_planned": u"start-planned",
        "end_planned": u"end-planned",
        "start_actual": u"start-actual",
        "end_actual": u"end-actual",
    }
    for dparam in date_names:
        if dparam in data:
            db.session.add(ActivityDate(
                type=date_names[dparam],
                iso_date=data[dparam],
                parent_id=act.id,
            ))
    db.session.commit()
    return act