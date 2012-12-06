import os
from datetime import datetime
import traceback
from . import basex

# Parse environment
db_config = {
    'DATABASE_URL':None,
    'DATABASE_PORT':None,
    'DATABASE_USER':None,
    'DATABASE_PASS':None,
    'DATABASE_NAME':None
}
for k in db_config.keys():
    db_config[k] = os.environ.get(k)
    if not db_config[k]: 
        raise ValueError('No %s defined in the environment. The following must all be defined: %s' % (k, ','.join(db_config.keys())))
db_config['DATABASE_PORT'] = int( db_config['DATABASE_PORT'] )

def open_db():
    return basex.BaseX(db_config['DATABASE_URL'], db_config['DATABASE_PORT'], db_config['DATABASE_USER'], db_config['DATABASE_PASS'], db_config['DATABASE_NAME'])

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

