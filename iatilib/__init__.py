import os
import sqlalchemy
import sqlalchemy.orm
from datetime import datetime
import traceback

database_url = os.environ.get('DATABASE_URL')
database_echo = os.environ.get('DATABASE_ECHO', '').lower()=='true'

if not database_url:
    raise ValueError('No DATABASE_URL defined in the environment. Try running:\n          $ export DATABASE_URL=postgresql://user:pass@localhost/mydatabase')

engine = sqlalchemy.create_engine(database_url,echo=database_echo)
Session = sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(engine))

import model

# Simple logfile class. Use a library if this gets any more than ~15 lines
class LogFile:
    def __init__(self,filename,log_to_screen=True):
        self.file = open(filename,'a')
        self.log_to_screen = log_to_screen
    def write(self,text):
        if self.log_to_screen:
            print text
        text = '%s %s' % (str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), text)
        print >>self.file, text
    def write_traceback(self):
        if self.log_to_screen:
            traceback.print_exc()
        traceback.print_exc(file=self.file)
    def close(self):
        self.file.close()

