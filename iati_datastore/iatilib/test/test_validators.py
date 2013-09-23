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
            validators.activity_api_args({"limit": 1000000})

    def test_per_page_string(self):
        self.assertEquals(
            validators.activity_api_args({"limit": "10"}),
            {"limit": 10}
            )

    def test_limit_zero(self):
        """
        [#96] offset of zero should be allowed!
        """
        self.assertEquals(
            validators.activity_api_args({"offset": "0"}),
            {"offset": 0}
            )

    def test_date(self):
        self.assertEquals(
            validators.activity_api_args({"date": "2007-05-25"}),
            {"date": datetime.date(2007, 5, 25)}
            )

    def test_stream(self):
        self.assertEquals(
            validators.activity_api_args({"stream": "t"}),
            {"stream": True}
        )

