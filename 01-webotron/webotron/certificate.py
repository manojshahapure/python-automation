# -*- coding: utf-8 -*-

"""Classes for ACM certificates."""

from pprint import pprint

class CertificateManager:
    """Manage ACM Certificates."""

    def __init__(self, session):
        """Creates ACM Certificate object."""
        self.session = session
        self.acm_client = self.session.client('acm', region_name='us-east-1')


    def cert_matches(self, cert_arn, domain_name):
        cert_details = self.acm_client.describe_certificate(CertificateArn=cert_arn)
        alt_names = cert_details['Certificate']['SubjectAlternativeNames']
        for name in alt_names:
            print('Name:' + name)
            if name == domain_name:
                return True
            if name[0] == '*' and domain_name.endswith(name[1:]):
                return True

        return False

    def find_matching_cert(self, domain_name):
        paginator = self.acm_client.get_paginator('list_certificates')
        for page in paginator.paginate(CertificateStatuses=['ISSUED']):
            for cert in page['CertificateSummaryList']:
                if self.cert_matches(cert['CertificateArn'], domain_name):
                    return cert

        return None
