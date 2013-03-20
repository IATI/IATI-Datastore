"""
Build & run acceptance tests.

These tests create an empty database, load a set of test data, retreive
results via the API and compair those results to an existing set.

Note: at the moment these only cover the csv formats.
"""

test_structure = """

Tests are directories containing a directory named "inputs" which holds
test data used to build the db, and another named "outputs" which holds
expected results.

For example - a test named 'dfid_drc' with several inputs & outputs:

acceptance_tests/dfid_drc
acceptance_tests/dfid_drc/inputs
acceptance_tests/dfid_drc/inputs/CD
acceptance_tests/dfid_drc/inputs/tearfund-cd.xml
acceptance_tests/dfid_drc/inputs/wvuk-cd.xml
acceptance_tests/dfid_drc/outputs
acceptance_tests/dfid_drc/outputs/transactions.csv
acceptance_tests/dfid_drc/outputs/transactions_by_country.csv
acceptance_tests/dfid_drc/outputs/transactions_by_sector.csv

"""

import os
import unicodecsv as csv
import html
import glob
import argparse
from collections import Counter


from iatilib import db, parse
from iatilib.frontend import create_app


def pairs(i1, i2):
    i1, i2 = iter(i1), iter(i2)
    try:
        while True:
            ii1 = next(i1)
            ii2 = next(i2)
            yield ii1, ii2
    except StopIteration:
        pass


def load_test_db(inputs):
    db.create_all()
    try:
        for fn in inputs:
            db.session.add_all(parse.document(fn))
    except parse.ParserError:
        print "Could not parse", fn
        raise
    else:
        db.session.commit()


class Results(Counter):
    def __init__(self):
        super(Results, self).__init__(passed=0, failed=0, errors=0)

    @property
    def passed(self):
        return self["failed"] == 0 and self["errors"] == 0

    def __str__(self):
        return "{0:d} passed {1:d} failed {2:d} errors ({3:d} total)".format(
            self["passed"], self["failed"], self["errors"],
            sum([self["passed"], self["failed"], self["errors"]])
        )


class HtmlReporter(object):
    def __init__(self):
        self.html = html.HTML()
        self.head()
        self.row = None
        self.table = None
        self.results = Results()

    def head(self):
        self.html.head.style(
            """
.pass {
    background-color: lightgreen
}

.fail {
    background-color: #CE8585
}

.err {
    background-color: #FFFF99
}

.note {
    font-size: small;
    color: lightgrey
}

hr {
    border: 0;
    height: 0;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}
            """, escape=False)

    def test_start(self, name):
        self.html.h1(name)

    def output_start(self, filename, url):
        self.html.h3("Filename: %s" % filename)
        self.html.h3("Url: %s" % url)
        self.table = self.html.table()

    def row_start(self):
        assert self.row is None
        self.row = self.table.tr()

    def row_end(self):
        self.row = None

    def _row_fail(self, exp):
        import ipdb; ipdb.set_trace()
        with self.table.tr() as row:
            row.td("missing")
            for i in exp:
                row.td(i)

    def row_missing(self, exp):
        return self._row_fail(exp)

    def row_extra(self, exp):
        return self._row_fail(exp)

    def cell_ok(self, exp, got):
        self.row.td(exp, klass="pass")
        self.results["passed"] += 1

    def cell_fail(self, exp, got):
        with self.row.td(klass="fail") as cell:
            cell.div.span('expected', klass="note")
            cell.div(exp)
            cell.hr()
            cell.div.span('got', klass="note")
            cell.div(got)
        self.results["failed"] += 1

    def cell_error(self, exp, got, exc):
        self.row.td(exp + "<hr>" + exc, klass="err")
        self.results["errors"] += 1


class Test(object):
    def __init__(self, app, inputs, outputs, name="Test"):
        self.app = app
        self.init_app(app)
        self.client = self.app.test_client()
        self.inputs = inputs
        self.outputs = outputs
        self.name = name

    def init_app(self, app):
        db.app = self.app
        db.init_app(self.app)

    def setup(self):
        load_test_db(self.inputs)

    def teardown(self):
        db.session.remove()
        db.drop_all()

    def run(self, reporter):
        reporter.test_start(name=self.name)
        for filename, url in self.outputs.items():
            resp_csv = csv.reader(self.client.get(url).data.splitlines())
            exp_csv = csv.reader(open(filename))
            reporter.output_start(filename, url)
            for rline, eline in pairs(resp_csv, exp_csv):
                reporter.row_start()
                for r, e in pairs(rline, eline):
                    try:
                        if r == e:
                            reporter.cell_ok(r, e)
                        else:
                            reporter.cell_fail(r, e)
                    except Exception, exc:
                        reporter.cell_error(r, e, exc)
                reporter.row_end()
            for line in resp_csv:
                reporter.row_missing(r)
            for line in exp_csv:
                reporter.row_extra(r)


base_url = "/api/1/access/"
input_url = {
    "transactions.csv": base_url + "transactions.csv",
    "transactions_by_sector.csv": base_url + "transactions/by_sector.csv",
    "transactions_by_country.csv": base_url + "transactions/by_country.csv",
    "activities.csv": base_url + "activities.csv",
    "activities_by_sector.csv": base_url + "activities/by_sector.csv",
    "activities_by_country.csv": base_url + "activities/by_country.csv",
    "budgets.csv": base_url + "budgets.csv",
    "budgets_by_sector.csv": base_url + "budgets/by_sector.csv",
    "budgets_by_country.csv": base_url + "budgets/by_country.csv",

}


def load_outputs(dirname):
    return {
        os.path.join(dirname, fn): input_url[os.path.basename(fn)]
        for fn in os.listdir(dirname)
    }


def load_inputs(dirname):
    return [infn for infn in glob.glob(
            "%s/*" % os.path.join(dirname, "inputs"))]


def create_test_app():
    return create_app(
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
    )


def test(args):
    root_dir = "acceptance_tests"
    app = create_test_app()
    agg_results = Results()
    for testdir in ["dfid_drc"]:
        test = Test(
            name=testdir,
            app=app,
            inputs=load_inputs(os.path.join(root_dir, testdir)),
            outputs=load_outputs(os.path.join(root_dir, testdir, "outputs")),
        )
        reporter = HtmlReporter()
        try:
            test.setup()
            test.run(reporter)

        finally:
            test.teardown()

        with open("acc_tests.html", "w") as outf:
            outf.write(str(reporter.html))
        if not reporter.results.passed:
            print "FAIL", testdir, reporter.results
        agg_results.update(reporter.results)
    if agg_results.passed:
        print "OK", agg_results
    else:
        print "FAIL", agg_results


def build(args):
    root_dir = "acceptance_tests"
    testdir = os.path.relpath(args.testdir, "acceptance_tests")
    app = create_test_app()
    inputs = load_inputs(os.path.join(root_dir, testdir))
    load_test_db(inputs)
    client = app.test_client()
    for output_fn, url in input_url.items():
        fn = os.path.join(root_dir, testdir, "outputs", output_fn)
        print "writing", fn
        with open(fn, "wb") as outf:
            outf.write(client.get(url).data)


def arg_parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=test_structure,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers()
    test_p = subparsers.add_parser(
        "test",
        help="Run tests",
    )
    test_p.set_defaults(func=test)
    build_p = subparsers.add_parser(
        "build",
        help="Build a test from a dir",
        description="Build a test by loading inputs then recording outputs",
    )
    build_p.add_argument(
        "testdir",
        help="The directory containing the inputs and outputs directories")
    build_p.set_defaults(func=build)
    return parser


def main():
    parser = arg_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    main()
