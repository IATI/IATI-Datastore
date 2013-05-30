from functools import partial
from sqlalchemy import or_
from iatilib import codelists, db
from iatilib.model import (
    Activity, Budget, Transaction, CountryPercentage, SectorPercentage,
    RegionPercentage, Participation, Organisation, PolicyMarker,
    RelatedActivity)

class BadFilterException(Exception):
    pass

def filter_from_codelist(codelist, column, related_column, code):
    value = codelist.from_string(code)
    return column.any(related_column == value)

def filter_from_text(query, column, related_column, text):
    return query.filter(column.any(related_column == text))

def _filter(query, args):
    recipient_country = partial(filter_from_codelist, codelists.Country,
        Activity.recipient_country_percentages, CountryPercentage.country)

    def recipient_country_text(country):
        return Activity.recipient_country_percentages.any(
            CountryPercentage.name == country
        )

    def recipient_region(region_string):
        region = codelists.Region.from_string(region_string)
        return Activity.recipient_region_percentages.any(
            RegionPercentage.region == region
        )

    def recipient_region_text(region):
        return Activity.recipient_region_percentages.any(
            RegionPercentage.name == region
        )

    def reporting_org(organisation):
        return Activity.reporting_org_ref == organisation

    def reporting_org_text(organisation):
        return Activity.reporting_org.has(
            Organisation.name == organisation
        )

    def reporting_org_type(organisation_type):
        code = codelists.OrganisationType.from_string(organisation_type)
        return Activity.reporting_org.has(
            Organisation.type == code
        )

    def participating_org(organisation):
        return Activity.participating_orgs.any(
            Participation.organisation_ref == organisation
        )
 
    def participating_org_text(organisation):
        return Activity.participating_orgs.any(
            Participation.organisation.has(
                Organisation.name == organisation
            )
        )

    def sector(sector_string):
        code = codelists.Sector.from_string(sector_string)
        return Activity.sector_percentages.any(
            SectorPercentage.sector == code
        )

    def sector_text(sector):
        return Activity.sector_percentages.any(
            SectorPercentage.text == sector 
        )

    def transaction_ref(transaction):
        return Activity.transactions.any(
            Transaction.ref == transaction
        )

    def transaction_provider_org(organisation):
        return Activity.transactions.any(
            Transaction.provider_org_ref == organisation
        )

    def transaction_provider_org_name(organisation):
        return Activity.transactions.any(
            Transaction.provider_org.has(
                Organisation.name == organisation
            )
        )

    def transaction_receiver_org(organisation):
        return Activity.transactions.any(
            Transaction.receiver_org_ref == organisation
        )

    def transaction_receiver_org_name(organisation):
        return Activity.transactions.any(
            Transaction.receiver_org.has(
                Organisation.name == organisation
            )
        )

    def policy_marker(code):
        policy = codelists.PolicyMarker.from_string(code)
        return Activity.policy_markers.any(
            PolicyMarker.code == policy
        )

    def related_activity(ref):
        return Activity.related_activities.any(
            RelatedActivity.ref == ref
        )


    filter_conditions = {
            'recipient-country' : recipient_country,
            'recipient-country.code' : recipient_country,
            'recipient-country.text' : recipient_country_text,
            'recipient-region' : recipient_region,
            'recipient-region.code' : recipient_region,
            'recipient-region.text' : recipient_region_text,
            'reporting-org' : reporting_org,
            'reporting-org.code' : reporting_org,
            'reporting-org.type' : reporting_org_type,
            'reporting-org.text' : reporting_org_text,
            'sector' : sector,
            'sector.code' : sector,
            'sector.text' : sector_text,
            'policy-marker' : policy_marker,
            'policy-marker.code' : policy_marker,
            'participating-org' : participating_org,
            'participating-org.ref' : participating_org,
            'participating-org.text' : participating_org_text,
            'related-activity': related_activity,
            'related-activity.ref' : related_activity,
            'transaction_ref' : transaction_ref,
            'transaction' : transaction_ref,
            'transaction_provider-org' : transaction_provider_org,
            'transaction_provider-org_ref' : transaction_provider_org,
            'transaction_provider-org_text' : transaction_provider_org_name,
            'transaction_receiver-org' : transaction_receiver_org,
            'transaction_receiver-org_ref' : transaction_receiver_org,
            'transaction_receiver-org_text' : transaction_receiver_org_name,
    }

    for filter, search_string in args.items():
        filter_condition = filter_conditions.get(filter, None)
        if filter_condition:
            terms = search_string.split('|')
            if len(terms) == 1:
                query = query.filter(filter_condition(search_string))
            else:
                conditions = tuple([ filter_condition(term) for term in terms ])
                query = query.filter(or_(*conditions))


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
