import os

from flask import Flask
from flask.ext.rq import RQ
from flask.ext.heroku import Heroku
from flaskext.markdown import Markdown

from iatilib import db, redis


def create_app(**config):
    app = Flask('iatilib.frontend')

    app.config.update(config)

    Heroku(app)

    if "REDISTOGO_URL" in os.environ:
        app.config.update({
            'RQ_DEFAULT_HOST': app.config["REDIS_HOST"],
            'RQ_DEFAULT_PORT': app.config["REDIS_PORT"],
            'RQ_DEFAULT_PASSWORD': app.config['REDIS_PASSWORD']
        })

    db.init_app(app)
    redis.init_app(app)

    RQ(app)
    Markdown(app, extensions=['tables'])

    @app.route('/')
    def homepage():
        from flask import render_template
        with app.open_resource('docs/index.md') as f:
            contents = f.read()
        return render_template('doc.html', doc=contents)

    @app.route('/error')
    def error():
        from flask import render_template
        with app.open_resource('docs/error.md') as f:
            contents = f.read()
        return render_template('doc.html', doc=contents)

    from .api1 import api

    app.register_blueprint(api, url_prefix="/api/1")
    return app
