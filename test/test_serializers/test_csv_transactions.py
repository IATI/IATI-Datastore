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

    def test_default_currency(self):
        data = self.process([
            fac.TransactionFactory.build(
                type=cl.TransactionType.disbursement,
                activity__default_currency=cl.Currency.us_dollar)
        ])
        self.assertField({"default-currency": "USD"}, data[0])

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
