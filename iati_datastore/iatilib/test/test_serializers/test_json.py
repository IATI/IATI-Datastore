from datetime import datetime
import json
from StringIO import StringIO
import mock
from iatilib import codelists
from iatilib.frontend.serialize import jsonserializer
from iatilib.test import factories, AppTestCase

class FakePage(object):
    def __init__(self, items):
        self.items = items

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
                    flow_type=codelists.FlowType.private_grants,
                    finance_type=codelists.FinanceType.aid_grant_excluding_debt_reorganisation,
                    aid_type=codelists.AidType.general_budget_support,
                    disbursement_channel=codelists.DisbursementChannel.aid_in_kind_donors_manage_funds_themselves,
                    tied_status=codelists.TiedStatus.untied,
                )

        json_output = jsonserializer.json(FakePage([activity]))
        output = json.load(StringIO(json_output))

        transactions = {
            "transaction-type": { "-code": "C" },
            "value": {
                "-value-date": "2012-12-31",
                "#text": "4119000.00"
            },
            "transaction-date": { "-iso-date": "2012-12-31" },
            "flow-type": { "-code": "30" },
            "finance-type": { "-code": "110" },
            "aid-type": { "-code": "A01" },
            "disbursement-channel": { "-code": "4" },
            "tied-status": { "-code": "5" }
        }
        self.assertItemsEqual(transactions, output['results'][0]['transactions'][0])
