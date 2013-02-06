from iatilib import log
from iatilib import session
from iatilib.model import *
from iatilib.frontend import app
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.sql.expression import and_, or_
from flask import request, make_response, escape
from datetime import datetime,timedelta
import json
import functools
import iso8601
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
        def wrapped_fn_csv(*args, **kwargs):
            try:
                raw = f(*args, **kwargs) 
                assert type(raw) is list, type(raw)
            except (AssertionError, ValueError) as e:
                if request.args.get('_debug') is not None:
                    raise e
                raw = [{ 'ok': False, 'message' : e.message }]
            csv_headers = []
            for x in raw: csv_headers += x.keys()
            csv_headers = list(set(csv_headers))
            response_text = ','.join(csv_headers) + '\n'
            for x in raw:
                response_text += ','.join( [str(x.get(key) or '') for key in csv_headers ] ) + '\n'
            response = make_response(response_text)
            response.headers['content-type'] = 'text/csv'
            return response
        @functools.wraps(f)
        def wrapped_fn_json(*args, **kwargs):
            callback = request.args.get('callback')
            try:
                response = f(*args, **kwargs) 
            except (AssertionError, ValueError) as e:
                if request.args.get('_debug') is not None:
                    raise e
                response = { 'ok': False, 'message' : e.message }
            response_text = json.dumps(response)
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
        app.add_url_rule(BASE+rule+'.csv', endpoint+'.csv', wrapped_fn_csv, **options)
        app.add_url_rule(BASE+rule, endpoint, wrapped_fn_json, **options)
        return f
    return decorator

def pure_obj(obj):
    keys = filter(lambda x:x[0]!='_', dir(obj))
    keys.remove('metadata')
    # Handle child relations
    out = {}
    for key in keys:
        val = getattr(obj,key)
        if type(val) is InstrumentedList:
            out[key] = [ pure_obj(x) for x in val ]
        elif type(val) is datetime:
            out[key] = val.isoformat()
        else:
            out[key] = val
    return out

###########################################
####   IATI argument parser 
###########################################

def _prepare(total=None, per_page=10):
    """Prepare a response object based off the incoming args (assume pagination)"""
    response = {}
    response['ok'] = True
    response['page'] = int(request.args.get('page',0))
    response['per_page'] = int(request.args.get('per_page',per_page))
    response['offset'] = response['per_page'] * response['page']
    assert response['page']>=0, 'Page number out of range.'
    assert response['per_page']>0, 'per_page out of range.'
    if total:
        response['total'] = total
        response['last_page'] = max(0,total-1) / response['per_page']
    return response

def parse_args():
    """Turn the querystring into an XPath expression we can use to select elements.
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
                or child=='recipient-country':
            return '/@code'
        if child=='participating-org'\
                or child=='reporting-org':
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
        # Left hand side of the query's equals sign
        lhs = clean_parent(xParent,xChild,xProperty)\
                + clean_child(xChild,xChild,xProperty)\
                + clean_property(xProperty,xChild,xProperty) 
        # Nested OR groups within AND groups...
        _or      = lambda x : x[0] if len(x)==1 else '(%s)' % ' or '.join(x)
        _and     = lambda x : x[0] if len(x)==1 else '(%s)' % ' and '.join(x)
        or_string  = lambda x:  _or( [    lhs+'=\''+y+'\'' for y in x.split('|') ] )
        and_string = lambda x: _and( [ or_string(y) for y in x.split('+') ] )
        # input:   ?field=aa||bb+cc   
        # output:  ((field/text()=aa or field/text()=bb) and (field.text()=cc))
        out.append(and_string(value))
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

#### URL: /about

@endpoint('/about')
def about():
    # General status info
    count_activity = session.query(Activity).count()
    count_transaction = session.query(Transaction).count()
    return {'ok':True,'status':'healthy','indexed_activities':count_activity,'indexed_transactions':count_transaction}

#### URL: /access/activities

@endpoint('/access/activities')
def activities_list():
    query = session.query(Activity)
    # Filter by country
    _country = request.args.get('country')
    if _country is not None:
        query = query.filter(func.lower(Activity.recipient_country__text).contains(_country.lower()))
    _country_code = request.args.get('country_code')
    if _country_code is not None:
        query = query.filter(func.lower(Activity.recipient_country__code)==(_country_code.lower()))
    # Filter by reporting-org
    _reporting_org = request.args.get('reporting_org')
    if _reporting_org is not None:
        query = query.filter(func.lower(Activity.reporting_org__text).contains(_reporting_org.lower()))
    _reporting_org_ref = request.args.get('reporting_org_ref')
    if _reporting_org_ref is not None:
        query = query.filter(func.lower(Activity.reporting_org__ref)==(_reporting_org_ref.lower()))
    # Filter by sector (using inner-join)
    _sector = request.args.get('sector')
    if _sector is not None:
        query = query.filter(Sector.parent_id==Activity.id)
        query = query.filter( func.lower(Sector.text).contains(_sector.lower()) )
    _sector_code = request.args.get('sector_code')
    if _sector_code is not None:
        query = query.filter(Sector.parent_id==Activity.id)
        query = query.filter( Sector.code==_sector_code )
    # Filter by participating-org (using inner-join)
    _participating_org = request.args.get('participating_org')
    if _participating_org is not None:
        query = query.filter(ParticipatingOrg.parent_id==Activity.id)
        query = query.filter( func.lower(ParticipatingOrg.text).contains(_participating_org.lower()) )
    _participating_org_ref = request.args.get('participating_org_ref')
    if _participating_org_ref is not None:
        query = query.filter(ParticipatingOrg.parent_id==Activity.id)
        query = query.filter( ParticipatingOrg.ref==_participating_org_ref )
    # Filter by dates (using inner-join)
    _date = request.args.get('date')
    Start = aliased(ActivityDate)
    End = aliased(ActivityDate)
    if _date is not None:
        try:
            _date = iso8601.parse_date(_date)
        except TypeError:
            _date = datetime.strptime(_date,"%Y-%m-%d")
        query = query\
                .join(Start,Activity.activitydate)\
                .join(End,Activity.activitydate)\
                .filter(and_(\
                    or_(End.type=='end-planned',End.type=='end-actual'),\
                    End.iso_date>_date)\
                    )\
                .filter(and_(\
                    or_(Start.type=='start-actual',Start.type=='start-planned'),\
                    Start.iso_date<_date)\
                    )
    """
    _XXX = request.args.get('XXX')
    if _XXX is not None:
        query = query.filter(XXX.parent_id==Activity.id)
        query = query.filter( XXX.code==_XXX )
        """
    # Prepare a response
    response = _prepare(query.count())
    query = query.offset(response['offset']).limit(response['per_page'])
    response['results'] = [ pure_obj(x) for x in query ]
    return response

"""
#### URL: /transaction and /transactions

@endpoint('/access/transactions')
def transaction_list():
    query = session.query(Transaction)
    query = query.limit(20)
    return [ json_obj(x) for x in query ]
"""


