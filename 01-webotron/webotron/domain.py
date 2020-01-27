# -*- coding: utf-8 -*-

"""Classes for Route 53 domains."""

import uuid

class DomainManager:
    """Manage a Route 53 domain."""

    def __init__(self, session):
        """Create DomainManager Object."""
        self.session = session
        self.route53_client = self.session.client('route53')


    def find_hosted_zone(self, domain_name):
        paginator = self.route53_client.get_paginator('list_hosted_zones')
        for page in paginator.paginate():
            for zone in page['HostedZones']:
                if domain_name.endswith(zone['Name'][:-1]):
                    return zone

        return None

    def create_hosted_zone(self, domain_name):
        """Create hosted zone for our domain."""
        zone_name = '.'.join(domain_name.split('.')[:-2]) + '.'
        return self.route53_client.create_hosted_zone(
            Name='zone_name',
            CallerReference=str(uuid.uuid4())
        )

    def create_s3_domain_record(self, zone, domain_name, endpoint):
        """Creates A record for given domain name."""
        print(zone, domain_name, endpoint.host)
        return self.route53_client.change_resource_record_sets(
        HostedZoneId=zone['Id'],
        ChangeBatch={
            'Comment': 'Created by webotron',
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domain_name,
                        'Type': 'A',
                        'AliasTarget': {
                            'HostedZoneId': endpoint.zone,
                            'DNSName': endpoint.host,
                            'EvaluateTargetHealth': False
                            }
                        }
                    }
                ]
            }
        )
