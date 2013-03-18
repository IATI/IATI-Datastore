from datetime import datetime
import json as jsonlib

from sqlalchemy.orm.collections import InstrumentedList

from iatilib import model

from .csv import (
    csv, csv_activity_by_country, csv_activity_by_sector,
    transaction_csv, budget_csv)


def pure_obj(obj):
    keys = [a for a in dir(obj) if not a.startswith("_") and a != "metadata"]
    # Handle child relations
    out = {}
    for key in keys:
        val = getattr(obj, key)
        if type(val) is InstrumentedList:
            out[key] = [pure_obj(x) for x in val]
        elif type(val) in (model.TransactionValue, model.TransactionType):
            out[key] = pure_obj(val)
        elif type(val) is datetime:
            out[key] = val.isoformat()
        elif key in (
            "query", "query_class", "parent", "disbursements", "expenditures",
            "incoming_funds", "interest_repayment", "loan_repayments",
            "reembursements", "activity"
            ):
            pass
        else:
            out[key] = val
    return out


def xml(items):
    out = u"<result><ok>True</ok><result-activity>"
    for activity in items:
        out += activity.raw_xml
    out += u"</result-activity></result>"
    return out


def json(items):
    return jsonlib.dumps({
        "ok": True,
        "results": []
        })
