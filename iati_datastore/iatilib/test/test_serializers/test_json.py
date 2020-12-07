from datetime import datetime
import json
from io import StringIO
import mock
from iatilib import codelists
from iatilib.frontend.serialize import jsonserializer
from iatilib.test import factories, AppTestCase

class FakePage(object):
    def __init__(self, items):
        self.items = items
        self.offset = 0
        self.limit = 50

    @property
    def total(self):
        return len(self.items)

class TestJson(AppTestCase):
    maxDiff = None
    @mock.patch('iatilib.frontend.serialize.jsonserializer.current_app')
    def test_transaction_json(self, mock):
        mock.debug = True
        activity = factories.ActivityFactory.create()
        trans = factories.TransactionFactory.create(
                    activity=activity,
                    value_amount=411900,
                    value_date=datetime(2012, 12, 31),
                    date=datetime(2012, 12, 31),
                    flow_type=codelists.FlowType.private_ngo_and_other_private_sources,
                    finance_type=codelists.FinanceType.aid_grant_excluding_debt_reorganisation,
                    aid_type=codelists.AidType.general_budget_support,
                    disbursement_channel=codelists.DisbursementChannel.aid_in_kind_donors_manage_funds_themselves,
                    tied_status=codelists.TiedStatus.untied,
                )

        json_output = jsonserializer.datastore_json(FakePage([activity]))
        output = json.load(StringIO(json_output))

        transactions = {
            "transaction-type": { "code": "C" },
            "value": {
                "value-date": "2012-12-31",
                "text": "4119000.00"
            },
            "transaction-date": { "iso-date": "2012-12-31" },
            "flow-type": { "code": "30" },
            "finance-type": { "code": "110" },
            "aid-type": { "code": "A01" },
            "disbursement-channel": { "code": "4" },
            "tied-status": { "code": "5" }
        }
        self.assertCountEqual(transactions, output['iati-activities'][0]['transaction'][0])

    @mock.patch('iatilib.frontend.serialize.jsonserializer.current_app')
    def test_version(self, mock):
        activity = factories.ActivityFactory.create(version='x.yy')
        json_datastore_output = json.loads(jsonserializer.datastore_json(FakePage([activity])))
        json_output = json.loads(jsonserializer.json(FakePage([activity])))
        self.assertEquals('x.yy', json_datastore_output['iati-activities'][0]['version'])
        # This has the "iati-extra:" because it should match the XML output
        self.assertEquals('x.yy', json_output['iati-activities'][0]['iati-extra:version'])
