import boto3
import click
session = boto3.Session(profile_name='apsraj01_manojs')
s3 = session.resource('s3')

@click.group()
def cli():
    "Webotron deploys websites to aws"
    pass

@cli.command('list-buckets')
def list_buckets():
    "List all S3 buckets"
    for bucket in s3.buckets.all():
        print(bucket)

@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    "List Objects in S3 bucket"
    for obj in s3.Bucket('apsraj01-manojs-pythonautomation-boto3').objects.all():
        print(obj)

if __name__ == '__main__':
    cli()
