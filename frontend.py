import os
from flask import Flask, escape
import iatilib
import iatilib.frontend

DEBUG=bool(os.environ.get('FLASK_DEBUG',False))

if __name__=='__main__':
  port = int(os.environ.get('PORT',5000))
  iatilib.log('info', 'Running server. Port=%d FLASK_DEBUG=%s' % (port,str(DEBUG)))
  iatilib.frontend.app.run(host='0.0.0.0',port=port,debug=DEBUG)

