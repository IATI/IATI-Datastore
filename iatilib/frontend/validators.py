import datetime

import voluptuous as v
from voluptuous import Invalid, MultipleInvalid


def apidate(value):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise Invalid(u"Date must be in the form yyyy-mm-dd")


activity_api_args = v.Schema({
    "per_page": v.All(v.Coerce(int), v.Range(max=50)),
    "page": v.All(v.Coerce(int), v.Range(min=1)),
    "date": apidate,
    }, extra=True)
