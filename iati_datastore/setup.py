from setuptools import setup, find_packages

requirements = """
Flask==0.10
Jinja2==2.6
SQLAlchemy==0.8
Flask-SQLAlchemy==1.0
Werkzeug==0.8.3
ckanapi==1.5
iso8601==0.1.4
lxml==3.4.1
psycopg2==2.4.6
python-dateutil==2.1
six==1.2.0
unicodecsv==0.9.4
voluptuous==0.7.1
Flask-Script==0.5.3
prettytable==0.7
alembic==0.5.0
gunicorn==0.17.2
defusedxml==0.4
redis==2.7.2
rq==0.3.7
Unidecode==0.04.12
requests==2.5.1
Flask-RQ==0.2
flask-heroku==0.1.4
Flask-And-Redis==0.4
Flask-Markdown==0.3
xmltodict==0.7.0
gevent>=0.13.8
"""

tests_require = """
mock==1.0.1
factory-boy==1.2.0
nose==1.2.1
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
