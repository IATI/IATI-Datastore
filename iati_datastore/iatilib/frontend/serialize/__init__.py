from datetime import datetime
from lxml import etree as ET
from .csv import (
    csv, csv_activity_by_country, csv_activity_by_sector,
    transaction_csv, csv_transaction_by_country, csv_transaction_by_sector,
    budget_csv, csv_budget_by_country, csv_budget_by_sector)

from .jsonserializer import json, datastore_json


def xml(pagination):
    yield """<result xmlns:iati-extra="http://datastore.iatistandard.org/ns">
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
        if activity.version:
            # This should always work, as the first element in the raw_xml should always be iati-activity
            # And is lower overhead than using a proper XML parser again here
            yield str(activity.raw_xml.replace('<iati-activity', '<iati-activity iati-extra:version="{}"'.format(activity.version), 1))
        else:
            yield str(activity.raw_xml)
    yield "</iati-activities></result>"
