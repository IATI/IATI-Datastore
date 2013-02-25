import datetime
from StringIO import StringIO
from unittest import TestCase
from functools import partial
import unicodecsv
from xml.etree import ElementTree as ET

from . import factories as fac
from .factories import create_activity
from iatilib.frontend import serialize


def load_csv(data):
    sio = StringIO(data)
    return list(unicodecsv.DictReader(sio, encoding="utf-8"))


for factory in (create_activity,):
    globals()[factory.__name__] = partial(factory, _commit=False)


class CSVTstMixin(TestCase):
    def process(self, data):
        return load_csv(serialize.csv(data))

    def assertField(self, mapping, row):
        assert len(mapping) == 1
        key, val = mapping.items()[0]
        self.assertIn(key, row)
        self.assertEquals(row[key], val)


class TestCSVSerializer(CSVTstMixin, TestCase):
    def test_empty(self):
        data = self.process([])
        self.assertEquals(0, len(data))

    def test_len_one(self):
        data = self.process([create_activity()])
        self.assertEquals(1, len(data))

    def test_len_many(self):
        data = self.process([create_activity(), create_activity()])
        self.assertEquals(2, len(data))

    def test_date_field(self):
        data = self.process([create_activity(
            start_planned=datetime.date(2012, 1, 1))])
        self.assertField({"start-planned": "2012-01-01"}, data[0])

    def test_quoting(self):
        data = self.process([create_activity(reporting_org__text=u"l,r")])
        self.assertField({"reporting-org": "l,r"}, data[0])

    def test_unicode(self):
        data = self.process([create_activity(reporting_org__text=u"\u2603")])
        self.assertField({"reporting-org": u"\u2603"}, data[0])

    def test_no_description(self):
        # Description is an optional thing
        act = create_activity()
        act.description = []
        data = self.process([act])
        self.assertField({"description": ""}, data[0])


class TestCSVExample(CSVTstMixin, TestCase):
    # these tests are based around an example from IATI
    # https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdHJIWDJtaXhBV0IwOG56N0p1TE04V2c#gid=4

    def test_iati_identifier(self):
        data = self.process([create_activity(iatiidentifier__text="GB-1-123")])
        self.assertField({"iati-identifier": "GB-1-123"}, data[0])

    def test_title(self):
        data = self.process([create_activity(title__text="Project 123")])
        self.assertField({"title": "Project 123"}, data[0])

    def test_description(self):
        data = self.process([create_activity(
            description__text="Description of Project 123")])
        self.assertField({"description": "Description of Project 123"}, data[0])

    def test_recepient_country_code(self):
        act = create_activity()
        act.recipientcountry = [
            fac.RecipientCountryFactory.build(code="KE", text="Kenya"),
            fac.RecipientCountryFactory.build(code="UG", text="Uganda"),
        ]
        data = self.process([act])
        self.assertField({
            "recipient-country-code": "KE;UG"}, data[0])

    def test_recepient_country(self):
        act = create_activity()
        act.recipientcountry = [
            fac.RecipientCountryFactory.build(code="KE", text="Kenya"),
            fac.RecipientCountryFactory.build(code="UG", text="Uganda"),
        ]
        data = self.process([act])
        self.assertField({
            "recipient-country": "Kenya;Uganda"}, data[0])

    def test_recepient_country_percentage(self):
        act = create_activity()
        act.recipientcountry = [
            fac.RecipientCountryFactory.build(percentage=80),
            fac.RecipientCountryFactory.build(percentage=20),
        ]
        data = self.process([act])
        self.assertField({"recipient-country-percentage": "80;20"}, data[0])

    def test_sector_code(self):
        act = create_activity()
        act.sector = [
            fac.SectorFactory.build(code="11130"),
            fac.SectorFactory.build(code="11220"),
        ]
        data = self.process([act])
        self.assertField({"sector-code": "11130;11220"}, data[0])

    def test_sector(self):
        act = create_activity()
        act.sector = [
            fac.SectorFactory.build(text="Teacher Training"),
            fac.SectorFactory.build(text="Primary Education"),
        ]
        data = self.process([act])
        self.assertField(
            {"sector": "Teacher Training;Primary Education"},
            data[0])

    def test_sector_percentage(self):
        act = create_activity()
        act.sector = [
            fac.SectorFactory.build(percentage=60),
            fac.SectorFactory.build(percentage=40)
        ]
        data = self.process([act])
        self.assertField({"sector-percentage": "60;40"}, data[0])

    def test_currency(self):
        act = create_activity()
        act.transaction = [
            fac.TransactionFactory.build(
                type__code="D",
                value__text=130000,
                value__currency="USD"
                ),
        ]
        data = self.process([act])
        self.assertField({"currency": "USD"}, data[0])

    def test_currency_mixed(self):
        act = create_activity()
        act.transaction = [
            fac.TransactionFactory.build(
                type__code="D",
                value__text=130000,
                value__currency="USD"
                ),
            fac.TransactionFactory.build(
                type__code="D",
                value__text=130000,
                value__currency="AUD"
                ),
        ]
        data = self.process([act])
        self.assertField({"currency": "!Mixed currency"}, data[0])

    def test_currency_missing(self):
        # If there is no default currency specified on the activity and
        # none on the transaction then we end up with a missing currency.
        act = create_activity()
        act.transaction = [
            fac.TransactionFactory.build(
                type__code="D",
                value__text=130000,
                value__currency=None
                ),
        ]
        data = self.process([act])
        self.assertField({"currency": ""}, data[0])

    def test_mixed_transation_types(self):
        act = create_activity()
        act.transaction = [
            fac.TransactionFactory.build(
                type__code="D",
                value__text=1,
                value__currency="USD"
                ),
            fac.TransactionFactory.build(
                type__code="E",
                value__text=2,
                value__currency="USD"
                ),
        ]
        data = self.process([act])
        self.assertField({"currency": "USD"}, data[0])
        self.assertField({"total-Disbursement": "1"}, data[0])
        self.assertField({"total-Expenditure": "2"}, data[0])


class TotalFieldMixin(object):
    # There are six total fields that behave identicaly
    def test_total(self):
        act = create_activity()
        act.transaction = [
            fac.TransactionFactory.build(
                type__code=self.transaction_code,
                value__text=130000
                ),
        ]
        data = self.process([act])
        self.assertField({self.csv_field: "130000"}, data[0])

    def test_many_trans(self):
        act = create_activity()
        act.transaction = [
            fac.TransactionFactory.build(
                type__code=self.transaction_code,
                value__text=2
                ),
            fac.TransactionFactory.build(
                type__code=self.transaction_code,
                value__text=1
                ),
        ]
        data = self.process([act])
        self.assertField({self.csv_field: "3"}, data[0])

    def test_many_currencies(self):
        act = create_activity()
        act.transaction = [
            fac.TransactionFactory.build(
                type__code=self.transaction_code,
                value__text=2,
                value__currency="USD",
                ),
            fac.TransactionFactory.build(
                type__code=self.transaction_code,
                value__text=1,
                value__currency="AUD"
                ),
        ]
        data = self.process([act])
        self.assertField({self.csv_field: "!Mixed currency"}, data[0])


class TestTotalDisbursement(CSVTstMixin, TotalFieldMixin, TestCase):
    transaction_code = "D"
    csv_field = "total-Disbursement"


class TestTotalExpenditure(CSVTstMixin, TotalFieldMixin, TestCase):
    transaction_code = "E"
    csv_field = "total-Expenditure"


class TestTotalIncomingFunds(CSVTstMixin, TotalFieldMixin, TestCase):
    transaction_code = "IF"
    csv_field = "total-Incoming Funds"


class TestTotalInterestRepayment(CSVTstMixin, TotalFieldMixin, TestCase):
    transaction_code = "IR"
    csv_field = "total-Interest Repayment"


class TestTotalLoanRepayment(CSVTstMixin, TotalFieldMixin, TestCase):
    transaction_code = "LR"
    csv_field = "total-Loan Repayment"


class TestTotalReimbursement(CSVTstMixin, TotalFieldMixin, TestCase):
    transaction_code = "R"
    csv_field = "total-Reimbursement"


class TestXMLSerializer(TestCase):
    def process(self, items):
        return ET.fromstring(serialize.xml(items).encode("utf-8"))

    def test_raw(self):
        # the xml that's output is the stuff in raw_xml
        data = self.process([
            create_activity(activity_parent__raw_xml=u"<test />")
            ])
        self.assert_(data.find(".//test") is not None)

    def test_unicode(self):
        data = self.process([
            create_activity(parent__raw_xml=u"<test>\u2603</test>")
            ])
        self.assertEquals(u"\u2603", data.find(".//test").text)

    def test_namespace(self):
        # raw xml that goes in with a ns prefix should come out with one
        # (even though it's meaningless without the ns declaration)
        # it's lousy to do this with string tests, but ET/Expat really
        # doesn't want to load xml with unbound prefixes
        items = [create_activity(parent__raw_xml=u"<t:test />")]
        ser_data = serialize.xml(items)
        self.assertIn("t:test", ser_data)
