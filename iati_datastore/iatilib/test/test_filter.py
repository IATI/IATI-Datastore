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

    def test_by_country_name(self):
        act_not = fac.ActivityFactory.create(
            recipient_country_percentages=[
                fac.CountryPercentageFactory.build(
                    name="Libyan Arab Jamahiriya",
                    country=cl.Country.libyan_arab_jamahiriya),
            ])
        act_in = fac.ActivityFactory.create(
            recipient_country_percentages=[
                fac.CountryPercentageFactory.build(
                    name="Zambia",
                    country=cl.Country.zambia
                    )
            ])
        activities = dsfilter.activities({
            "recipient-country.text": u"Zambia"
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

    def test_by_reporting_org_text(self):
        act_in = fac.ActivityFactory.create(reporting_org__ref=u"AAA", reporting_org__name="aaa")
        act_not = fac.ActivityFactory.create(reporting_org__ref=u"ZZZ", reporting_org__name="zzz")
        activities = dsfilter.activities({
            "reporting-org.text": u"aaa"
        })
        self.assertIn(act_in, activities.all())
        self.assertNotIn(act_not, activities.all())


    def test_by_reporting_org_type(self):
        act_in = fac.ActivityFactory.create(
            reporting_org__type=cl.OrganisationType.government)
        act_not = fac.ActivityFactory.create(
            reporting_org__type=cl.OrganisationType.foundation)
        activities = dsfilter.activities({
            "reporting-org.type": u"10"
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

    def test_by_recipient_region_text(self):
        act_in = fac.ActivityFactory.create(
            recipient_region_percentages=[
                fac.RegionPercentageFactory.build(
                    name="Africa",
                    region=cl.Region.africa_regional),
            ])
        act_not = fac.ActivityFactory.create(
            recipient_region_percentages=[
                fac.RegionPercentageFactory.build(
                    name="Oceania, regional",
                    region=cl.Region.oceania_regional
                ),
            ])
        activities = dsfilter.activities({
            "recipient-region.text": u"Africa"
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

    def test_by_sector_name(self):
        act_in = fac.ActivityFactory.create(
            sector_percentages=[
                fac.SectorPercentageFactory.build(
                    text="Primary",
                    sector=cl.Sector.primary_education),
            ])
        act_not = fac.ActivityFactory.create(
            sector_percentages=[
                fac.SectorPercentageFactory.build(
                    text="Secondary",
                    sector=cl.Sector.secondary_education
                ),
            ])
        activities = dsfilter.activities({
            "sector.text": u"Primary"
        })
        self.assertIn(act_in, activities.all())
        self.assertNotIn(act_not, activities.all())

    def test_transaction_ref(self):
        trans_in = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(),
            ref="12345"
        )
        trans_not = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(),
            ref="0123"
        )
        activity = dsfilter.activities({
            "transaction_ref": u"12345"
        })
        
        self.assertIn(trans_in.activity, activity.all())
        self.assertNotIn(trans_not.activity, activity.all())


    def test_provider_org(self):
        org_in=fac.OrganisationFactory.build(
            ref="GB-1",
            name="an org",
        )
        org_out=fac.OrganisationFactory.build(
            ref="GB-2",
            name="another org",
        )
        trans_in = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(),
            provider_org=org_in
        )
        trans_not = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(),
            provider_org=org_out,
        )
        activity = dsfilter.activities({
            "transaction_provider-org": u"GB-1"
        })
        
        self.assertIn(trans_in.activity, activity.all())
        self.assertNotIn(trans_not.activity, activity.all())

        text = dsfilter.activities({
            "transaction_provider-org_text": u"an org"
        })
        self.assertIn(trans_in.activity, text.all())
        self.assertNotIn(trans_not.activity, text.all())

    def test_receiver_org(self):
        org_in=fac.OrganisationFactory.build(
            ref="GB-1",
            name="an org",
        )
        org_out=fac.OrganisationFactory.build(
            ref="GB-2",
            name="another org",
        )
        trans_in = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(),
            receiver_org=org_in
        )
        trans_not = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(),
            receiver_org=org_out,
        )
        activity = dsfilter.activities({
            "transaction_receiver-org": u"GB-1"
        })
        
        self.assertIn(trans_in.activity, activity.all())
        self.assertNotIn(trans_not.activity, activity.all())

        text = dsfilter.activities({
            "transaction_receiver-org_text": u"an org"
        })
        self.assertIn(trans_in.activity, text.all())

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

    def test_by_participating_org_text(self):
        trans_in = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(
                participating_orgs=[
                    fac.ParticipationFactory.build(
                        organisation__ref=u"AAA", organisation__name=u"aaa")
                ]))
        trans_not = fac.TransactionFactory.create(
            activity=fac.ActivityFactory.build(
                participating_orgs=[
                    fac.ParticipationFactory.build(
                        organisation__ref=u"ZZZ", organisation__name=u"zzz")
                ]))

        transactions = dsfilter.transactions({
            "participating-org.text": u"aaa"
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
