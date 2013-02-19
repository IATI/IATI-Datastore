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

from werkzeug.datastructures import MultiDict

from . import dsfilter
from . import validators

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
    valid_args = validators.activity_api_args(MultiDict(request.args))
    query = dsfilter.activities(valid_args)
    pagination = query.paginate(
        valid_args.get("page", 1),
        valid_args.get("per_page", 50),
        )

    if format == ".xml":
        out = "<result><ok>True</ok><result-activity>"
        for activity in pagination.items:
            out += activity.raw_xml.raw_xml
        out += "</result-activity></result>"
        resp = make_response(out)
        resp.headers['Content-Type'] = "application/xml"
        return resp
    return jsonify(
        ok=True,
        results=[pure_obj(x) for x in pagination.items]
        )
