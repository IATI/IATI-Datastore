import datetime
from unittest import TestCase

from . import CSVTstMixin as _CSVTstMixin
from test import factories as fac

from iatilib.frontend import serialize
from iatilib import codelists as cl


class CSVTstMixin(_CSVTstMixin):
    def serialize(self, data):
        return serialize.transaction_csv(data)


def example():
    activity = fac.ActivityFactory.build(
        iati_identifier="GB-1-123",
        title="Project 123",
        description="Desc project 123",
        recipient_country_percentages=[
            fac.CountryPercentageFactory.build(
                country=cl.Country.kenya,
                percentage=80,
            ),
            fac.CountryPercentageFactory.build(
                country=cl.Country.uganda,
                percentage=20,
            )
        ],
        sector_percentages=[
            fac.SectorPercentageFactory.build(
                sector=cl.Sector.teacher_training,
                percentage=60
            ),
            fac.SectorPercentageFactory.build(
                sector=cl.Sector.primary_education,
                percentage=40
            ),

        ]
    )

    transactions = [
        fac.TransactionFactory.build(
            type=cl.TransactionType.disbursement,
            date=datetime.datetime(2012, 6, 30),
            value_amount=10000,
        ),
        fac.TransactionFactory.build(
            type=cl.TransactionType.disbursement,
            date=datetime.datetime(2012, 9, 30),
            value_amount=90000,
        ),
        fac.TransactionFactory.build(
            type=cl.TransactionType.disbursement,
            date=datetime.datetime(2012, 1, 31),
            value_amount=30000,
        ),
    ]
    for trans in transactions:
        trans.activity = activity
    activity.transactions = transactions
    return activity


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


class TestTransactionByCountry(TestCase, CSVTstMixin):
    def serialize(self, data):
        return serialize.csv_transaction_by_country(data)

    def example(self):
        ret = []
        act = example()
        for transaction in act.transactions:
            for country in act.recipient_country_percentages:
                ret.append((transaction, country))
        return ret

    def test_rec_country_code_0(self):
        data = self.process(self.example())
        self.assertField({"recipient-country-code": "KE"}, data[0])

    def test_rec_country_code_1(self):
        data = self.process(self.example())
        self.assertField({"recipient-country-code": "UG"}, data[1])

    def test_trans_date_0(self):
        data = self.process(self.example())
        self.assertField({"transaction-date": "06/30/2012"}, data[1])

    def test_trans_date_2(self):
        data = self.process(self.example())
        self.assertField({"transaction-date": "09/30/2012"}, data[2])

    def test_identifier(self):
        data = self.process(self.example())
        self.assertField({"iati-identifier": "GB-1-123"}, data[2])


class TestTransactionBySector(TestCase, CSVTstMixin):
    def serialize(self, data):
        return serialize.csv_transaction_by_sector(data)

    def example(self):
        ret = []
        act = example()
        for transaction in act.transactions:
            for sector in act.sector_percentages:
                ret.append((transaction, sector))
        return ret

    def test_sector_code_0(self):
        data = self.process(self.example())
        self.assertField({"sector-code": "11130"}, data[0])

    def test_sector_code_1(self):
        data = self.process(self.example())
        self.assertField({"sector-code": "11220"}, data[1])

    def test_trans_date_0(self):
        data = self.process(self.example())
        self.assertField({"transaction-date": "06/30/2012"}, data[1])

    def test_trans_date_2(self):
        data = self.process(self.example())
        self.assertField({"transaction-date": "09/30/2012"}, data[2])

    def test_identifier(self):
        data = self.process(self.example())
        self.assertField({"iati-identifier": "GB-1-123"}, data[2])


