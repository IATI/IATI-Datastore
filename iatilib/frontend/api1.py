from flask import request, make_response, Blueprint, jsonify, abort
from werkzeug.datastructures import MultiDict


from iatilib import db
from iatilib.model import Activity, Transaction

from . import dsfilter, validators, serialize


api = Blueprint('api', __name__)


@api.route('/about')
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


@api.route('/access/activities', defaults={"format": ".json"})
@api.route('/access/activities<format>')
def activities_list(format):
    forms = {
        ".xml": (serialize.xml, "application/xml"),
        ".json": (serialize.json, "application/json"),  # rfc4627
        ".csv": (serialize.csv, "text/csv")  # rfc4180
    }

    if format not in forms:
        abort(404)

    try:
        valid_args = validators.activity_api_args(MultiDict(request.args))
    except validators.Invalid:
        abort(404)

    query = dsfilter.activities(valid_args)
    pagination = query.paginate(
        valid_args.get("page", 1),
        valid_args.get("per_page", 50),
        )



    serializer, content_type = forms[format]
    resp = make_response(serializer(pagination.items))
    resp.headers['Content-Type'] = content_type
    return resp
