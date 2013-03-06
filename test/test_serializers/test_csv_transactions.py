from unittest import TestCase

from . import CSVTstMixin


class Test1(TestCase, CSVTstMixin):
    def test_1(self):
        self.fail()
