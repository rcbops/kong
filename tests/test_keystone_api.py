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

"""Functional test case against the OpenStack Nova API server"""

import json
import os
import tempfile
import unittest
import httplib2
import urllib
import hashlib
import time
import os
import tests
import subprocess
from pprint import pprint


class TestKeystoneAPI(tests.FunctionalTest):
    def test_001_bad_user_bad_key(self):
        path = self.nova['path']
        http = httplib2.Http()
        if not self.keystone:
            headers = {'X-Auth-User': 'unknown_auth_user',
                      'X-Auth-Key': 'unknown_auth_key'}
            response, content = http.request(path, 'GET', headers=headers)
        else:
            path = path + "/tokens"
            body = self._keystone_json('unknown_auth_user',
                                       'unknown_auth_key',
                                       self.keystone['tenantid'])
            response, content = http.request(path,
                                'POST',
                                body,
                                headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status, 401)
    test_001_bad_user_bad_key.tags = ['nova', 'nova-api', 'keystone']

    def test_002_bad_user_good_key(self):
        path = self.nova['path']
        http = httplib2.Http()
        if not self.keystone:
            headers = {'X-Auth-User': 'unknown_auth_user',
                      'X-Auth-Key': self.nova['key']}
            response, content = http.request(path, 'GET', headers=headers)
        else:
            path = path + "/tokens"
            body = self._keystone_json('unknown_auth_user',
                                       self.keystone['pass'],
                                       self.keystone['tenantid'])
            response, content = http.request(path,
                                'POST',
                                body,
                                headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status, 401)
    test_002_bad_user_good_key.tags = ['nova', 'nova-api', 'keystone']

    def test_003_good_user_bad_key(self):
        path = self.nova['path']
        http = httplib2.Http()
        if not self.keystone:
            headers = {'X-Auth-User': self.keystone['user'],
                      'X-Auth-Key': 'unknown_auth_key'}
            response, content = http.request(path, 'GET', headers=headers)
        else:
            path = path + "/tokens"
            body = self._keystone_json(self.keystone['user'],
                                       'unknown_auth_key',
                                       self.keystone['tenantid'])
            response, content = http.request(path,
                                'POST',
                                body,
                                headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status, 401)
    test_003_good_user_bad_key.tags = ['nova', 'nova-api', 'keystone']

    def test_004_no_key(self):
        path = self.nova['path']
        http = httplib2.Http()
        if not self.keystone:
            headers = {'X-Auth-User': self.keystone['user']}
            response, content = http.request(path, 'GET', headers=headers)
        else:
            path = path + "/tokens"
            body = self._keystone_json(self.keystone['user'],
                                       '',
                                       self.keystone['tenantid'])
            response, content = http.request(path,
                                'POST',
                                body,
                                headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status, 401)
    test_004_no_key.tags = ['nova', 'nova-api', 'keystone']

    def test_005_bad_token(self):
        path = self.nova['path']
        http = httplib2.Http()
        if not self.keystone:
            headers = {'X-Auth-Token': 'unknown_token'}
            response, content = http.request(path, 'GET', headers=headers)
        else:
            path = path + "/tokens"
            body = self._keystone_json('',
                                       self.keystone['pass'],
                                       self.keystone['tenantid'])
            response, content = http.request(path,
                                'POST',
                                body,
                                headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status, 401)
    test_005_bad_token.tags = ['nova', 'nova-api', 'keystone']

    def test_006_no_tenant(self):
        path = self.nova['path'] + "/tokens"
        http = httplib2.Http()
        body = {"passwordCredentials": {
            "username": self.keystone['user'],
            "password": self.keystone['pass']}}
        body = json.dumps(body)
        response, content = http.request(path,
                            'POST',
                            body,
                            headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status, 401)
    test_006_no_tenant.tags = ['nova', 'nova-api', 'keystone']

    # @tests.skip_test("Currently Not Working")
    def test_007_get_tenant_list(self):
        path = "http://%s:%s/%s/tenants" % (self.keystone['host'],
                                           self.keystone['admin_port'],
                                           self.keystone['apiver'])
        http = httplib2.Http()
        response, content = http.request(path,
                            'GET',
                            headers={'Content-Type': 'application/json',
                                 'X-Auth-Token': self.nova['X-Auth-Token']})
        self.assertEqual(response.status, 200)
    test_007_get_tenant_list.tags = ['nova', 'nova-api', 'keystone']

    def test_008_get_extension_list(self):
        path = "http://%s:%s/%s/extensions" %(self.keystone['host'],
                                              self.keystone['admin_port'],
                                              self.keystone['apiver'])
        http = httplib2.Http()
        response, content = http.request(path,
                            'GET',
                            headers={'Content-Type': 'application/json',
                                     'X-Auth-Token': self.nova['X-Auth-Token']
                                    })
        self.assertEqual(response.status, 200)
        json_return = json.loads(content)
        self.assertEqual(json_return['extensions']['values'], [])
    test_008_get_extension_list.tags = ['nova', 'nova-api', 'keystone']
