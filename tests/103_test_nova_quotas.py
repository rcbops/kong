# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack, LLC
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Functional test case against the OpenStack Nova API for quotas"""

import json
import os
import tempfile
import unittest
import httplib2
import urllib
import hashlib
import random
import time
import os

from novaclient import exceptions as novacli_exceptions
from pprint import pprint

import tests


class TestNovaQuotas(tests.NovaFunctionalTest):

    def raw_quota(self):
        return {'instances': 10, 'cores': 20, 'ram': 51200, 'volumes': 10,
                'floating_ips': 10, 'metadata_items': 128, 'gigabytes': 1000,
                'injected_files': 5, 'injected_file_content_bytes': 10240,
                'id': self.TEST_ALT_TENANT}

    def reset_quotas(self):
        self.admincli.quotas.update(self.TEST_ALT_TENANT,
            instances=10, cores=20, ram=51200, volumes=10,
            floating_ips=10, metadata_items=128, gigabytes=1000,
            injected_files=5, injected_file_content_bytes=10240)

    def setUp(self):
        super(TestNovaQuotas, self).setUp()
        self.reset_quotas()

    def tearDown(self):
        super(TestNovaQuotas, self).tearDown()
        self.reset_quotas()

    def test_001_test_quota_defaults(self):
        quota_set = self.novacli.quotas.defaults(self.TEST_ALT_TENANT)
        self.assertEqual(quota_set._info, self.raw_quota())

    def test_002_test_quota_get_as_authorized_user(self):
        quota_set = self.novacli.quotas.get(self.TEST_ALT_TENANT)
        self.assertEqual(quota_set._info, self.raw_quota())

    def test_003_test_quota_get_as_unauthorized_user(self):
        try:
            self.novacli.quotas.get(self.TEST_TENANT)
        except novacli_exceptions.Forbidden as e:
            self.assertEqual(str(e), 'Forbidden (HTTP 403)')

    def test_004_test_quota_update(self):
        self.admincli.quotas.update(self.TEST_ALT_TENANT, volumes=999)
        quota_set = self.admincli.quotas.get(self.TEST_ALT_TENANT)
        self.assertEqual(quota_set.volumes, 999)

    def test_005_test_instance_quotas(self):
        self.admincli.quotas.update(self.TEST_ALT_TENANT, instances=1)

        # launch 2 instances using ami-tty, and m1.tiny
        servers = []
        for i in range(2):
            try:
                servers.append(self.novacli.servers.create('test_%s' % i,
                                                            3, 1))
            except novacli_exceptions.ClientException as e:
                self.assertEqual(e.message.split(":")[0],
                                 "InstanceLimitExceeded")
        # cleanup created servers
        for server in servers:
            self.novacli.servers.delete(server)
        self.reset_quotas()
