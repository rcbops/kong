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

    INSTANCE_LIMIT = 1
    CORE_LIMIT = 2
    RAM_LIMIT = 512
    FLOATING_IP_LIMIT = 2
    INJECTED_FILE_LIMIT = 10
    INJECTED_FILESIZE_LIMIT = 10
    METADATA_LIMIT = 5
    VOLUME_LIMIT = 1
    GIGABYTE_LIMIT = 1

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

    def cleanup_instances(self):
        [self.novacli.servers.delete(server.id)
         for server in self.novacli.servers.list()]

    def get_all_server_flavors_info(self):
        return [self.novacli.flavors.get(server.flavor['id'])
                for server in self.novacli.servers.list()]

    def get_total_active_ram(self):
        return sum(f._info['ram'] 
                   for f in self.get_all_server_flavors_info())

    def get_total_active_cores(self):
        # NOTE(jakedahn): flavors api does not return cores value, stubbing
        # for now... Uncomment the second return when it is implemented.

        return self.CORE_LIMIT
        # return sum(f._info['cores']
        #            for f in self.get_all_server_flavors_info())

    def get_total_active_injected_files(self):
        # NOTE(jakedahn): injected files are not currently accessable,
        # uncomment below lines when they become present in the api.
        return 0
        # servers =  [self.novacli.flavors.get(server.flavor['id'])
        #             for server in self.novacli.servers.list()]
        # return sum(len(server._info['injected_files']) for server in servers)

    def get_total_active_injected_filesize(self):
        # NOTE(jakedahn): injected filesizes are not currently accessable,
        # uncomment below lines when they become present in the api.
        return 0
        # servers =  [self.novacli.flavors.get(server.flavor['id'])
        #             for server in self.novacli.servers.list()]
        # return sum(len(server._info['injected_file_content_bytes'])
        #                             for server in servers)

    def get_metadata_item_count(self):
        # NOTE(jakedahn): metadata is not currently accessable in the api,
        # uncomment below lines when they become present in the api.
        return 0
        # servers =  [self.novacli.flavors.get(server.flavor['id'])
        #             for server in self.novacli.servers.list()]
        # return sum(len(server._info['injected_file_content_bytes'])
        #                             for server in servers)
    
    def setUp(self):
        super(TestNovaQuotas, self).setUp()
        self.cleanup_instances()
        self.reset_quotas()

    def tearDown(self):
        super(TestNovaQuotas, self).tearDown()
        self.cleanup_instances()
        self.reset_quotas()

    # def test_001_test_quota_defaults(self):
    #     quota_set = self.novacli.quotas.defaults(self.TEST_ALT_TENANT)
    #     self.assertEqual(quota_set._info, self.raw_quota())
    # 
    # def test_002_test_quota_get_as_authorized_user(self):
    #     quota_set = self.novacli.quotas.get(self.TEST_ALT_TENANT)
    #     self.assertEqual(quota_set._info, self.raw_quota())
    # 
    # def test_003_test_quota_get_as_unauthorized_user(self):
    #     with self.assertRaises(novacli_exceptions.Forbidden):
    #         self.novacli.quotas.get(self.TEST_TENANT)
    # 
    def test_004_test_quota_update(self):
        self.admincli.quotas.update(self.TEST_ALT_TENANT, volumes=999)
        quota_set = self.admincli.quotas.get(self.TEST_ALT_TENANT)
        self.assertEqual(quota_set.volumes, 999)
    
    # def test_005_test_instance_quotas(self):
    #     self.admincli.quotas.update(self.TEST_ALT_TENANT,
    #                                 instances=self.INSTANCE_LIMIT)
    #     with self.assertRaises(novacli_exceptions.ClientException):
    #         for i in xrange(self.INSTANCE_LIMIT+1):
    #             self.novacli.servers.create('kong_%s' % i, 3, 1)
    #     self.assertEqual(len(self.novacli.servers.list()),
    #                          self.INSTANCE_LIMIT)
    # 
    # def test_006_test_ram_quotas(self):
    #     self.admincli.quotas.update(self.TEST_ALT_TENANT,ram=self.RAM_LIMIT)
    #     with self.assertRaises(novacli_exceptions.ClientException):
    #         for i in xrange(5):
    #             self.novacli.servers.create('kong_%s' % i, 3, 1)
    #     self.assertLessEqual(self.get_total_active_ram(), self.RAM_LIMIT)
    #     self.assertEqual(len(self.novacli.servers.list()), 1)
    # 
    # def test_007_test_cores_quotas(self):
    #     self.admincli.quotas.update(self.TEST_ALT_TENANT,
    #                                 cores=self.CORE_LIMIT)
    #     with self.assertRaises(novacli_exceptions.ClientException):
    #         for i in xrange(3):
    #             self.novacli.servers.create('kong_%s' % i, 3, 1)
    #     self.assertLessEqual(self.get_total_active_cores(), self.CORE_LIMIT)
    #     self.assertEqual(len(self.novacli.servers.list()), 0)

    # def test_008_test_injected_file_quotas(self):
    #     self.admincli.quotas.update(self.TEST_ALT_TENANT,
    #                                 injected_files=self.INJECTED_FILE_LIMIT)
    #     with self.assertRaises(novacli_exceptions.BadRequest):
    #         inject_files = {}
    #         for i in xrange(self.INJECTED_FILE_LIMIT+1):
    #             inject_files['key_%d' % i] = 'value %s' % i
    #         self.novacli.servers.create('kong_1', 3, 1, files=inject_files)
    #     self.assertLessEqual(self.get_total_active_injected_files(),
    #                      self.INJECTED_FILE_LIMIT)
    #     self.assertEqual(len(self.novacli.servers.list()), 0)

    # def test_009_test_injected_file_size_quotas(self):
    #     self.admincli.quotas.update(self.TEST_ALT_TENANT,
    #                 injected_file_content_bytes=self.INJECTED_FILESIZE_LIMIT)
    #     with self.assertRaises(novacli_exceptions.BadRequest):
    #         inject_files = {}
    #         for i in xrange(5):
    #             inject_files['key_%d' % i] = 'this is a large string..%s' % i
    #         self.novacli.servers.create('kong_1', 3, 1, files=inject_files)
    #     self.assertLessEqual(self.get_total_active_injected_filesize(),
    #                          self.INJECTED_FILESIZE_LIMIT)
    #     self.assertEqual(len(self.novacli.servers.list()), 0)


    # def test_010_test_metadata_item_quotas(self):
    #     self.admincli.quotas.update(self.TEST_ALT_TENANT,
    #                                 metadata_items=self.METADATA_LIMIT)
    #     with self.assertRaises(novacli_exceptions.ClientException):
    #         metadata = {}
    #         for i in xrange(self.METADATA_LIMIT+1):
    #             metadata['key_%d' % i] = 'value %s' % i
    #         self.novacli.servers.create('kong_1', 3, 1, meta=metadata)
    #     self.assertLessEqual(self.get_metadata_item_count(),
    #                          self.METADATA_LIMIT)
    #     self.assertEqual(len(self.novacli.servers.list()), 0)
    # 
    # def test_011_test_floating_ip_quotas(self):
    #     self.admincli.quotas.update(self.TEST_ALT_TENANT,
    #                                 floating_ips=self.FLOATING_IP_LIMIT)
    #     # attempt to allocate 5 floating ips to tenant, only 2 shoudl work.
    #     with self.assertRaises(novacli_exceptions.ClientException):
    #         for i in xrange(5):
    #             self.novacli.floating_ips.create()
    #     self.assertLessEqual(len(self.novacli.floating_ips.list()),
    #                              self.FLOATING_IP_LIMIT)
