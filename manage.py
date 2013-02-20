import sqlalchemy as sa
import prettytable
from flask.ext.script import Manager


from iatilib.frontend import create_app, db
from iatilib import magic_numbers, parser
from iatilib.model import IndexedResource, RawXmlBlob

manager = Manager(create_app())


def qtable(itr, headers=None):
    if headers is None:
        headers = next(itr)
    tbl = prettytable.PrettyTable(headers)
    for row in itr:
        tbl.add_row(row)
    return tbl


@manager.command
def status():
    print "Database: %s" % manager.app.config["SQLALCHEMY_DATABASE_URI"]
    print

    resource_status = db.session.query(
        IndexedResource.state, sa.func.count()).group_by(IndexedResource.state)

    print "Download"
    print qtable(
        ((magic_numbers.label[n], c) for n, c in resource_status),
        ["state", "no of urls"])

    print "Parsing"
    parse_status = db.session.query(
        RawXmlBlob.parsed, sa.func.count()).group_by(RawXmlBlob.parsed)
    print qtable(parse_status, ["status", "no of blobs"])


@manager.command
def parse_blob(blob_id, pdb=False):
    """
    Parse a blob by id, don't insert into the db (debugging tool)
    """
    blob = RawXmlBlob.query.get(blob_id)
    print "Blob %s parsed status=%r" % (blob.id, blob.parsed)
    if pdb:
        try:
            import ipdb; ipdb.set_trace()
        except ImportError:
            import pdb; pdb.set_trace()
    activity, errors = parser.parse(blob.raw_xml)
    print "activity", activity
    print "activity.id", activity.id
    print "errors", errors









if __name__ == "__main__":
    manager.run()
