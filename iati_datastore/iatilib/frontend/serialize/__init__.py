from datetime import datetime
from .csv import (
    csv, csv_activity_by_country, csv_activity_by_sector,
    transaction_csv, csv_transaction_by_country, csv_transaction_by_sector,
    budget_csv, csv_budget_by_country, csv_budget_by_sector)

from .jsonserializer import json, datastore_json


def xml(pagination):
    yield u"""<result>
    <ok>True</ok>
    <iati-activities generated-datetime='{3}'>
      <query>
        <total-count>{0}</total-count>
        <start>{1}</start>
        <limit>{2}</limit>
      </query>
    """.format(pagination.total,
            pagination.offset, pagination.limit, datetime.now().isoformat())
    for activity in pagination.items:
        yield activity.raw_xml
    yield u"</iati-activities></result>"
