import iatilib
import argparse
import sys
import os
import traceback
from datetime import date

def main(data_dump):
    assert os.path.exists(data_dump), 'Data dump folder "%s" does not exist.' % data_dump
    logfilename = 'log-%s.txt' % str(date.today())
    log = iatilib.LogFile( logfilename )
    log.write('Commencing import task. Directory=%s' % data_dump)
    try:
        importer = iatilib.Importer(log)
        importer.load_directory(data_dump)
        count_activity = iatilib.Session.query(iatilib.model.Activity).count()
        count_transaction = iatilib.Session.query(iatilib.model.Transaction).count()
        log.write('Completed import task. Database contains:')
        log.write('  %d activities' % count_activity)
        log.write('  %d transactions' % count_transaction)
    except Exception as e:
        traceback.print_exc()
        log.write('Import task failed. Exception')
        log.write(str(e))
    log.close()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Parse an IATI data dump folder and populate the database with activities.')
    parser.add_argument('data_dump', help='Data dump folder to parse.')
    #parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help='Verbose output')
    arg = parser.parse_args()
    main(arg.data_dump)
