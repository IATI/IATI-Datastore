from iatilib import codelists, db
from iatilib.model import (
    Activity, Budget, Transaction, CountryPercentage, Participation)


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

    if "participating_org_ref" in args:
        query = query.filter(
            Activity.participating_orgs.any(
                Participation.organisation_ref == args["participating_org_ref"]
            )
        )

    return query


def activities(args):
    return _filter(Activity.query, args)


def activities_by_country(args):
    return _filter(
        db.session.query(Activity, CountryPercentage).join(CountryPercentage),
        args
    )


def transactions(args):
    return _filter(Transaction.query.join(Activity), args)


def budgets(args):
    return _filter(Budget.query.join(Activity), args)
