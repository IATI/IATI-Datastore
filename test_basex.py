import BaseXClient
import time
from lxml import etree

class BaseXConnection:
    def __init__(self,host,port,user,pw,db_name):
        # create session
        self.session = BaseXClient.Session(host,port,user,pw)
        self.session.init()
        self.session.execute(db_name)
    def query(self,xquery):
        xquery = 'xquery '+xquery
        result = self.session.execute(xquery)
        return result
    def close():
        session.close()


def main():
    conn = BaseXConnection('107.22.195.156', 8984, 'admin', 'admin')
    print conn.query('//iati-activity')
    conn.close()

if __name__=='__main__':
    main()

