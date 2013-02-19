import datetime

from . import AppTestCase
from .factories import create_activity

from iatilib.frontend import dsfilter


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
