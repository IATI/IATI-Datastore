from StringIO import StringIO

import unicodecsv


def load_csv(data):
    sio = StringIO(data)
    return list(unicodecsv.DictReader(sio, encoding="utf-8"))


class CSVTstMixin(object):
    def process(self, data):
        return load_csv(self.serialize(data))

    def serialize(self, data):
        raise Exception("Not Implemented")

    def assertField(self, mapping, row):
        assert len(mapping) == 1
        key, val = mapping.items()[0]
        self.assertIn(key, row)
        self.assertEquals(row[key], val)
