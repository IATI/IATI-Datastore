from flask import Flask,request,make_response,escape
import json
import iatilib

app = Flask('iatilib.frontend')
session = iatilib.open_db()

@app.route('/')
def homepage():
    return app.send_static_file('index.html')

# Patch the app with API v1 endpoints
import api1
