from setuptools import setup, find_packages

requirements = """
Flask==1.1.2
Flask-SQLAlchemy==2.4.4
ckanapi==4.5
lxml==4.6.2
python-dateutil==2.8.1
six==1.15.0
voluptuous>=0.12.0
alembic==1.4.3
gunicorn==20.0.4
Unidecode==1.1.1
requests==2.25.0
xmltodict==0.12.0
gevent>=20.9.0
Markdown==3.3.3
Flask-RQ==0.2
Flask-And-Redis==1.0.0
redis==3.5.3
rq==1.7.0
"""

tests_require = """
nose==1.3.7  # rq.filter: <2.0
mock==4.0.2  # rq.filter: <2.0
factory-boy==3.1.0  # rq.filter: <2.0
coveralls==2.2.0  # rq.filter: <0.6
coverage==5.3  # rq.filter: <4.0
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
            'iati = iatilib.console:cli',
        ]
    }
)
