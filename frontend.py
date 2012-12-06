import os
from flask import Flask, escape
import iatilib

app = Flask(__name__)

session = iatilib.open_db()

# TODO update this at some point
DEBUG = True

@app.route('/')
def hello():
    # Ping the DB server for something
    query = '//iati-activity'
    result = session.query(query)
    out = '<p>API Status: healthy</p>'
    out += '<hr/>'
    out += '<p>query=<code>%s</code></p>' % query
    out += '<hr/>'
    out += '<pre>%s</pre>' % escape(result)
    return '<html>%s</html>' % out

if __name__=='__main__':
  port = int(os.environ.get('PORT',5000))
  app.run(host='0.0.0.0',port=port,debug=DEBUG)

