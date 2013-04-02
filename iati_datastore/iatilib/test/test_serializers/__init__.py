from StringIO import StringIO

import unicodecsv


def load_csv(data):
    sio = StringIO(data)
    return list(unicodecsv.DictReader(sio, encoding="utf-8"))


class CSVTstMixin(object):
    def process(self, data):
        csv_str = u"".join(self.serialize(data)).encode('utf-8')
        return load_csv(csv_str)

    def serialize(self, data):
        raise Exception("Not Implemented")

    def assertField(self, mapping, row):
        assert len(mapping) == 1
        key, val = mapping.items()[0]
        self.assertIn(key, row)
        self.assertEquals(row[key], val)
