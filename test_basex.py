import time
from lxml import etree
from iatilib import BaseX

def main():
    conn = BaseX('107.22.195.156', 8984, 'admin', 'admin', 'local')
    print conn.query('//iati-activity')
    conn.close()

if __name__=='__main__':
    main()

