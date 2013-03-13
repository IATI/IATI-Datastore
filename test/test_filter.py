import datetime
from unittest import skip

from . import AppTestCase, factories as fac
from .factories import create_activity

from iatilib import codelists as cl
from iatilib.frontend import dsfilter


class TestFilter(AppTestCase):
    @skip("search by country name nonimpl")
    def test_by_country_name(self):
        act_in = create_activity(recipient_country__text=u"Libya")
        act_not = create_activity(recipient_country__text=u"Test")
        activities = dsfilter.activities({
            "country": u"Libya"
        })
        self.assertIn(act_in, activities.all())
        self.assertNotIn(act_not, activities.all())

    def test_by_country_code(self):
        act_in = fac.ActivityFactory.create(
            recipient_country_percentages=[
                fac.CountryPercentageFactory.build(
                    country=cl.Country.libyan_arab_jamahiriya),
            ])
        act_not = fac.ActivityFactory.create(
            recipient_country_percentages=[
                fac.CountryPercentageFactory.build(country=cl.Country.zambia),
            ])
        activities = dsfilter.activities({
            "country_code": u"LY"
        })
        self.assertIn(act_in, activities.all())
        self.assertNotIn(act_not, activities.all())

    def test_by_reporting_org_ref(self):
        act_in = fac.ActivityFactory.create(reporting_org__ref=u"AAA")
        act_not = fac.ActivityFactory.create(reporting_org__ref=u"ZZZ")
        activities = dsfilter.activities({
            "reporting_org_ref": u"AAA"
        })
        self.assertIn(act_in, activities.all())
        self.assertNotIn(act_not, activities.all())


class TestTransactionFilter(AppTestCase):
    def test_by_country_code(self):
        trans_in = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(
                recipient_country_percentages=[
                    fac.CountryPercentageFactory.build(
                        country=cl.Country.libyan_arab_jamahiriya),
                ])
        )
        trans_not = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(
                recipient_country_percentages=[
                    fac.CountryPercentageFactory.build(
                        country=cl.Country.zambia),
                ])
        )
        transactions = dsfilter.transactions({
            "country_code": u"LY"
        })
        self.assertIn(trans_in, transactions.all())
        self.assertNotIn(trans_not, transactions.all())

    def test_by_reporting_org_ref(self):
        trans_in = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(reporting_org__ref=u"AAA"))
        trans_not = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(reporting_org__ref=u"ZZZ"))
        transactions = dsfilter.transactions({
            "reporting_org_ref": u"AAA"
        })
        self.assertIn(trans_in, transactions.all())
        self.assertNotIn(trans_not, transactions.all())

    def test_by_participating_org_ref(self):
        trans_in = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(
                participating_orgs=[
                    fac.ParticipationFactory.build(
                        organisation__ref=u"AAA")
                ]))
        trans_not = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(
                participating_orgs=[
                    fac.ParticipationFactory.build(
                        organisation__ref=u"ZZZ")
                ]))

        transactions = dsfilter.transactions({
            "participating_org_ref": u"AAA"
        })
        self.assertIn(trans_in, transactions.all())
        self.assertNotIn(trans_not, transactions.all())
