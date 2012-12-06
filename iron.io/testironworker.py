from time import sleep
from datetime import datetime
import sys
import argparse
import json
import requests

def main(payload):
    # connect to the database
    from iatilib import Session, model
    assert 'url' in payload, 'No URL specified'
    url = payload['url']
    r = requests.get(url)
    hashval = hash(r.text)
    logtext = 'url %s :: hash %d' % (url,hashval)
    x = model.LogEntry(timestamp=datetime.now(), text=logtext)
    Session.add(x)
    Session.commit()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Demo IronWorker thread')
    parser.add_argument('-e', dest='environment', help='Environment [eg. production]')
    parser.add_argument('-d', dest='tempdir', help='Temp storage directory')
    parser.add_argument('-id', dest='id', help='Thread ID')
    parser.add_argument('-payload', dest='payloadfile', help='Payload filename')
    arg = parser.parse_args()
    print 'Starting thread [id=%s]' % arg.id
    payload = json.load(open(arg.payloadfile,'r'))
    main(payload)

