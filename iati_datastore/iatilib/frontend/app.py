import os

from flask import Flask
from flask_rq import RQ

from iatilib import db, redis

from .api1 import api
from iatilib.frontend.routes import routes
from iatilib.crawler import manager as crawler_manager
from iatilib.queue import manager as queue_manager

def create_app(config_object='iatilib.config'):
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    return app

def register_blueprints(app):
    app.register_blueprint(routes, url_prefix="")
    app.register_blueprint(api, url_prefix="/api/1")
    app.register_blueprint(crawler_manager)
    app.register_blueprint(queue_manager)

def register_extensions(app):
    db.init_app(app)
    redis.init_app(app)
    RQ(app)
