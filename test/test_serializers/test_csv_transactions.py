from unittest import TestCase

from . import CSVTstMixin as _CSVTstMixin
from test import factories as fac
from test.factories import create_activity

from iatilib.frontend import serialize


class CSVTstMixin(_CSVTstMixin):
    def serialize(self, data):
        return serialize.transaction_csv(data)


class TestCSVTransactionExample(TestCase, CSVTstMixin):
    # See example here: https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdHJIWDJtaXhBV0IwOG56N0p1TE04V2c&usp=sharing#gid=5
    def test_transaction_type(self):
        data = self.process([
            fac.TransactionFactory.build(type__code="D")
        ])
        self.assertField({"transaction-type": "D"}, data[0])

    def test_default_currency(self):
        data = self.process([
            fac.TransactionFactory.build(
                type__code="D",
                activity__default_currency="USD")
        ])
        self.assertField({"default-currency": "USD"}, data[0])
