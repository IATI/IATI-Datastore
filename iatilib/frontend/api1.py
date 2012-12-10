from iatilib.frontend import app,session
from flask import request, make_response, escape
from datetime import datetime,timedelta
import json
import functools
from urllib import urlencode

##################################################
####           Utilities
##################################################

all_endpoints = []

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
            home_link = request.url_root+'api/1'
            json_link = request.url.replace( request.base_url, request.base_url+'.json' )
            xml_link = request.url.replace( request.base_url, request.base_url+'.xml' )
            if type(raw) is not str:
                raw = json.dumps(raw,indent=4)
            html_string = """
            <html>
            <ul><li>API Home: <a href="%s">%s</a></li>
                <li>Retrieve as XML: <a href="%s">%s</a></li>
                <li>Retrieve as JSON: <a href="%s">%s</a></li>
            </ul>
            <hr/>Response:
            <pre>%s</pre>
            </html>'
            """
            response = make_response(html_string % (home_link,home_link,xml_link,xml_link,json_link,json_link,escape(raw)))
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
        # Add this endpoint to the list
        all_endpoints.append(BASE+rule)
        # Bind to the root, JSON and CSV endpoints simultaneously
        app.add_url_rule(BASE+rule+'.json', endpoint+'.json', wrapped_fn_json, **options)
        app.add_url_rule(BASE+rule+'.xml', endpoint+'.xml', wrapped_fn_xml, **options)
        app.add_url_rule(BASE+rule, endpoint, wrapped_fn_raw, **options)
        return f
    return decorator


###########################################
####   IATI argument parser 
###########################################

def parse_args():
    """Turn the querystring into an XPath expression we can use to select elements from the databse.
    See the querystring section of the IATI document:
    https://docs.google.com/document/d/1gxvmYZSDXBTSMAU16bxfFd-hn1lYVY1c2olkXbuPBj4/edit
    Plenty of special cases apply!
    """
    def clean_parent(parent, child, property):
        if parent:
            return parent+'/'
        return ''
    def clean_child(parent, child, property):
        if child=='sector':
            return 'sector[@vocabulary=\'DAC\']'
        return child
    def clean_property(parent, child, property):
        if property=='text':
            return '/text()'
        if property:
            return '/@'+property
        if child=='sector' \
                or child=='reporting-org'\
                or child=='recipient-country':
            return '/@code'
        if child=='participating-org':
            return '/@ref'
        return '/text()'
    def split(key):
        # Split out the parent xPath element
        split_parent = key.split('_')
        assert len(split_parent)<=2, 'Bad parameter: %s' % key
        xParent = split_parent[0] if len(split_parent)==2 else None
        # Split out the child xPath element
        split_child = split_parent[-1].split('.')
        assert len(split_child)<=2, 'Bad parameter: %s' % key
        xChild = split_child[0]
        xProperty = split_child[1] if len(split_child)>1 else None
        return xParent, xChild, xProperty
    # Create an array of xpath strings...
    out = []
    for key,value in sorted(request.args.items(), key=lambda x:x[0]):
        xParent, xChild, xProperty = split(key)
        lhs = clean_parent(xParent,xChild,xProperty)\
                + clean_child(xChild,xChild,xProperty)\
                + clean_property(xProperty,xChild,xProperty)
        # Nested OR groups within AND groups...
        _or      = lambda x : x[0] if len(x)==1 else '(%s)' % ' or '.join(x)
        _and     = lambda x : x[0] if len(x)==1 else '(%s)' % ' and '.join(x)
        or_list  = lambda x: [(lhs+'='+y) for y in x.split('|')]
        and_list = lambda x: [ _or(or_list(y)) for y in x.split('+') ]
        # input:   ?field=aa||bb+cc   
        # output:  ((field/text()=aa or field/text()=bb) and (field.text()=cc))
        out.append(_and(and_list(value)))
    return ' and '.join(out)



##################################################
####           URL: /
##################################################
@endpoint('/')
def index():
    # Root of the API lists all available endpoints
    rules = [x.rule for x in app.url_map.iter_rules()]
    #all_endpoints = [request.url_root[:-1]+x for x in rules if x.startswith('/api/1')]
    return {'version':'1.0','ok':True,'endpoints':all_endpoints}

#### URL: /health

@endpoint('/health')
def health():
    # Ping the DB server for something
    count_activity = session.query('count(//iati-activity)')
    count_transaction = session.query('count(//transaction)')
    return 'DB contains %s activities; %s transactions.' % (count_activity,count_transaction)

#### URL: /activity and /activities

@endpoint('/activities')
def activities_list():
    query = '//iati-activity'
    result = session.query(query)
    return result

@endpoint('/activity/<id>')
def activity(id):
    query = '//iati-activity[iati-identifier[text()=\'%s\']]' % id
    result = session.query(query)
    #return '%s<br/>%s' % (query,result)
    return result


@endpoint('/debug/args')
def debug_args():
    return {'raw':request.args, 'processed':parse_args()}


