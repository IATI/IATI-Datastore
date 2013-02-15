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

    if format == ".xml":
        out = "<result><ok>True</ok><result-activity>"
        for activity in query:
            out += activity.raw_xml.raw_xml
        out += "</result-activity></result>"
        resp = make_response(out)
        resp.headers['Content-Type'] = "application/xml"
        return resp
    return jsonify(
        ok=True,
        results=[pure_obj(x) for x in query]
        )
