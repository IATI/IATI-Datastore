import os
os.environ['DATABASE_URL'] = 'postgres:///iati-datastore'
from iatilib.wsgi import app as application
