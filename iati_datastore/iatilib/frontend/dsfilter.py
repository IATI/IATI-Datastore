from iatilib import codelists, db
from iatilib.model import (
    Activity, Budget, Transaction, CountryPercentage, SectorPercentage,
    RegionPercentage, Participation, Organisation)


def _filter(query, args):
    if "recipient-country" in args:
        country = codelists.Country.from_string(args["recipient-country"])
        query = query.filter(
            Activity.recipient_country_percentages.any(
                CountryPercentage.country == country
            )
        )

    if "recipient-region" in args:
        region = codelists.Region.from_string(args["recipient-region"])
        query = query.filter(
            Activity.recipient_region_percentages.any(
                RegionPercentage.region == region
            )
        )

    if "reporting-org" in args:
        query = query.filter(
            Activity.reporting_org_ref == args["reporting-org"])

    if "reporting-org_type" in args:
        code = codelists.OrganisationType.from_string(args["reporting-org_type"])
        query = query.filter(
            Activity.reporting_org.has(
                Organisation.type == code
            )
        )

    if "sector" in args:
        code = codelists.Sector.from_string(args["sector"])
        query = query.filter(
            Activity.sector_percentages.any(
                SectorPercentage.sector == code
            )
        )

    if "participating-org" in args:
        query = query.filter(
            Activity.participating_orgs.any(
                Participation.organisation_ref == args["participating-org"]
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


def activities_by_sector(args):
    return _filter(
        db.session.query(Activity, SectorPercentage).join(SectorPercentage),
        args
    )


def transactions(args):
    return _filter(Transaction.query.join(Activity), args)


def transactions_by_country(args):
    return _filter(
        db.session.query(Transaction, CountryPercentage)
        .join(Activity)
        .join(CountryPercentage),
        args
    )


def transactions_by_sector(args):
    return _filter(
        db.session.query(Transaction, SectorPercentage)
        .join(Activity)
        .join(SectorPercentage),
        args
    )


def budgets(args):
    return _filter(Budget.query.join(Activity), args)


def budgets_by_country(args):
    return _filter(
        db.session.query(Budget, CountryPercentage)
        .join(Activity)
        .join(CountryPercentage),
        args
    )


def budgets_by_sector(args):
    return _filter(
        db.session.query(Budget, SectorPercentage)
        .join(Activity)
        .join(SectorPercentage),
        args
    )
