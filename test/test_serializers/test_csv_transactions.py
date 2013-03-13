import datetime
from unittest import TestCase

from . import CSVTstMixin as _CSVTstMixin
from test import factories as fac

from iatilib.frontend import serialize
from iatilib import codelists as cl


class CSVTstMixin(_CSVTstMixin):
    def serialize(self, data):
        return serialize.transaction_csv(data)


class TestCSVTransactionExample(TestCase, CSVTstMixin):
    # See example here: https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdHJIWDJtaXhBV0IwOG56N0p1TE04V2c&usp=sharing#gid=5
    def test_transaction_type(self):
        data = self.process([
            fac.TransactionFactory.build(type=cl.TransactionType.disbursement)
        ])
        self.assertField({"transaction-type": "D"}, data[0])

    def test_transaction_type2(self):
        data = self.process([
            fac.TransactionFactory.build(type=cl.TransactionType.commitment)
        ])
        self.assertField({"transaction-type": "C"}, data[0])

    def test_transaction_date(self):
        data = self.process([
            fac.TransactionFactory.build(date=datetime.date(2012, 6, 30))
        ])
        self.assertField({"transaction-date": "06/30/2012"}, data[0])

    def test_default_currency(self):
        data = self.process([
            fac.TransactionFactory.build(
                type=cl.TransactionType.disbursement,
                activity__default_currency=cl.Currency.us_dollar)
        ])
        self.assertField({"default-currency": "USD"}, data[0])

    def test_currency(self):
        # I'm assuming they want the actual currency
        data = self.process([
            fac.TransactionFactory.build(
                type=cl.TransactionType.disbursement,
                value_currency=cl.Currency.australian_dollar)
        ])
        self.assertField({"default-currency": "AUD"}, data[0])

    def test_transaction_value(self):
        data = self.process([
            fac.TransactionFactory.build(value_amount=1000)
        ])
        self.assertField({"transaction-value": "1000"}, data[0])

    def test_iati_id(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity__iati_identifier="GB-1-123")
        ])
        self.assertField({"iati-identifier": "GB-1-123"}, data[0])

    def test_title(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity__title="test title")
        ])
        self.assertField({"title": "test title"}, data[0])

    def test_description(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity__description="test desc")
        ])
        self.assertField({"description": "test desc"}, data[0])


    def test_recipient_country_code(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    recipient_country_percentages=[
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.zambia)
                    ])
            )
        ])
        self.assertField({"recipient-country-code": "ZM"}, data[0])

    def test_recipient_country(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    recipient_country_percentages=[
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.zambia),
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.australia)
                    ])
            )
        ])
        self.assertField({"recipient-country": "Zambia;Australia"}, data[0])

    def test_recipient_country_percentage(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    recipient_country_percentages=[
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.zambia,
                            percentage=20),
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.australia,
                            percentage=80)
                    ])
            )
        ])
        self.assertField({"recipient-country-percentage": "20;80"}, data[0])

    def test_recipient_country_percentage_blank(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    recipient_country_percentages=[
                        fac.CountryPercentageFactory.build(
                            country=cl.Country.zambia)
                    ])
            )
        ])
        self.assertField({"recipient-country-percentage": ""}, data[0])

    def test_sector_code(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    sector_percentages=[
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.teacher_training),
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.primary_education)
                    ])
            )
        ])
        self.assertField({"sector-code": "11130;11220"}, data[0])

    def test_sector(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    sector_percentages=[
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.teacher_training),
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.primary_education)
                    ])
            )
        ])
        self.assertField(
            {"sector": "Teacher training;Primary education"},
            data[0])

    def test_sector_blank(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    sector_percentages=[
                        fac.SectorPercentageFactory.build(sector=None),
                    ])
            )
        ])
        self.assertField({"sector": ""}, data[0])

    def test_sector_percentage(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    sector_percentages=[
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.teacher_training,
                            percentage=60),
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.primary_education,
                            percentage=40)
                    ])
            )
        ])
        self.assertField({"sector-percentage": "60;40"}, data[0])

    def test_sector_percentage_blank(self):
        data = self.process([
            fac.TransactionFactory.build(
                activity=fac.ActivityFactory.build(
                    sector_percentages=[
                        fac.SectorPercentageFactory.build(
                            sector=cl.Sector.teacher_training,
                            percentage=None),
                    ])
            )
        ])
        self.assertField({"sector-percentage": ""}, data[0])

