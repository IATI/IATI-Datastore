from datetime import datetime
import sqlalchemy as sa
from flask import request, Response, Blueprint, jsonify, abort, render_template
from flask.views import MethodView
from werkzeug.datastructures import MultiDict
from flask.ext.sqlalchemy import Pagination

from iatilib import db
from iatilib.model import Activity, Resource, Transaction, Dataset, Log

from . import dsfilter, validators, serialize


api = Blueprint('api', __name__)

def dictify(resource):
    fields = []
    for key in resource._fields:
        if isinstance(resource.__dict__[key], datetime):
            fields.append((key, resource.__dict__[key].isoformat()))
        else:
            fields.append((key, resource.__dict__[key]))
    return dict(fields)

@api.route('/about')
def about():
    # General status info
    count_activity = db.session.query(Activity).count()
    count_transaction = db.session.query(Transaction).count()
    return jsonify(
        ok=True,
        status='healthy',
        indexed_activities=count_activity,
        indexed_transactions=count_transaction,
    )

@api.route('/about/dataset')
def datasets():
    datasets = db.session.query(Dataset.name)
    return jsonify(datasets=[ i.name for i in datasets.all()] )


@api.route('/about/dataset/<dataset>')
def about_dataset(dataset):
    dataset = db.session.query(Dataset).get(dataset)
    resources = []
    for r in dataset.resources:
        resources.append({
            'url': r.url,
            'last_fetch': r.last_fetch.isoformat() if r.last_fetch else None,
            'last_status_code': r.last_status_code,
            'last_successful_fetch': r.last_succ.isoformat() if r.last_succ else None,
            'last_parsed': r.last_parsed.isoformat() if r.last_parsed else None,
            'num_of_activities': len(r.activities),
        }) 
        
    return jsonify(
            dataset=dataset.name,
            last_modified=dataset.last_modified.isoformat(),
            num_resources=len(dataset.resources),
            resources=resources,
    )


@api.route('/error/dataset')
def error():
    #logs = db.session.query(Log.dataset).distinct()
    logs = db.session.query(Log.dataset, Log.logger).\
            group_by(Log.dataset, Log.logger).\
            order_by(Log.dataset)
    return jsonify(
            errored_datasets=[ {'dataset': i[0], 'logger': i[1]} for i in logs.all() ]
    )

@api.route('/error/resource')
def resource_error():
    resource_url = request.args.get('url')
    if not resource_url:
        abort(404)
    error_logs = db.session.query(Log).filter(Log.resource == resource_url)
    errors = []
    for log in error_logs.all():
        error = {}
        error['resource_url'] = log.resource
        error['dataset'] = log.dataset
        error['logger'] = log.logger
        error['msg'] = log.msg
        error['traceback'] = log.trace
        error['datestamp'] = log.created_at.isoformat()
        errors.append(error)

    return jsonify(errors=errors)

@api.route('/error/dataset/<dataset_id>')
def dataset_error(dataset_id):
    error_logs = db.session.query(Log).filter(Log.dataset == dataset_id)
    errors = []
    for log in error_logs.all():
        error = {}
        error['resource_url'] = log.resource
        error['logger'] = log.logger
        error['msg'] = log.msg
        error['traceback'] = log.trace
        error['datestamp'] = log.created_at.isoformat()
        errors.append(error)

    return jsonify(errors=errors)

@api.route('/error/dataset.log')
def dataset_log():
    logs = db.session.query(Log.dataset).distinct()
    return render_template('datasets.log', logs=logs)
    
@api.route('/error/dataset.log/<dataset_id>')
def dataset_log_error(dataset_id):
    error_logs = db.session.query(Log).order_by(sa.desc(Log.created_at)).\
                        filter(Log.dataset == dataset_id)
    errors = []
    for log in error_logs.all():
        error = {}
        error['resource_url'] = log.resource
        error['logger'] = log.logger
        error['msg'] = log.msg
        error['traceback'] = log.trace.split('\n')
        error['datestamp'] = log.created_at.isoformat()
        errors.append(error)

    return render_template('dataset.log', errors=errors)


class DataStoreView(MethodView):
    filter = None
    serializer = None

    @property
    def streaming(self):
        return self.validate_args().get("stream", False)

    def paginate(self, query, page, per_page):
        if page < 1:
            abort(404)
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        if not items and page != 1:
            abort(404)
        return Pagination(query, page, per_page, query.count(), items)

    def validate_args(self):
        if not hasattr(self, "_valid_args"):
            try:
                self._valid_args = validators.activity_api_args(MultiDict(request.args))
            except validators.Invalid:
                abort(400)
        return self._valid_args

    def get_response(self, serializer=None, mimetype="text/csv"):
        if serializer is None:
            serializer = self.serializer

        valid_args = self.validate_args()
        query = self.filter(valid_args)

        if self.streaming:
            query = query.yield_per(100)
            body = serializer(query)
        else:
            pagination = self.paginate(
                query,
                valid_args.get("page", 1),
                valid_args.get("per_page", 50),
            )
            body = u"".join(serializer(pagination.items))
        return Response(body, mimetype=mimetype)


class ActivityView(DataStoreView):
    filter = staticmethod(dsfilter.activities)

    def get(self, format):
        forms = {
            ".xml": (serialize.xml, "application/xml"),
            ".json": (serialize.json, "application/json"),  # rfc4627
            ".csv": (serialize.csv, "text/csv")  # rfc4180
        }
        if format not in forms:
            abort(404)
        return self.get_response(*forms[format])


class DataStoreCSVView(DataStoreView):
    def get(self, format=".csv"):
        if not request.path.endswith("csv"):
            abort(404)
        return self.get_response()


class ActivityByCountryView(DataStoreCSVView):
    filter = staticmethod(dsfilter.activities_by_country)
    serializer = staticmethod(serialize.csv_activity_by_country)


class ActivityBySectorView(DataStoreCSVView):
    filter = staticmethod(dsfilter.activities_by_sector)
    serializer = staticmethod(serialize.csv_activity_by_sector)


class TransactionsView(DataStoreCSVView):
    filter = staticmethod(dsfilter.transactions)
    serializer = staticmethod(serialize.transaction_csv)


class TransactionsByCountryView(DataStoreCSVView):
    filter = staticmethod(dsfilter.transactions_by_country)
    serializer = staticmethod(serialize.csv_transaction_by_country)


class TransactionsBySectorView(DataStoreCSVView):
    filter = staticmethod(dsfilter.transactions_by_sector)
    serializer = staticmethod(serialize.csv_transaction_by_sector)


class BudgetsView(DataStoreCSVView):
    filter = staticmethod(dsfilter.budgets)
    serializer = staticmethod(serialize.budget_csv)


class BudgetsByCountryView(DataStoreCSVView):
    filter = staticmethod(dsfilter.budgets_by_country)
    serializer = staticmethod(serialize.csv_budget_by_country)


class BudgetsBySectorView(DataStoreCSVView):
    filter = staticmethod(dsfilter.budgets_by_sector)
    serializer = staticmethod(serialize.csv_budget_by_sector)


api.add_url_rule(
    '/access/activity',
    defaults={"format": ".json"},
    view_func=ActivityView.as_view('activity')
)

api.add_url_rule(
    '/access/activity<format>',
    view_func=ActivityView.as_view('activity')
)

api.add_url_rule(
    '/access/activity/by_country<format>',
    view_func=ActivityByCountryView.as_view('activity_by_country'))

api.add_url_rule(
    '/access/activity/by_sector<format>',
    view_func=ActivityBySectorView.as_view('activity_by_sector'))

api.add_url_rule(
    '/access/transaction<format>',
    view_func=TransactionsView.as_view('transaction_list'))

api.add_url_rule(
    '/access/transaction/by_country<format>',
    view_func=TransactionsByCountryView.as_view('transaction_by_country'))

api.add_url_rule(
    '/access/transaction/by_sector<format>',
    view_func=TransactionsBySectorView.as_view('transaction_by_sector'))

api.add_url_rule(
    '/access/budget<format>',
    view_func=BudgetsView.as_view('budget_list'))

api.add_url_rule(
    '/access/budget/by_country<format>',
    view_func=BudgetsByCountryView.as_view('budget_by_country'))

api.add_url_rule(
    '/access/budget/by_sector<format>',
    view_func=BudgetsBySectorView.as_view('budget_by_sector'))
