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
