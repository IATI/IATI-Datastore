import os
from flask import Flask
from iatilib import Session, model

app = Flask(__name__)
# TODO update this at some point
DEBUG = True

@app.route('/')
def hello():
    q = Session.query(model.LogEntry)
    def row(x):
        return '<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (x.id,x.timestamp.isoformat(),x.text)
    table = '<table border="2">%s</table>' % ''.join( [row(x) for x in q] )
    return '<html>API Status: Healthy<br/>%s</html>' % table

if __name__=='__main__':
  port = int(os.environ.get('PORT',5000))
  app.run(host='0.0.0.0',port=port,debug=DEBUG)

