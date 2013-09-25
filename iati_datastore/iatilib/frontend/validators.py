import datetime
from functools import partial

import voluptuous as v
from voluptuous import Invalid, MultipleInvalid

from iatilib import codelists


def apidate(value):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise Invalid(u"Date must be in the form yyyy-mm-dd")

def codelist_validator(Codelist, value):
    try:
        return Codelist.from_string(value)
    except ValueError:
        raise Invalid(u"{0} is not on code list".format(value))

organisation_role = partial(codelist_validator, codelists.OrganisationRole)
recipient_country = partial(codelist_validator, codelists.Country)
recipient_region = partial(codelist_validator, codelists.Region)
reporting_org_type = partial(codelist_validator, codelists.OrganisationType) 
sector = partial(codelist_validator, codelists.Sector)
policy_marker = partial(codelist_validator, codelists.PolicyMarker)

activity_api_args = v.Schema({
    "limit": v.All(v.Coerce(int), v.Range(max=250000)),
    "offset": v.All(v.Coerce(int), v.Range(min=0)),
    "date": apidate,
    "stream": v.All(v.Coerce(bool)),
    'recipient-country' : v.All(v.Coerce(str), recipient_country),
    'recipient-country.code' : v.All(v.Coerce(str), recipient_country),
    'recipient-country.text' : v.All(v.Coerce(str)),
    'recipient-region' : v.All(v.Coerce(str)),
    'recipient-region.code' : v.All(v.Coerce(str), recipient_region),
    'recipient-region.text' : v.All(v.Coerce(str), recipient_region),
    'reporting-org' : v.All(v.Coerce(str)),
    'reporting-org.code' : v.All(v.Coerce(str)),
    'reporting-org.type' : v.All(v.Coerce(str), reporting_org_type),
    'reporting-org.text' : v.All(v.Coerce(str)),
    'sector' : v.All(v.Coerce(str), sector),
    'sector.code' : v.All(v.Coerce(str), sector),
    'sector.text' : v.All(v.Coerce(str)),
    'policy-marker' : v.All(v.Coerce(str)),
    'policy-marker.code' : v.All(v.Coerce(str), policy_marker),
    'participating-org' : v.All(v.Coerce(str)),
    'participating-org.ref' : v.All(v.Coerce(str)),
    'participating-org.text' : v.All(v.Coerce(str)),
    'participating-org.role' : organisation_role,
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
