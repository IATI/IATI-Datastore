import datetime

import voluptuous as v
from voluptuous import Invalid, MultipleInvalid


def apidate(value):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise Invalid(u"Date must be in the form yyyy-mm-dd")

activity_api_args = v.Schema({
    "limit": v.All(v.Coerce(int), v.Range(max=250000)),
    "offset": v.All(v.Coerce(int), v.Range(min=0)),
    "date": apidate,
    "stream": v.All(v.Coerce(bool)),
    'recipient-country' : v.All(v.Coerce(str)),
    'recipient-country.code' : v.All(v.Coerce(str)),
    'recipient-country.text' : v.All(v.Coerce(str)),
    'recipient-region' : v.All(v.Coerce(str)),
    'recipient-region.code' : v.All(v.Coerce(str)),
    'recipient-region.text' : v.All(v.Coerce(str)),
    'reporting-org' : v.All(v.Coerce(str)),
    'reporting-org.code' : v.All(v.Coerce(str)),
    'reporting-org.type' : v.All(v.Coerce(str)),
    'reporting-org.text' : v.All(v.Coerce(str)),
    'sector' : v.All(v.Coerce(str)),
    'sector.code' : v.All(v.Coerce(str)),
    'sector.text' : v.All(v.Coerce(str)),
    'policy-marker' : v.All(v.Coerce(str)),
    'policy-marker.code' : v.All(v.Coerce(str)),
    'participating-org' : v.All(v.Coerce(str)),
    'participating-org.ref' : v.All(v.Coerce(str)),
    'participating-org.text' : v.All(v.Coerce(str)),
    'related-activity': v.All(v.Coerce(str)),
    'related-activity.ref': v.All(v.Coerce(str)),
    'transaction_ref' : v.All(v.Coerce(str)),
    'transaction' : v.All(v.Coerce(str)),
    'start-date__gt' : apidate,
    'start-date__lt' : apidate,
    'end-date__gt' : apidate,
    'end-date__lt' : apidate,
    'last-change__gt' : apidate,
    'last-change__lt' : apidate,
})
