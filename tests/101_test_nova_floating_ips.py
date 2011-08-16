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

from pprint import pprint

import tests


class TestNovaFloatingIps(tests.NovaFunctionalTest):
    def setUp(self):
        super(TestNovaFloatingIps, self).setUp()

        for i in range(self.nova['floating_ip_count'] - len(self.novacli.floating_ips.list())):
            self.novacli.floating_ips.create()
        for i in range(self.nova['server_count'] - len(self.novacli.servers.list())):
            self.novacli.servers.create(name="test %s" % random.random(),
                                flavor=self.nova['flavor_id'], image=self.nova['image_id'])
        self.servers = self.novacli.servers.list()
        for ip in self.novacli.floating_ips.list():
            try:
                ip.disassociate()
            except Exception:
                pass
        time.sleep(1)

    def tearDown(self):
        super(TestNovaFloatingIps, self).tearDown()

    def remote_ping(self, floating):
        # FIXME(ja): should be checking for one or other...
        # if floating.fixed_ip or floating.instance_id:
        TEST_PING = "ping -c 1 rackspace.com"
        try:
            ssh = self.ssh(floating.ip)
            stdin, stdout, stderr = ssh.exec_command(TEST_PING)
            if '1 packets received' in stdout.read():
                print "PASS PING", floating.fixed_ip, floating.ip
            else:
                print "FAIL PING", floating.fixed_ip, floating.ip
        except Exception, e:
            print "FAIL CONNECT", floating.fixed_ip, floating.ip

    def metadata(self, floating):
        # FIXME(ja): should be checking for one or other...
        # if floating.fixed_ip or floating.instance_id:
        try:
            ssh = self.ssh(floating.ip)
            stdin, stdout, stderr = ssh.exec_command(TEST_METADATA)
            # FIXME(ja): check for actual matche
            if 'i-' in stdout.read():
                print "PASS METADATA", floating.fixed_ip, floating.ip
            else:
                print "FAIL METADATA", floating.fixed_ip, floating.ip
        except Exception, e:
            print "FAIL CONNECT", floating.fixed_ip, floating.ip

    def check_allocated(self, ip, expected):
        if (ip.fixed_ip or ip.instance_id) is expected:
            if expected:
                error = 'FAIL ASSIGN'
            else:
                error = 'FAIL CLEAR'
            print error, ip._info

    def test_001_test_roaming_association(self):
        for ip in self.novacli.floating_ips.list():
            for s in self.novacli.servers.list():
                try:
                    print 'TEST', s
                    ip.associate(s)
                    self.remote_ping(ip)
                    self.metadata(ip)
                    ip.disassociate()
                except Exception, e:
                    print "EXCEPTION", ip, s, e

