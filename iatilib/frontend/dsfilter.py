from iatilib import codelists
from iatilib.model import Activity, Transaction, CountryPercentage


def _filter(query, args):
    if "country_code" in args:
        country = codelists.Country.from_string(args["country_code"])
        query = query.filter(
            Activity.recipient_country_percentages.any(
                CountryPercentage.country == country
            )
        )

    if "reporting_org_ref" in args:
        query = query.filter(
            Activity.reporting_org_ref == args["reporting_org_ref"])

    return query


def activities(args):
    return _filter(Activity.query, args)


def transactions(args):
    return _filter(Transaction.query.join(Activity), args)
