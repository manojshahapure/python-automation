# -*- coding: utf-8 -*-

"""Classes for S3 buckets."""

from pathlib import Path
import mimetypes
from botocore.exceptions import ClientError
import util

class BucketManager:
    """Manage an S3 bucket."""

    def __init__(self, session):
        """Create a BucketManager object."""
        self.session = session
        self.s3 = self.session.resource('s3')

    def get_region_name(self, bucket):
        """Get the bucket's region name."""
        bucket_location = self.s3.meta.client.get_bucket_location(Bucket=bucket.name)
        return bucket_location["LocationConstraint"] or 'us-east-1'

    def get_bucket_url(self, bucket):
        """Get the website url for this bucket."""
        return "http://{}.{}".format(bucket.name,
            util.get_endpoint(self.get_region_name(bucket)).host)

    def all_buckets(self):
        """Get an iterator for all buckets."""
        return self.s3.buckets.all()

    def all_objects(self, bucket_name):
        """Get an iterator for all objects in S3."""
        return self.s3.Bucket(bucket_name).objects.all()

    def init_bucket(self, bucket_name):
        """Create or Get s3 bucket."""
        s3_bucket = None
        try:
            if self.session.region_name == 'us-east-1':
                s3_bucket = self.s3.create_bucket(
                    Bucket=bucket_name
                )
            else:
                s3_bucket = self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': self.session.region_name
                        }
                    )
        except ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket = self.s3.Bucket(bucket_name)
            else:
                raise error
        return s3_bucket

    def set_policy(self, bucket):
        """Set policy for my S3 bucket."""
        policy = """
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::%s/*"
                }
            ]
        }
        """ % bucket.name
        policy = policy.strip()
        pol = bucket.Policy()
        pol.put(Policy=policy)

    def configure_website(self, bucket):
        """Configure a website using this bucket."""
        bucket.Website().put(
            WebsiteConfiguration={
                'ErrorDocument': {
                    'Key': 'error.html'
                },
                'IndexDocument': {
                    'Suffix': 'index.html'
                }
            })

    @staticmethod
    def upload_file(bucket, path, key):
        """Upload path to S3 bucket at key."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            })

    def sync(self, pathname, bucket_name):
        """Sync directory structure to S3 bucket."""
        bucket = self.s3.Bucket(bucket_name)
        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for p in target.iterdir():
                if p.is_dir():
                    handle_directory(p)
                if p.is_file():
                    self.upload_file(
                        bucket,
                        str(p.as_posix()),
                        str(p.relative_to(root).as_posix())
                    )

        handle_directory(root)
