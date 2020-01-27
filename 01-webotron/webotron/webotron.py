#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Webotron: Deploy websites with AWS.

webotron automates process of deploying static websites to AWS
- Configure AWS S3 bucketd
    - Create s3 bucket
    - Setup s3 bucket for static website hosting
    - Deploy local files to s3 bucket
- Configure DNS with AWS Route 53
- Configure a Content Delivery Network and SSL with AWS Cloudfront
"""

import boto3
import click

from bucket import BucketManager
from domain import DomainManager
from certificate import CertificateManager
import util

# s3 = session.resource('s3')
session = None
bucket_manager = None
domain_manager = None
certificate_manager = None

@click.group()
@click.option('--profile', default=None,
    help="Use a given AWS profile.")
def cli(profile):
    """Webotron deploys websites to aws."""
    global session, bucket_manager, domain_manager, certificate_manager
    session_cfg = {}
    if profile:
        session_cfg['profile_name'] = profile
    session = boto3.Session(**session_cfg)
    bucket_manager = BucketManager(session)
    domain_manager = DomainManager(session)
    certificate_manager = CertificateManager(session)


@cli.command('list-buckets')
def list_buckets():
    """List all S3 buckets."""
    # for bucket in bucket_manager.s3.buckets.all():
    for bucket in bucket_manager.all_buckets():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List Objects in S3 bucket."""
    for obj in bucket_manager.all_objects(bucket):
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create and Configure website in S3 bucket."""
    s3_bucket = bucket_manager.init_bucket(bucket)
    bucket_manager.set_policy(s3_bucket)
    bucket_manager.configure_website(s3_bucket)

    return


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Synch contents of PATHNAME to Bucket."""
    bucket_manager.sync(pathname, bucket)
    print(bucket_manager.get_bucket_url(bucket_manager.s3.Bucket(bucket)))


@cli.command('setup-domain')
@click.argument('domain')
@click.argument('bucket')
def setup_domain(domain, bucket):
    """Configure Domain to point to S3 Bucket."""
    bucket = bucket_manager.get_bucket(bucket)

    zone = domain_manager.find_hosted_zone(domain) \
        or domain_manager.create_hosted_zone(domain)

    endpoint = util.get_endpoint(bucket_manager.get_region_name(bucket))
    a_record = domain_manager.create_s3_domain_record(zone, domain, endpoint)
    print('Domain Configure: http://{}'.format(domain))
    print(a_record)


@cli.command('find-cert')
@click.argument('domain')
def find_cert(domain):
    """Searches issued matching certificate."""
    print(certificate_manager.find_matching_cert(domain))

if __name__ == '__main__':
    cli()
