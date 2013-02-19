from datetime import datetime
from collections import OrderedDict
import json as jsonlib
import unicodecsv
from StringIO import StringIO

from sqlalchemy.orm.collections import InstrumentedList


def date(date_type):
    def accessor(activity):
        dates = [d.iso_date.strftime("%Y-%m-%d")
                 for d in activity.date
                 if d.type == date_type]
        if dates:
            return dates[0]
        return ""
    return accessor


def first_text(attr):
    def accessor(activity):
        return getattr(activity, attr)[0].text or ""
    return accessor


def csv(query):
    fields = OrderedDict((
        (u"iati-identifier", first_text(u"iatiidentifier")),
        (u"reporting-org", first_text(u"reportingorg")),
        (u"title", first_text(u"title")),
        (u"start-planned", date(u"start-planned")),
        ))

    out = StringIO()
    writer = unicodecsv.writer(out, encoding='utf-8')
    writer.writerow(fields.keys())
    for activity in query:
        row = [accessor(activity) for accessor in fields.values()]
        writer.writerow(row)
    return out.getvalue()


def xml(items):
    out = "<result><ok>True</ok><result-activity>"
    for activity in items:
        out += activity.raw_xml.raw_xml
    out += "</result-activity></result>"
    return out


def pure_obj(obj):
    keys = filter(lambda x: x[0] != '_', dir(obj))
    keys.remove('metadata')
    # Handle child relations
    out = {}
    for key in keys:
        val = getattr(obj, key)
        if type(val) is InstrumentedList:
            out[key] = [pure_obj(x) for x in val]
        elif type(val) is datetime:
            out[key] = val.isoformat()
        elif key in ("query", "query_class", "raw_xml"):
            pass
        else:
            out[key] = val
    return out


def json(items):
    return jsonlib.dumps({
        "ok": True,
        "results": [pure_obj(x) for x in items]
        })
