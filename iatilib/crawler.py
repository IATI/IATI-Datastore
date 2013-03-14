import datetime

import requests
import ckanclient
from dateutil.parser import parse as date_parser

from iatilib import db
from iatilib.model import Dataset


CKAN_WEB_BASE = 'http://iatiregistry.org/dataset/%s'
CKAN_API = 'http://iatiregistry.org/api'

registry = ckanclient.CkanClient(base_location=CKAN_API)


def fetch_dataset_list():
    existing_datasets = Dataset.query.all()
    existing_ds_names = set(ds.name for ds in existing_datasets)
    incoming_ds_names = set(registry.package_register_get())
    new_datasets = [Dataset(name=n) for n
                    in incoming_ds_names - existing_ds_names]
    db.session.add_all(new_datasets)
    db.session.commit()
    return existing_datasets + new_datasets


def fetch_dataset_metadata(dataset):
    ds_entity = registry.package_entity_get(dataset.name)
    dataset.last_modified = date_parser(ds_entity.get('metadata_modified', ""))
    dataset.resource_urls = [resource['url'] for resource
                             in ds_entity.get('resources', [])]
    db.session.add(dataset)
    return dataset


def http_date(dt):
    from wsgiref.handlers import format_date_time
    from time import mktime
    return format_date_time(mktime(dt.timetuple()))


def fetch_resource(resource):
    headers = {}
    if resource.last_succ:
        headers['If-Modified-Since'] = http_date(resource.last_succ)
    if resource.etag:
        headers["If-None-Match"] = resource.etag
    resp = requests.get(resource.url, headers=headers)
    resource.last_status_code = resp.status_code
    resource.last_fetch = datetime.datetime.utcnow()
    if resp.status_code == 200:
        resource.document = resp.text
        resource.etag = resp.headers.get('etag')
        resource.last_succ = datetime.datetime.utcnow()
    if resp.status_code == 304:
        resource.last_succ = datetime.datetime.utcnow()
    return resource


from flask.ext.script import Manager
manager = Manager(usage="Crawl IATI registry")


@manager.command
def dataset_list():
    fetch_dataset_list()


@manager.command
def metadata(verbose=False):
    for dataset in Dataset.query.all():
        if verbose:
            print "Fetching metadata for %s" % dataset.name
        db.session.add(fetch_dataset_metadata(dataset))
        db.session.commit()


@manager.command
def documents(verbose=False):
    for dataset in Dataset.query.all():
        if verbose:
            print "Fetching documents for %s" % dataset.name
        for resource in dataset.resources:
            if verbose:
                print "Fetching %s" % resource.url,
            resource = fetch_resource(resource)
            if verbose:
                print resource.last_status_code
            db.session.add(resource)
            db.session.commit()

