from datetime import datetime
from functools import partial
from sqlalchemy import or_, and_
from sqlalchemy.sql.operators import eq, gt, lt
from iatilib import codelists, db
from iatilib.model import (
    Activity, Budget, Transaction, CountryPercentage, SectorPercentage,
    RegionPercentage, Participation, Organisation, PolicyMarker,
    RelatedActivity, Resource)

class BadFilterException(Exception):
    pass

def filter_from_codelist(codelist, column, related_column, code):
    value = codelist.from_string(code)
    return column.any(related_column == value)

def filter_from_text(query, column, related_column, text):
    return query.filter(column.any(related_column == text))

def filter_from(codelist, column, related_column, code):
    value = codelist.from_string(code)
    return column.any(related_column == value)

def _filter(query, args):
    #recipient_country = partial(filter_from_codelist, codelists.Country,
    #    Activity.recipient_country_percentages, CountryPercentage.country)
    def recipient_country(country_code):
        return Activity.recipient_country_percentages.any(
            CountryPercentage.country == country_code
        )

    def recipient_country_text(country):
        return Activity.recipient_country_percentages.any(
            CountryPercentage.name == country
        )

    def recipient_region(region_code):
        return Activity.recipient_region_percentages.any(
            RegionPercentage.region == region_code
        )

    def recipient_region_text(region):
        return Activity.recipient_region_percentages.any(
            RegionPercentage.name == region
        )

    def reporting_org(organisation):
        return Activity.reporting_org.has(
            Organisation.ref == organisation
        )

    def reporting_org_text(organisation):
        return Activity.reporting_org.has(
            Organisation.name == organisation
        )

    def reporting_org_type(organisation_type):
        return Activity.reporting_org.has(
            Organisation.type == organisation_type 
        )

    def participating_org(organisation):
        return Activity.participating_orgs.any(
            Participation.organisation.has(
                Organisation.ref == organisation
            )
        )
 
    def participating_org_text(organisation):
        return Activity.participating_orgs.any(
            Participation.organisation.has(
                Organisation.name == organisation
            )
        )

    def participating_org_role(role):
        return Activity.participating_orgs.any(
            Participation.role == role 
        )

    def sector(sector_code):
        return Activity.sector_percentages.any(
            SectorPercentage.sector == sector_code
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
            Transaction.provider_org.has(
                Organisation.ref == organisation
            )
        )

    def transaction_provider_org_name(organisation):
        return Activity.transactions.any(
            Transaction.provider_org.has(
                Organisation.name == organisation
            )
        )

    def transaction_receiver_org(organisation):
        return Activity.transactions.any(
            Transaction.receiver_org.has(
                Organisation.ref == organisation
            )
        )

    def transaction_receiver_org_name(organisation):
        return Activity.transactions.any(
            Transaction.receiver_org.has(
                Organisation.name == organisation
            )
        )

    def policy_marker(policy_marker):
        return Activity.policy_markers.any(
            PolicyMarker.code == policy_marker
        )

    def related_activity(ref):
        return Activity.related_activities.any(
            RelatedActivity.ref == ref
        )

    def date_condition(condition, actual_date, planned_date, date):
        return or_(
                condition(actual_date, date),
                and_(condition(planned_date, date), actual_date == None),
        )

    def registry_dataset(dataset_id):
        return Activity.resource.has(
            Resource.dataset_id == dataset_id
        )



    filter_conditions = {
            'iati-identifier': partial(eq, Activity.iati_identifier),
            'recipient-country' : recipient_country,
            'recipient-country.code' : recipient_country,
            'recipient-country.text' : recipient_country_text,
            'recipient-region' : recipient_region,
            'recipient-region.code' : recipient_region,
            'recipient-region.text' : recipient_region_text,
            'reporting-org' : reporting_org,
            'reporting-org.ref' : reporting_org,
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
            'participating-org.role' : participating_org_role,
            'related-activity': related_activity,
            'related-activity.ref' : related_activity,
            'transaction.ref' : transaction_ref,
            'transaction' : transaction_ref,
            'transaction_provider-org' : transaction_provider_org,
            'transaction_provider-org.ref' : transaction_provider_org,
            'transaction_provider-org.text' : transaction_provider_org_name,
            'transaction_receiver-org' : transaction_receiver_org,
            'transaction_receiver-org.ref' : transaction_receiver_org,
            'transaction_receiver-org.text' : transaction_receiver_org_name,
            'start-date__gt' : partial(date_condition, gt, Activity.start_actual, Activity.start_planned),
            'start-date__lt' : partial(date_condition, lt, Activity.start_actual, Activity.start_planned),
            'end-date__gt' : partial(date_condition, gt, Activity.end_actual, Activity.end_planned),
            'end-date__lt' : partial(date_condition, lt, Activity.end_actual, Activity.end_planned),
            'last-change__gt': partial(gt, Activity.last_change_datetime),
            'last-change__lt': partial(lt, Activity.last_change_datetime),
            'last-updated-datetime__gt': partial(gt, Activity.last_updated_datetime),
            'last-updated-datetime__lt': partial(lt, Activity.last_updated_datetime),
            'registry-dataset': registry_dataset,
    }

    for filter, search_string in args.items():
        filter_condition = filter_conditions.get(filter, None)
        if filter_condition:
            if isinstance(search_string, basestring):
                terms = search_string.split('|')
                if len(terms) >= 1:
                    conditions = tuple([ filter_condition(term) for term in terms ])
                    query = query.filter(or_(*conditions))
                else:
                    query = query.filter(filter_condition(search_string))

            elif isinstance(search_string, list):
                if len(search_string) == 1:
                    query = query.filter(filter_condition(search_string[0]))
                elif len(search_string) >= 1:
                    conditions = tuple([ filter_condition(term) for term in search_string])
                    query = query.filter(or_(*conditions))
            else:
                query = query.filter(filter_condition(search_string))

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
