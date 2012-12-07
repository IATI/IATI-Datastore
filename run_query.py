import sys
import iatilib

session = iatilib.open_db()

if __name__=='__main__':
    query = sys.argv[1]
    print session.query(query)


