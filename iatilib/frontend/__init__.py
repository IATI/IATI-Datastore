from flask import Flask,request,make_response,escape
import json
import iatilib

app = Flask('iatilib.frontend')

@app.route('/')
def homepage():
    return app.send_static_file('index.html')

from .api1 import api

app.register_blueprint(api)
