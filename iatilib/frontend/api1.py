from iatilib import log
from iatilib import db
from iatilib.model import *
from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.sql.expression import and_, or_
from flask import request, make_response, escape, Blueprint, jsonify
from datetime import datetime,timedelta
import json
import functools
import iso8601
from urllib import urlencode

api = Blueprint('api', __name__)

##################################################
####           Utilities
##################################################

all_endpoints = []

def endpoint(rule, **options):
    """Function decorator borrowed & modified from Flask core."""
    BASE='/api/1'
    def decorator(f):
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
        api.add_url_rule(BASE + rule, endpoint, wrapped_fn_json, **options)
        api.add_url_rule(BASE + rule + "<path:format>", endpoint, wrapped_fn_json, **options)
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
        elif key in ("query", "query_class", "raw_xml"):
            pass
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


@api.route('/api/1/about')
def about():
    # General status info
    count_activity = db.session.query(Activity).count()
    count_transaction = db.session.query(Transaction).count()
    return jsonify(
        ok=True,
        status='healthy',
        indexed_activities=count_activity,
        indexed_transactions=count_transaction
        )



@api.route('/api/1/access/activities', defaults={"format": ".json"})
@api.route('/api/1/access/activities<format>')
def activities_list(format):
    query = db.session.query(Activity)
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
    # Prepare a response
    response = _prepare(query.count())
    query = query.offset(response['offset']).limit(response['per_page'])
    response['results'] = [ pure_obj(x) for x in query ]

    if format == ".xml":
        out = "<x><ok>True</ok><result-activity>"
        for activity in query:
            out += activity.raw_xml.raw_xml
        out += "</result-activity></x>"
        return out
    return jsonify(
        ok=True,
        results = [ pure_obj(x) for x in query ]
        )


def xml_response(query):
    return "<x />"