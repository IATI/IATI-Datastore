import sqlalchemy as sa
import prettytable
from flask.ext.script import Manager


from iatilib.frontend import create_app, db
from iatilib import magic_numbers
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








if __name__ == "__main__":
    manager.run()
