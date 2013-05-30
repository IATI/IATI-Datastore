from .csv import (
    csv, csv_activity_by_country, csv_activity_by_sector,
    transaction_csv, csv_transaction_by_country, csv_transaction_by_sector,
    budget_csv, csv_budget_by_country, csv_budget_by_sector)

from .json import json


def xml(pagination):
    out = u"""<result>
    <ok>True</ok>
    <number-of-results>{0}</number-of-results>
    <page>{1}</page>
    <per_page>{2}</per_page>
    <result-activity>""".format(pagination.total, pagination.page, pagination.per_page)
    for activity in pagination.items:
        out += activity.raw_xml
    out += u"</result-activity></result>"
    return out
