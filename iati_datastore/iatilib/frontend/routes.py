from flask import Blueprint, current_app
import markdown
import markdown.extensions.tables
from flask import Markup

routes = Blueprint('routes', __name__, template_folder='templates')

@routes.route('/')
def homepage():
    from flask import render_template
    with current_app.open_resource('frontend/docs/index.md') as f:
        contents = f.read().decode("utf-8")
    markdown_string = markdown.markdown(
        contents, extensions=["tables"]
    )
    return render_template('doc.html', markdown_string=Markup(markdown_string))

@routes.route('/error')
def error():
    from flask import render_template
    with current_app.open_resource('frontend/docs/error.md') as f:
        contents = f.read().decode("utf-8")
    markdown_string = markdown.markdown(
        contents, extensions=["tables"]
    )
    return render_template('doc.html', markdown_string=Markup(markdown_string))