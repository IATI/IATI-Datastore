from iatilib import codelists
from iatilib.model import Activity, CountryPercentage


def activities(args):
    query = Activity.query

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
