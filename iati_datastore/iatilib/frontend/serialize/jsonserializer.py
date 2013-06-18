import datetime
from decimal import Decimal

from flask import current_app
from flask import json as jsonlib

from iatilib.model import (
    Activity, Organisation, Transaction, Participation, SectorPercentage,
    CountryPercentage, Budget
)
from iatilib import codelists


class JSONEncoder(jsonlib.JSONEncoder):
    TWOPLACES = Decimal(10) ** -2

    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        if isinstance(o, codelists.enum.EnumSymbol):
            return o.value
        if isinstance(o, Decimal):
            return str(o.quantize(self.TWOPLACES))
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
            "iati-identifier": obj.iati_identifier,
            "title": obj.title,
            "description": obj.description,
            "reporting-org": json_rep(obj.reporting_org),
            "start-planned": obj.start_planned,
            "end-planned": obj.end_planned,
            "start-actual": obj.start_actual,
            "end-actual": obj.end_actual,
            "activity-websites": list(obj.websites),
            "transaction": [json_rep(o) for o in obj.transactions],
            "participating-orgs": [json_rep(o) for o in obj.participating_orgs],
            "recipient-countries": [json_rep(o) for o in obj.recipient_country_percentages],
            "sector-percentages": [json_rep(o) for o in obj.sector_percentages],
            "budgets": {},
        }
    if isinstance(obj, Organisation):
        return {
            "ref" : obj.ref,
            "name" : obj.name,
        }
    if isinstance(obj, Transaction):
        return {
            "value": {
                "value-date": obj.value.date,
                "text": obj.value.amount,
                "currency": obj.value.currency.value,
            },
            "transaction-type": { "code": obj.type.value },
            "transaction-date": { "iso-date": obj.date },
            "flow-type": { "code": obj.flow_type },
            "finance-type": { "code": obj.finance_type },
            "aid-type": { "code": obj.aid_type },
            "disbursement-channel": { "code": obj.disbursement_channel},
            "tied-status": { "code": obj.tied_status}
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
            "period-start": obj.period_start,
            "period-end": obj.period_end,
            "value": {
                "currency": obj.value_currency.value,
                "amount": str(obj.value_amount),
            }
        }
    return {}


def json(pagination):
    return jsonlib.dumps({
        "ok": True,
        "total-count": pagination.total,
        "iati-activities": [json_rep(a) for a in pagination.items]
    },
    indent=2 if current_app.debug else 0,
    cls=JSONEncoder)
