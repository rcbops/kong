# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010-2011 OpenStack LLC.
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

import ConfigParser
from hashlib import md5
import nose.plugins.skip
import os
import subprocess
import unittest2
from xmlrpclib import Server

import novaclient.client
import novaclient.keystone
import novaclient.v1_1.client


NOVA_DATA = {}
GLANCE_DATA = {}
SWIFT_DATA = {}
RABBITMQ_DATA = {}
CONFIG_DATA = {}
KEYSTONE_DATA = {}

class skip_test(object):
    """Decorator that skips a test."""
    def __init__(self, msg):
        self.message = msg

    def __call__(self, func):
        def _skipper(*args, **kw):
            """Wrapped skipper function."""
            raise nose.SkipTest(self.message)
        _skipper.__name__ = func.__name__
        _skipper.__doc__ = func.__doc__
        return _skipper


class skip_if(object):
    """Decorator that skips a test."""
    def __init__(self, condition, msg):
        self.condition = condition
        self.message = msg

    def __call__(self, func):
        def _skipper(*args, **kw):
            """Wrapped skipper function."""
            if self.condition:
                raise nose.SkipTest(self.message)
            func(*args, **kw)
        _skipper.__name__ = func.__name__
        _skipper.__doc__ = func.__doc__
        return _skipper


class skip_unless(object):
    """Decorator that skips a test."""
    def __init__(self, condition, msg):
        self.condition = condition
        self.message = msg

    def __call__(self, func):
        def _skipper(*args, **kw):
            """Wrapped skipper function."""
            if not self.condition:
                raise nose.SkipTest(self.message)
            func(*args, **kw)
        _skipper.__name__ = func.__name__
        _skipper.__doc__ = func.__doc__
        return _skipper


class FunctionalTest(unittest2.TestCase):
    def setUp(self):
        global GLANCE_DATA, NOVA_DATA, SWIFT_DATA, RABBITMQ_DATA, KEYSTONE_DATA, CONFIG_DATA
        # Define config dict
        self.config = CONFIG_DATA
        # Define service specific dicts
        self.glance = GLANCE_DATA
        self.nova = NOVA_DATA
        self.swift = SWIFT_DATA
        self.rabbitmq = RABBITMQ_DATA
        self.keystone = KEYSTONE_DATA

        self._parse_defaults_file()

        # Swift Setup
        if 'swift' in self.config:
            self.swift['auth_host'] = self.config['swift']['auth_host']
            self.swift['auth_port'] = self.config['swift']['auth_port']
            self.swift['auth_prefix'] = self.config['swift']['auth_prefix']
            self.swift['auth_ssl'] = self.config['swift']['auth_ssl']
            self.swift['account'] = self.config['swift']['account']
            self.swift['username'] = self.config['swift']['username']
            self.swift['password'] = self.config['swift']['password']
            self.swift['ver'] = 'v1.0'  # need to find a better way to get this.

        # Glance Setup
        self.glance['host'] = self.config['glance']['host']
        self.glance['port'] = self.config['glance']['port']
        if 'apiver' in self.config['glance']:
            self.glance['apiver'] = self.config['glance']['apiver']

        if 'nova' in self.config:
            self.nova['host'] = self.config['nova']['host']
            self.nova['port'] = self.config['nova']['port']
            self.nova['ver'] = self.config['nova']['apiver']
            self.nova['user'] = self.config['nova']['user']
            self.nova['key'] = self.config['nova']['key']
            self.nova['flavor_id'] = self.config['nova']['flavor_id']
            self.nova['image_id'] = self.config['nova']['image_id']
            self.nova['server_count'] = int(self.config['nova']['server_count'])
            self.nova['floating_ip_count'] = int(self.config['nova']['floating_ip_count'])

        if 'keystone' in self.config:
            self.keystone['host'] = self.config['keystone']['host']
            self.keystone['port'] = self.config['keystone']['port']
            self.keystone['apiver'] = self.config['keystone']['apiver']
            self.keystone['user'] = self.config['keystone']['user']
            self.keystone['pass'] = self.config['keystone']['password']
            self.keystone['password'] = self.config['keystone']['password']
            self.keystone['tenant'] = self.config['keystone']['tenant']

    def _md5sum_file(self, path):
        md5sum = md5()
        with open(path, 'rb') as file:
            for chunk in iter(lambda: file.read(8192), ''):
                md5sum.update(chunk)
        return md5sum.hexdigest()

    def _read_in_chunks(self, infile, chunk_size=1024 * 64):
        file_data = open(infile, "rb")
        while True:
            # chunk = file_data.read(chunk_size).encode('base64')
            chunk = file_data.read(chunk_size)
            if chunk:
                yield chunk
            else:
                return
        file_data.close()

    def _parse_defaults_file(self):
        cfg = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   "..", "etc", "config.ini"))
        if os.path.exists(cfg):
            self._build_config(cfg)
        else:
            raise Exception("Cannot read %s" % cfg)

    def _build_config(self, config_file):
        parser = ConfigParser.ConfigParser()
        parser.read(config_file)

        for section in parser.sections():
            self.config[section] = {}
            for value in parser.options(section):
                self.config[section][value] = parser.get(section, value)
                # print "%s = %s" % (value, parser.get(section, value))


class NovaFunctionalTest(FunctionalTest):
    def setUp(self):
        super(NovaFunctionalTest, self).setUp()
        auth_url = "http://%s:%s/v2.0/" % (self.config['keystone']['host'],
                                           self.config['keystone']['port'])

        self.TEST_USER = "TEST_USER"
        self.TEST_PW = "TEST_PW"
        self.TEST_EMAIL = "test@email.com"
        self.TEST_TENANT = "TEST_TENANT"
        self.TEST_ALT_TENANT = "TEST_ALT_TENANT"

        conn = novaclient.client.HTTPClient(self.keystone['user'],
                                            self.keystone['password'],
                                            self.keystone['tenant'],
                                            auth_url)
        kc = novaclient.keystone.Client(conn)

        try:
            kc.tenants.get(self.TEST_TENANT)
        except:
            kc.tenants.create(self.TEST_TENANT)

        try:
            test_user = kc.users.get(self.TEST_USER)
        except:
            test_user = kc.users.create(self.TEST_USER,
                                        self.TEST_PW,
                                        self.TEST_EMAIL,
                                        self.TEST_TENANT)

        try:
            rcb = kc.tenants.get(self.TEST_ALT_TENANT)
        except:
            rcb = kc.tenants.create(self.TEST_ALT_TENANT)

        if not test_user in kc.users.list(self.TEST_ALT_TENANT):
            rcb.add_user(test_user)

        self.kc = kc
        self.novacli = novaclient.v1_1.client.Client(self.TEST_USER,
                                                     self.TEST_PW,
                                                     self.TEST_ALT_TENANT,
                                                     auth_url)

    def tearDown(self):
        super(NovaFunctionalTest, self).tearDown()
        # For now, don't tear down user and tenants?
        #self.kc.users.get(self.TEST_USER).delete()
        #self.kc.tenants.get(self.TEST_ALT_TENANT).delete()
        #self.kc.tenants.get(self.TEST_TENANT).delete()

    def ssh(self, host, username='root', password='password', max_tries=2):
        tries = 0
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(IgnorePolicy())
            client.connect(host, username=username, password=password, timeout=5)
            return client
        except (paramiko.AuthenticationException, paramiko.SSHException):
            tries += 1
            if tries == max_tries:
                raise

    def ping(self, ip):
        cmd = "ping -c 1 %s" % ip
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        process.wait()
        return (0 == process.returncode)

    def is_pingable(addr, timeout=20):
        for i in xrange(0, timeout):
            if self.ping(addr):
                return True
            time.sleep(1)
        return False
