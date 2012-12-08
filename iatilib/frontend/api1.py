from iatilib.frontend import app,session
from flask import request, make_response, escape
from datetime import datetime,timedelta
import json
import functools
from urllib import urlencode

##################################################
####           Utilities
##################################################

def endpoint(rule, **options):
    """Function decorator borrowed & modified from Flask core."""
    BASE='/api/1'
    def decorator(f):
        @functools.wraps(f)
        def wrapped_fn_raw(*args, **kwargs):
            callback = request.args.get('callback')
            try:
                raw = f(*args, **kwargs)
            except (AssertionError, ValueError) as e:
                if request.args.get('_debug') is not None:
                    raise e
                raw = { 'ok': False, 'message' : e.message }
            json_link = request.url.replace( request.base_url, request.base_url+'.json' )
            xml_link = request.url.replace( request.base_url, request.base_url+'.xml' )
            if type(raw) is not str:
                raw = json.dumps(raw,indent=4)
            response = make_response('<html>Retrieve as XML: <a href="%s">%s</a><br/>Retrieve as JSON: <a href="%s">%s</a><hr/>Response:<pre>%s</pre></html>' % (xml_link,xml_link,json_link,json_link,escape(raw)))
            response.headers['content-type'] = 'text/html'
            return response
        @functools.wraps(f)
        def wrapped_fn_xml(*args, **kwargs):
            callback = request.args.get('callback')
            try:
                raw = f(*args, **kwargs)
            except (AssertionError, ValueError) as e:
                if request.args.get('_debug') is not None:
                    raise e
                raw = { 'ok': False, 'message' : e.message }
            response = make_response(raw)
            response.headers['content-type'] = 'text/xml'
            return response
        @functools.wraps(f)
        def wrapped_fn_json(*args, **kwargs):
            callback = request.args.get('callback')
            try:
                raw = {
                        'ok': True, 
                        'raw_xml' : f(*args, **kwargs) 
                      }
            except (AssertionError, ValueError) as e:
                if request.args.get('_debug') is not None:
                    raise e
                raw = { 'ok': False, 'message' : e.message }
            response_text = json.dumps(raw)
            if callback:
                response_text = '%s(%s);' % (callback,response_text)
            response = make_response(response_text)
            response.headers['content-type'] = 'application/json'
            return response
        endpoint = options.pop('endpoint', BASE+rule)
        # Bind to the root, JSON and CSV endpoints simultaneously
        app.add_url_rule(BASE+rule+'.json', endpoint+'.json', wrapped_fn_json, **options)
        app.add_url_rule(BASE+rule+'.xml', endpoint+'.xml', wrapped_fn_xml, **options)
        app.add_url_rule(BASE+rule, endpoint, wrapped_fn_raw, **options)
        return f
    return decorator

##################################################
####           URL: /
##################################################
@endpoint('/')
def index():
    rules = [x.rule for x in app.url_map.iter_rules()]
    endpoints = [request.url_root[:-1]+x for x in rules if x.startswith('/api/1')]
    return {'version':'1.0','ok':True,'endpoints':endpoints}

#### URL: /health

@endpoint('/health')
def health():
    # Ping the DB server for something
    query = '//iati-activity'
    result = session.query(query)
    return result

