from setuptools import setup, find_packages

requirements = """
Flask==0.10.1
Jinja2==2.10
SQLAlchemy==0.8.7
Flask-SQLAlchemy==1.0
Werkzeug==0.8.3
ckanapi==4.1
iso8601==0.1.12
lxml==3.8.0
psycopg2==2.7.5
python-dateutil==2.4.2
six==1.11.0
unicodecsv==0.9.4
voluptuous==0.7.1
Flask-Script==0.5.3
prettytable==0.7.2
alembic==0.5.0
gunicorn==0.17.4
defusedxml==0.4.1
redis==2.10.6
rq==0.3.13
Unidecode==0.04.21
requests==2.19.1
Flask-RQ==0.2
flask-heroku==0.1.9
Flask-And-Redis==0.4
Flask-Markdown==0.3
xmltodict==0.7.0
gevent==0.13.8
"""

tests_require = """
nose==1.3.7
mock==1.3.0
factory-boy==1.3.0
coveralls==0.5
coverage==3.7.1
html==1.16
"""


setup(
    name='IATI-Datastore',
    version='0.6',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        # If any package contains a .csv file include it
        '': ['*.csv'],
        # static web resources
        'iatilib.frontend': ['static/*', "templates/*", "doc/*"]
    },
    zip_safe=False,
    install_requires=requirements.strip().splitlines(),
    tests_require=tests_require.strip().splitlines(),
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'iati = iatilib.console:main',
        ]
    }
)
