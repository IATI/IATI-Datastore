from sqlalchemy import func

from iatilib.model import Activity, ActivityDate, RecipientCountry, ReportingOrg
from iatilib import db


def activities(args):
    query = Activity.query

    filter_fields = {
        u"country": (Activity.recipientcountry, RecipientCountry.text),
        u"country_code": (Activity.recipientcountry, RecipientCountry.code),
        u"reporting_org_ref": (Activity.reportingorg, ReportingOrg.ref),
    }

    for arg_field, (table, table_field) in filter_fields.items():
        if arg_field in args:
            query = query.filter(
                table.any(
                    func.lower(table_field) == args[arg_field].lower())
                )

    # there are 4 dates: start-actual, end-actual, start-planned, end-planned
    if "date" in args:
        start_sq = db.session.query(
            ActivityDate.parent_id,
            func.min(ActivityDate.iso_date)
            )\
            .filter(ActivityDate.iso_date >= args["date"])\
            .group_by(ActivityDate.parent_id).subquery()
        end_sq = db.session.query(
            ActivityDate.parent_id,
            func.max(ActivityDate.iso_date)
            )\
            .filter(ActivityDate.iso_date <= args["date"])\
            .group_by(ActivityDate.parent_id).subquery()
        query = query\
            .join(start_sq, Activity.id == start_sq.c.parent_id)\
            .join(end_sq, Activity.id == end_sq.c.parent_id)\

    return query
