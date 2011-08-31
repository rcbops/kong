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

"""Simple integration tests against the OpenStack Nova API"""

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

from pprint import pprint

import tests


class TestNovaBasics(tests.NovaFunctionalTest):
    def setUp(self):
        super(TestNovaBasics, self).setUp()
        for server in self.novacli.servers.list():
            server.delete()

    def tearDown(self):
        super(TestNovaBasics, self).tearDown()
        for server in self.novacli.servers.list():
            server.delete()

    def test_001_test_server_launch(self):
        self.novacli.servers.create(name="test %s" % random.random(),
                                    flavor=self.nova['flavor_id'],
                                    image=self.nova['image_id'])
        self.assertEqual(len(self.novacli.servers.list()), 1)
