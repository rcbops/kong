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

"""Functional test case against the OpenStack Nova API for floating ips"""

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
                'id': 'TEST_TENANT'}

    def setUp(self):
        super(TestNovaQuotas, self).setUp()

    def tearDown(self):
        super(TestNovaQuotas, self).tearDown()

    def test_001_test_quota_defaults(self):
        quota_set = self.novacli.quotas.defaults('TEST_TENANT')
        self.assertEqual(quota_set._info, self.raw_quota())

    def test_002_test_quota_get(self):
        quota_set = self.novacli.quotas.get('TEST_TENANT_ALT')
        self.assertEqual(quota_set._info, self.raw_quota())

    def test_003_test_quota_update(self):
        quota_set = self.novacli.quotas.get('TEST_TENANT_ALT')
        quota_set.update(volumes=999)
        self.assertEqual(quota_set.volumes, 999)
