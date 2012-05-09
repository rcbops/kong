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
from utils import SERVICES
from resttest.jsontools import nested_search

r = SERVICES['keystone']
admin = SERVICES['keystone-admin']


class TestKeystoneAPI2(tests.FunctionalTest):
    tags = ['nova', 'nova-api', 'keystone']

    def test_keystone_d5_failed_auth(self):
        r.POST('/tokens',
               body={"passwordCredentials":
                      {"username": "bad",
                       "password": "bad"}},
               code=400)

    def test_keystone_v2_failed_auth(self):
        r.POST('/tokens',
               body={"auth": {"passwordCredentials":
                              {"username": "bad",
                               "password": "bad"}}},
                               code=401)

    def test_keystone_v2_successful_auth(self):
        r.POST('/tokens',
               body={"auth": {"passwordCredentials":
                              {"username": self.keystone['user'],
                               "password": self.keystone['pass']},
                                 "tenantId": self.keystone['tenantid']}},
               code=200)

    def test_keystone_d5_bad_key(self):
        r.POST('/tokens',
               body={"passwordCredentials":
                      {"username": self.keystone['user'],
                       "password": "badpass"}},
               code=401)

    def test_keystone_v2_bad_key(self):
        r.POST('/tokens',
               body={"auth": {"passwordCredentials":
                              {"username": self.keystone['user'],
                               "password": "badpass"}}},
               code=401)

    def test_keystone_d5_no_key(self):
        r.POST('/tokens',
               body={"passwordCredentials":
                      {"username": self.keystone['user']}},
               code=400)

    def test_keystone_v2_no_key(self):
        r.POST('/tokens',
               body={"auth": {"passwordCredentials":
                              {"username": self.keystone['user']}}},
               code=400)

    def test_keystone_v2_no_key_essex(self):
        r.POST('/tokens',
               body={"auth": {"passwordCredentials":
                              {"username": self.keystone['user']}}},
               code=401)

    def test_keystone_v2_check_token(self):
        admin.HEAD("/tokens/%s" % r.token, code=204)

    def test_keystone_v2_validate_token(self):
        admin.GET_with_keys_eq("/tokens/%s" % r.token,
                               {"/access/user/username": r.get_config()[1]},
                               code=200)

    def test_keystone_v2_validate_token_d5(self):
        admin.GET_with_keys_eq("/tokens/%s" % r.token,
                               {"/auth/user/username": r.get_config()[1]},
                               code=200)

    def test_keystone_v2_01_create_tenant(self):
        admin.POST('/tenants', body={"tenant": {
                                "name": "kongtenant",
                                "description": "description"}}, code=200)

    def test_keystone_v2_02_create_tenant_user(self):
        response, data = admin.GET("/tenants")
        kong_tenant = nested_search("/tenants/*/name=kongtenant/id", data)[0]
        user = {"user": {
                             "name": "kongadmin",
                             "password": "kongsecrete",
                             "tenantid": kong_tenant,
                             "email": ""}}
        admin.POST("/users", body=user, code=200)

    def test_keystone_v2_03_get_tenant_list_essex(self):
        response, d = admin.GET("/tenants", code=200)
        self.assertEqual(len(nested_search("/tenants/*/name=kongtenant", d)),
                         1)
        
    def test_keystone_v2_get_extension_list(self):
        response, d = admin.GET("/extensions", code=200)
        if not (type(d['extensions']['values']) == type([])):
            raise AssertionError("Returned extensions is not a list")
    
    def test_keystone_v2_04_delete_tenant(self):
        response, data = admin.GET("/tenants")
        kong_tenant = nested_search("/tenants/*/name=kongtenant/id", data)[0]
        admin.DELETE("/tenants/%s" % kong_tenant, code=204)

    def test_keystone_v2_05_delete_user(self):
        response, data = admin.GET("/users")
        kong_user = nested_search("/users/*/name=kongadmin/id", data)[0]
        admin.DELETE("/users/%s" % kong_user, code=204)
