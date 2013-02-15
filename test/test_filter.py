import datetime

from . import AppTestCase

from iatilib.frontend import dsfilter, db
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


class TestFilter(AppTestCase):
    def test_by_country_name(self):
        act_in = create_activity(recipient_country__text=u"Libya")
        act_not = create_activity(recipient_country__text=u"Test")
        activities = dsfilter.activities({
            "country": u"Libya"
            })
        self.assertIn(act_in, activities.all())
        self.assertNotIn(act_not, activities.all())

    def test_by_country_code(self):
        act_in = create_activity(recipient_country__code=u"LY")
        act_not = create_activity(recipient_country__code=u"ZM")
        activities = dsfilter.activities({
            "country_code": u"LY"
            })
        self.assertIn(act_in, activities.all())
        self.assertNotIn(act_not, activities.all())

    def test_by_reporting_org_ref(self):
        act_in = create_activity(reporting_org__ref=u"AAA")
        act_not = create_activity(reporting_org__ref=u"ZZZ")
        activities = dsfilter.activities({
            "reporting_org_ref": u"AAA"
            })
        self.assertIn(act_in, activities.all())
        self.assertNotIn(act_not, activities.all())

    def test_date(self):
        act_in = create_activity(
            start_planned=datetime.date(2009, 1, 1),
            end_planned=datetime.date(2009, 12, 31)
            )
        act_not = create_activity(
            start_planned=datetime.date(2020, 1, 1),
            end_planned=datetime.date(2020, 12, 31)
            )
        activities = dsfilter.activities({
            "date": u"2009-05-09"
            })
        self.assertIn(act_in, activities.all())
        self.assertNotIn(act_not, activities.all())
