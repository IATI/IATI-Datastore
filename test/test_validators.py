import datetime
from unittest import TestCase

from iatilib.frontend import validators


class TestApiDate(TestCase):
    def test_valid_date(self):
        self.assertEquals(
            validators.apidate("2007-01-25"),
            datetime.date(2007, 1, 25)
            )

    def test_invalid_date(self):
        with self.assertRaises(validators.Invalid):
            validators.apidate("1-1-2012")


class TestApiSchema(TestCase):
    def test_max_per_page(self):
        with self.assertRaises(validators.MultipleInvalid):
            validators.activity_api_args({"per_page": 1000})

    def test_date(self):
        self.assertEquals(
            validators.activity_api_args({"date": "2007-05-25"}),
            {"date": datetime.date(2007, 5, 25)}
            )
