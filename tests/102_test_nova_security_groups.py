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


class TestNovaSecurityGroups(tests.NovaFunctionalTest):
    def setUp(self):
        super(TestNovaSecurityGroups, self).setUp()
        # using the default security group for now...
        self.TEST_GROUP_NAME = "default"
        self.TEST_GROUP_DESC = "default_desc"
        for group in self.novacli.security_groups.list():
            group.delete()

    def tearDown(self):
        super(TestNovaSecurityGroups, self).tearDown()

    def test_001_test_create_and_delete(self):
        group = self.novacli.security_groups.create(self.TEST_GROUP_NAME,
                                                    self.TEST_GROUP_DESC)
        self.assertTrue(self.novacli.security_groups.get(group.id))
        group.delete()

        with self.assertRaises(novacli_exceptions.NotFound):
            self.novacli.security_groups.get(group.id)

    def test_002_test_security_group_rules(self):
        group = self.novacli.security_groups.create(self.TEST_GROUP_NAME,
                                                    self.TEST_GROUP_DESC)

        self.assertTrue(self.novacli.security_groups.get(group.id))

        rule = self.novacli.security_group_rules.create(group.id,
                                                        'icmp',
                                                        '-1',
                                                        '-1',
                                                        '0.0.0.0/0')

        server = self.novacli.servers.create(name="sgtest%s" % random.random(),
                                             flavor=self.nova['flavor_id'],
                                             image=self.nova['image_id'])

        addr = server.addresses[0]['addr']
        self.assertTrue(self.is_pingable(addr))

        server.delete()
        group.delete()
