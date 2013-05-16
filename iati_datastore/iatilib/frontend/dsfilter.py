from iatilib import codelists, db
from iatilib.model import (
    Activity, Budget, Transaction, CountryPercentage, SectorPercentage,
    RegionPercentage, Participation, Organisation)

class BadFilterException(Exception):
    pass

def _filter(query, args):
    def recipient_country(country_arg):
        country = codelists.Country.from_string(country_arg)
        return query.filter(
            Activity.recipient_country_percentages.any(
                CountryPercentage.country == country
            )
        )

    def recipient_region(region_string):
        region = codelists.Region.from_string(region_string)
        return query.filter(
            Activity.recipient_region_percentages.any(
                RegionPercentage.region == region
            )
        )

    def reporting_org(organisation):
        return query.filter(Activity.reporting_org_ref == organisation)

    def reporting_org_type(organisation_type):
        code = codelists.OrganisationType.from_string(organisation_type)
        return query.filter(
            Activity.reporting_org.has(
                Organisation.type == code
            )
        )

    def sector(sector_string):
        code = codelists.Sector.from_string(sector_string)
        return query.filter(
            Activity.sector_percentages.any(
                SectorPercentage.sector == code
            )
        )

    def participating_org(organisation):
        return query.filter(
            Activity.participating_orgs.any(
                Participation.organisation_ref == organisation
            )
        )

    filter_functions = {
            'recipient-country' : recipient_country,
            #'recipient-country.code' : recipient_country,
            'recipient-region' : recipient_region,
            'reporting-org' : reporting_org,
            'reporting-org_type' : reporting_org_type,
            'sector' : sector,
            'participating-org' : participating_org,
    }

    for filter, search_string in args.items():
        filter_function = filter_functions.get(filter, None)
        if filter_function:
            query = filter_function(search_string)

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
