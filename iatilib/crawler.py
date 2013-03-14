import datetime
import logging

import requests
import ckanclient
from dateutil.parser import parse as date_parser
from flask.ext.rq import get_queue

from iatilib import db, parse
from iatilib.model import Dataset, Resource

log = logging.getLogger("crawler")


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
    return existing_datasets + new_datasets


def fetch_dataset_metadata(dataset):
    ds_entity = registry.package_entity_get(dataset.name)
    dataset.last_modified = date_parser(ds_entity.get('metadata_modified', ""))
    new_urls = [resource['url'] for resource
                in ds_entity.get('resources', [])
                if resource['url'] not in dataset.resource_urls]
    dataset.resource_urls.extend(new_urls)
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
        headers["If-None-Match"] = resource.etag.encode('ascii')
    resp = requests.get(resource.url, headers=headers)
    resource.last_status_code = resp.status_code
    resource.last_fetch = datetime.datetime.utcnow()
    if resp.status_code == 200:
        resource.document = resp.content
        if "etag" in resp.headers:
            resource.etag = resp.headers.get('etag').decode('ascii')
        else:
            resource.etag = None
        resource.last_succ = datetime.datetime.utcnow()
        resource.last_parsed = None
        resource.last_parse_error = None
    if resp.status_code == 304:
        resource.last_succ = datetime.datetime.utcnow()
    db.session.add(resource)
    return resource


def parse_resource(resource):
    db.session.add(resource)
    try:
        resource.activities = list(parse.document(resource.document))
        log.info(
            "Parsed %d activities from %s",
            len(resource.activities),
            resource.url)
        resource.last_parsed = datetime.datetime.utcnow()
    except parse.ParserError, exc:
        resource.last_parse_error = str(exc)
    return resource


def update_resource(resource_url):
    resource = fetch_resource(Resource.query.get(resource_url))
    db.session.commit()

    if resource.last_status_code == 200:
        parse_resource(resource)
        db.session.commit()


def update_dataset(dataset_name):
    rq = get_queue()
    dataset = Dataset.query.get(dataset_name)
    fetch_dataset_metadata(dataset)
    db.session.commit()
    need_update = [r for r in dataset.resources
                   if not r.last_succ or r.last_succ < dataset.last_modified]
    for resource in need_update:
        rq.enqueue(update_resource, args=(resource.url,), result_ttl=0)


from flask.ext.script import Manager
manager = Manager(usage="Crawl IATI registry")


@manager.command
def dataset_list():
    fetch_dataset_list()
    db.session.commit()


@manager.command
def metadata(verbose=False):
    for dataset in Dataset.query.all():
        if verbose:
            print "Fetching metadata for %s" % dataset.name
        fetch_dataset_metadata(dataset)
        db.session.commit()


@manager.command
def documents(verbose=False):
    for dataset in Dataset.query.all():
        if verbose:
            print "Fetching documents for %s" % dataset.name
        for resource in dataset.resources:
            if verbose:
                print "Fetching %s" % resource.url,
            fetch_resource(resource)
            if verbose:
                print resource.last_status_code
            db.session.commit()


@manager.option('--limit', action="store", type=int,
                help="max no of datasets to update")
@manager.option('-v', '--verbose', action="store_true")
def update(verbose=False, limit=None):
    rq = get_queue()

    fetch_dataset_list()
    db.session.commit()

    datasets = Dataset.query
    if limit:
        datasets = datasets.limit(limit)

    print "Enqueing %d datasets for update" % datasets.count()
    for dataset in datasets:
        if verbose:
            print "Enquing %s" % dataset.name
        rq.enqueue(update_dataset, args=(dataset.name,), result_ttl=0)
