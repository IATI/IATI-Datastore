import os
from flask import Flask
from flask.ext.rq import RQ

from iatilib import db


def create_app(**config):
    app = Flask('iatilib.frontend')

    app.config.update(config)

    if "SQLALCHEMY_DATABASE_URI" not in app.config:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]

    if "REDISTOGO_URL" in os.environ:
        app.config["RQ_LOW_URL"] = os.environ["REDISTOGO_URL"]

    db.app = app  # don't understand why I need to this
    db.init_app(app)

    RQ(app)

    @app.route('/')
    def homepage():
        return app.send_static_file('index.html')

    from .api1 import api

    app.register_blueprint(api, url_prefix="/api/1")
    return app
