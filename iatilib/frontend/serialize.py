from collections import OrderedDict


def date(date_type):
    def accessor(activity):
        dates = [d.iso_date.strftime("%Y-%m-%d")
                 for d in activity.date
                 if d.type == date_type]
        if dates:
            return dates[0]
        return ""
    return accessor


def first_text(attr):
    def accessor(activity):
        return getattr(activity, attr)[0].text or ""
    return accessor


def csv(query):
    fields = OrderedDict((
        ("iati-identifier", first_text("iatiidentifier")),
        ("reporting-org", first_text("reportingorg")),
        ("title", first_text("title")),
        ("start-planned", date("start-planned")),
        ))

    rows = []
    for activity in query:
        row = [accessor(activity) for accessor in fields.values()]
        rows.append(",".join(row))
    return ",".join(fields.keys()) + "\n" + "\n".join(rows)
