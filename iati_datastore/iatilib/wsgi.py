from iatilib.frontend.app import create_app

app = create_app()

try:
    import newrelic.agent
    app = newrelic.agent.wsgi_application()(app)
except ImportError:
    pass
