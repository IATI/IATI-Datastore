from flask import request, Response, Blueprint, jsonify, abort
from flask.views import MethodView
from werkzeug.datastructures import MultiDict
from flask.ext.sqlalchemy import Pagination

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

    serializer, mimetype = forms[format]
    return Response(serializer(pagination.items), mimetype=mimetype)


class DataStoreView(MethodView):
    filter = None
    serializer = None

    def paginate(self, query, page, per_page):
        return Pagination(
            query,
            page,
            per_page,
            query.count(),
            query.limit(per_page).offset((page - 1) * per_page).all()
        )

    def get(self, format=".csv"):
        if not request.path.endswith("csv"):
            abort(404)

        try:
            valid_args = validators.activity_api_args(MultiDict(request.args))
        except validators.Invalid:
            abort(404)

        page = valid_args.get("page", 1)
        per_page = valid_args.get("per_page", 50)
        query = self.filter(valid_args)
        pagination = self.paginate(query, page, per_page)

        return Response(
            self.serializer(pagination.items),
            mimetype="text/csv")


class DataStoreCSVView(DataStoreView):
    pass


class ActivityByCountryView(DataStoreCSVView):
    filter = staticmethod(dsfilter.activities_by_country)
    serializer = staticmethod(serialize.csv_activity_by_country)


class ActivityBySectorView(DataStoreCSVView):
    filter = staticmethod(dsfilter.activities_by_sector)
    serializer = staticmethod(serialize.csv_activity_by_sector)


class TransactionsView(DataStoreCSVView):
    filter = staticmethod(dsfilter.transactions)
    serializer = staticmethod(serialize.transaction_csv)


class BudgetsView(DataStoreCSVView):
    filter = staticmethod(dsfilter.budgets)
    serializer = staticmethod(serialize.budget_csv)


api.add_url_rule(
    '/access/activities/by_country<format>',
    view_func=ActivityByCountryView.as_view('activities_by_country'))

api.add_url_rule(
    '/access/activities/by_sector<format>',
    view_func=ActivityBySectorView.as_view('activities_by_sector'))

api.add_url_rule(
    '/access/transactions<format>',
    view_func=TransactionsView.as_view('transactions_list'))

api.add_url_rule(
    '/access/budgets<format>',
    view_func=BudgetsView.as_view('budgets_list'))
