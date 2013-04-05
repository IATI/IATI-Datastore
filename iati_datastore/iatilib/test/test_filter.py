import datetime
from unittest import skip

from . import AppTestCase, factories as fac
from .factories import create_activity

from iatilib import codelists as cl
from iatilib.frontend import dsfilter
from iatilib.model import Activity


class TestActivityFilter(AppTestCase):
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
            "recipient-country": u"LY"
        })
        self.assertIn(act_in, activities.all())
        self.assertNotIn(act_not, activities.all())

    def test_by_reporting_org_ref(self):
        act_in = fac.ActivityFactory.create(reporting_org__ref=u"AAA")
        act_not = fac.ActivityFactory.create(reporting_org__ref=u"ZZZ")
        activities = dsfilter.activities({
            "reporting-org": u"AAA"
        })
        self.assertIn(act_in, activities.all())
        self.assertNotIn(act_not, activities.all())

    def test_by_reporting_org_type(self):
        act_in = fac.ActivityFactory.create(
            reporting_org__type=cl.OrganisationType.government)
        act_not = fac.ActivityFactory.create(
            reporting_org__type=cl.OrganisationType.foundation)
        activities = dsfilter.activities({
            "reporting-org_type": u"10"
        })
        self.assertIn(act_in, activities.all())
        self.assertNotIn(act_not, activities.all())

    def test_by_recipient_region_code(self):
        act_in = fac.ActivityFactory.create(
            recipient_region_percentages=[
                fac.RegionPercentageFactory.build(
                    region=cl.Region.africa_regional),
            ])
        act_not = fac.ActivityFactory.create(
            recipient_region_percentages=[
                fac.RegionPercentageFactory.build(
                    region=cl.Region.oceania_regional
                ),
            ])
        activities = dsfilter.activities({
            "recipient-region": u"298"
        })
        self.assertIn(act_in, activities.all())
        self.assertNotIn(act_not, activities.all())

    def test_by_sector(self):
        act_in = fac.ActivityFactory.create(
            sector_percentages=[
                fac.SectorPercentageFactory.build(
                    sector=cl.Sector.primary_education),
            ])
        act_not = fac.ActivityFactory.create(
            sector_percentages=[
                fac.SectorPercentageFactory.build(
                    sector=cl.Sector.secondary_education
                ),
            ])
        activities = dsfilter.activities({
            "sector": u"11220"
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
            "recipient-country": u"LY"
        })
        self.assertIn(trans_in, transactions.all())
        self.assertNotIn(trans_not, transactions.all())

    def test_by_reporting_org_ref(self):
        trans_in = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(reporting_org__ref=u"AAA"))
        trans_not = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(reporting_org__ref=u"ZZZ"))
        transactions = dsfilter.transactions({
            "reporting-org": u"AAA"
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
            "participating-org": u"AAA"
        })
        self.assertIn(trans_in, transactions.all())
        self.assertNotIn(trans_not, transactions.all())


class TestBudgetFilter(AppTestCase):
    def test_by_country_code(self):
        budget_in = fac.BudgetFactory.create(
            activity=fac.ActivityFactory.build(
                recipient_country_percentages=[
                    fac.CountryPercentageFactory.build(
                        country=cl.Country.libyan_arab_jamahiriya),
                ])
        )
        budget_not = fac.BudgetFactory.create(
            activity=fac.ActivityFactory.build(
                recipient_country_percentages=[
                    fac.CountryPercentageFactory.build(
                        country=cl.Country.zambia),
                ])
        )
        budgets = dsfilter.budgets({
            "recipient-country": u"LY"
        })
        self.assertIn(budget_in, budgets.all())
        self.assertNotIn(budget_not, budgets.all())

    def test_by_reporting_org_ref(self):
        budget_in = fac.BudgetFactory.create(
            activity=fac.ActivityFactory.build(reporting_org__ref=u"AAA"))
        budget_not = fac.BudgetFactory.create(
            activity=fac.ActivityFactory.build(reporting_org__ref=u"ZZZ"))
        budgets = dsfilter.budgets({
            "reporting-org": u"AAA"
        })
        self.assertIn(budget_in, budgets.all())
        self.assertNotIn(budget_not, budgets.all())

    def test_by_participating_org_ref(self):
        budget_in = fac.BudgetFactory.create(
            activity=fac.ActivityFactory.build(
                participating_orgs=[
                    fac.ParticipationFactory.build(
                        organisation__ref=u"AAA")
                ]))
        budget_not = fac.BudgetFactory.create(
            activity=fac.ActivityFactory.build(
                participating_orgs=[
                    fac.ParticipationFactory.build(
                        organisation__ref=u"ZZZ")
                ]))

        budgets = dsfilter.budgets({
            "participating-org": u"AAA"
        })
        self.assertIn(budget_in, budgets.all())
        self.assertNotIn(budget_not, budgets.all())
