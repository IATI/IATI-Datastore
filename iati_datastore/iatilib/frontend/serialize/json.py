import datetime
from decimal import Decimal

from flask import current_app
from flask import json as jsonlib

from iatilib.model import (
    Activity, Organisation, Transaction, Participation, SectorPercentage,
    CountryPercentage, Budget
)


class JSONEncoder(jsonlib.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        return super(JSONEncoder, self).default(o)


def code(attr):
    if attr:
        return {
            "value": attr.value,
            "description": attr.description
        }
    return None


def json_rep(obj):
    if isinstance(obj, Activity):
        return {
            "iati_identifier": obj.iati_identifier,
            "title": obj.title,
            "description": obj.description,
            "reporting_org": json_rep(obj.reporting_org),
            "start_planned": obj.start_planned,
            "end_planned": obj.end_planned,
            "start_actual": obj.start_actual,
            "end_actual": obj.end_actual,
            "activity_websites": list(obj.websites),
            "transactions": {
                "commitments": [json_rep(o) for o in obj.commitments],
                "disbursements": [json_rep(o) for o in obj.disbursements],
                "expenditures": [json_rep(o) for o in obj.expenditures],
                "incoming_funds": [json_rep(o) for o in obj.incoming_funds],
                "interest_repayment": [json_rep(o) for o in obj.interest_repayment],
                "loan_repayments": [json_rep(o) for o in obj.loan_repayments],
                "reembursements": [json_rep(o) for o in obj.reembursements],
            },
            "participating_orgs": [json_rep(o) for o in obj.participating_orgs],
            "recipient_countries": [json_rep(o) for o in obj.recipient_country_percentages],
            "sector_percentages": [json_rep(o) for o in obj.sector_percentages],
            "budgets": {},
        }
    if isinstance(obj, Organisation):
        return {
            "ref": obj.ref,
            "name": obj.name
        }
    if isinstance(obj, Transaction):
        return {
            "value": {
                "currency": obj.value.currency.value,
                "amount": str(obj.value.amount),
                "date": obj.value.date
            }
        }
    if isinstance(obj, Participation):
        return {
            "organisation": json_rep(obj.organisation),
            "role": {
                "code": obj.role.value,
                "description": obj.role.description,
            }
        }
    if isinstance(obj, CountryPercentage):
        return {
            "country": {
                "code": obj.country.value,
                "name": obj.country.description,
            },
            "percentage": obj.percentage,
        }
    if isinstance(obj, SectorPercentage):
        return {
            "sector": code(obj.sector),
            "vocabulary": code(obj.vocabulary),
            "percentage": obj.percentage,
        }
    if isinstance(obj, Budget):
        return {
            "type": {
                "code": obj.type.value,
                "name": obj.type.description,
            },
            "period_start": obj.period_start,
            "period_end": obj.period_end,
            "value": {
                "currency": obj.value_currency.value,
                "amount": str(obj.value_amount),
            }
        }
    return {}


def json(pagination):
    return jsonlib.dumps({
        "ok": True,
        "number-of-results": pagination.total,
        "results": [json_rep(a) for a in pagination.items]
    },
    indent=2 if current_app.debug else 0,
    cls=JSONEncoder)
