import datetime
from unittest import TestCase

from . import CSVTstMixin as _CSVTstMixin
from test import factories as fac

from iatilib.frontend import serialize
from iatilib import codelists as cl


class CSVTstMixin(_CSVTstMixin):
    def serialize(self, data):
        return serialize.budget_csv(data)


class TestCSVBudgetExample(TestCase, CSVTstMixin):
    # See example here: https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdHJIWDJtaXhBV0IwOG56N0p1TE04V2c&usp=sharing#gid=5
    def test_start(self):
        data = self.process([
            fac.BudgetFactory.build(period_start=datetime.date(2012, 1, 1))
        ])
        self.assertField({"budget-period-start-date": "2012-01-01"}, data[0])

    def test_end(self):
        data = self.process([
            fac.BudgetFactory.build(period_end=datetime.date(2012, 1, 1))
        ])
        self.assertField({"budget-period-end-date": "2012-01-01"}, data[0])

    def test_value(self):
        data = self.process([
            fac.BudgetFactory.build(value_amount=100000)
        ])
        self.assertField({"budget-value": "100000"}, data[0])

    def test_iati_identifier(self):
        data = self.process([
            fac.BudgetFactory.build(
                value_amount=100000,
                activity=fac.ActivityFactory.build(iati_identifier="GB-123")
            )
        ])
        self.assertField({"iati-identifier": "GB-123"}, data[0])

    def test_title(self):
        data = self.process([
            fac.BudgetFactory.build(
                value_amount=100000,
                activity=fac.ActivityFactory.build(title="Project 123")
            )
        ])
        self.assertField({"title": "Project 123"}, data[0])

    def test_description(self):
        data = self.process([
            fac.BudgetFactory.build(
                activity=fac.ActivityFactory.build(description="Desc 123")
            )
        ])
        self.assertField({"description": "Desc 123"}, data[0])

    def test_recepient_country_code(self):
        data = self.process([
            fac.BudgetFactory.build(
                activity=fac.ActivityFactory.build(
                    recipient_country_percentages=[
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.nigeria
                            )
                    ]
                )
            )
        ])
        self.assertField({"recipient-country-code": "NG"}, data[0])

    def test_recepient_country(self):
        data = self.process([
            fac.BudgetFactory.build(
                activity=fac.ActivityFactory.build(
                    recipient_country_percentages=[
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.nigeria
                            )
                    ]
                )
            )
        ])
        self.assertField({"recipient-country": "Nigeria"}, data[0])

    def test_recepient_country_percentage(self):
        data = self.process([
            fac.BudgetFactory.build(
                activity=fac.ActivityFactory.build(
                    recipient_country_percentages=[
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.nigeria,
                            percentage=20
                            )
                    ]
                )
            )
        ])
        self.assertField({"recipient-country-percentage": "20"}, data[0])

    def test_sector_code(self):
        data = self.process([
            fac.BudgetFactory.build(
                activity=fac.ActivityFactory.build(
                    sector_percentages=[
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.teacher_training
                            )
                    ]
                )
            )
        ])
        self.assertField({"sector-code": "11130"}, data[0])

    def test_sector(self):
        data = self.process([
            fac.BudgetFactory.build(
                activity=fac.ActivityFactory.build(
                    sector_percentages=[
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.teacher_training
                            )
                    ]
                )
            )
        ])
        self.assertField({"sector": "Teacher training"}, data[0])

    def test_sector_percentage(self):
        data = self.process([
            fac.BudgetFactory.build(
                activity=fac.ActivityFactory.build(
                    sector_percentages=[
                        fac.SectorPercentageFactory.build(
                            percentage=20
                            )
                    ]
                )
            )
        ])
        self.assertField({"sector-percentage": "20"}, data[0])
