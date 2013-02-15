import unittest

from iatilib.frontend import create_app
from iatilib import db


def create_db():
    db.create_all()


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:')
        create_db()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class ClientTestCase(AppTestCase):
    def setUp(self):
        super(ClientTestCase, self).setUp()
        self.client = self.app.test_client()
