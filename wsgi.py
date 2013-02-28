from iatilib.frontend import create_app
import newrelic.agent

app = create_app()
app = newrelic.agent.wsgi_application()(app)
