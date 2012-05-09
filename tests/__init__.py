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
import httplib2
import nose.plugins.skip
import os
from pprint import pprint
import unittest2
import urlparse
import json
# from xmlrpclib import Server


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
    @classmethod
    def setUpClass(self):
        # Setup project hashes
        self.rabbitmq = {}
        try:
            self.__class__.tags
            methods = [self.__getattribute__(m) for m in self.__dict__.keys()
                       if callable(self.getattribute(m)) and
                       not m.find("_") == 0]
            for m in methods:
                try:
                    m.tags
                except AttributeError:
                    m.tags = self.__class__.tags
        except AttributeError:
            pass

        def parse_config_file(self):
            cfg = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   "..", "etc", "config.ini"))
            if os.path.exists(cfg):
                ret_hash = _build_config(self, cfg)
            else:
                raise Exception("Cannot read %s" % cfg)
            return ret_hash

        def _build_config(self, config_file):
            parser = ConfigParser.ConfigParser()
            parser.read(config_file)
            ret_hash = {}
            for section in parser.sections():
                ret_hash[section] = {}
                for value in parser.options(section):
                    ret_hash[section][value] = parser.get(section, value)
            return ret_hash

        def _generate_auth_token(self):
            http = httplib2.Http()
            path = "http://%s:%s/%s/tokens" % (self.config['keystone']['host'],
                                             self.config['keystone']['port'],
                                             self.config['keystone']['apiver'])
            if self.config['keystone']['apiver'] == 'v2.0':
                # try first with d-final keystone auth.  if this fails then
                # fallback to d5.  d5_compat test breaks the d-final first test
                # so we try this from the newest to the oldest.
                self.keystone['subversion'] = 'diablo-final'
                body = {"auth": {"passwordCredentials": {
                            "username": self.keystone['user'],
                            "password": self.keystone['pass']},
                            "tenantName": self.keystone['tenantname']}}
                post_path = urlparse.urljoin(path, "tokens")
                post_data = json.dumps(body)
                headers = {'Content-Type': 'application/json'}
                response, content = http.request(post_path, 'POST',
                                                 post_data,
                                                 headers=headers)
                if response.status != 200:
                    # try again... with yet another 2.0 style
                    self.keystone['subversion'] = 'diablo-d5'
                    body = {"passwordCredentials": {
                                  "username": self.keystone['user'],
                                  "password": self.keystone['pass']},
                           "tenantid": self.keystone['tenantname']}
                    post_path = urlparse.urljoin(path, "tokens")
                    post_data = json.dumps(body)
                    response, content = http.request(post_path, 'POST',
                                 post_data,
                                 headers={'Content-Type': 'application/json'})
                if response.status == 200:
                    decode = json.loads(content)
                    meaningless_cruft = 'auth'
                    if self.keystone['subversion'] == 'diablo-final':
                        meaningless_cruft = 'access'

                    self.keystone['catalog'] =\
                        decode[meaningless_cruft]['serviceCatalog']
                    self.keystone['tenantid'] = decode[meaningless_cruft]['token']['tenant']['id']

                    # print json.dumps(self.keystone['catalog'], indent=2)
                    return decode[meaningless_cruft]['token']['id']
                    #.encode('utf-8')

            if self.config['keystone']['apiver'] == "v1.0":
                headers = {'X-Auth-User': self.keystone['user'],
                           'X-Auth-Key': self.keystone['key']}
                response, content = http.request(path, 'HEAD', headers=headers)
                if response.status == 204:
                    return response['X-Auth-Token']
            else:
                raise Exception("Unable to get a valid token, please fix")

        def _endpoint_for(self, service, region, path):
            if self.keystone['subversion'] == 'diablo-d5':
                for k, v in enumerate(self.keystone['catalog'][service]):
                    if v['region'] == region:
                        return str(v[path])
            elif self.keystone['subversion'] == 'diablo-final':
                for endpoint_list in self.keystone['catalog']:
                    if endpoint_list['name'] == service:
                        for endpoint in endpoint_list['endpoints']:
                            if endpoint['region'] == region:
                                return str(endpoint[path])


            raise Exception("You've been keystoned -- can't find endpoint for\
                                %s/%s/%s" % (service, region, path))

        def _gen_nova_path(self):
            self.nova['path'] = _endpoint_for(self,
                                              'nova',
                                              self.keystone['region'],
                                              'publicURL')
            self.nova['adminPath'] = _endpoint_for(self,
                                                   'nova',
                                                   self.keystone['region'],
                                                   'adminURL')
            return True
            raise Exception(
                "Cannot find region defined in configuration file.")

        def _gen_swift_path(self):
            self.swift['path'] = _endpoint_for(self,
                                               'swift',
                                               self.keystone['region'],
                                               'publicURL')
            self.swift['adminPath'] = _endpoint_for(self,
                                                    'swift',
                                                    self.keystone['region'],
                                                    'adminURL')
            return True
            raise Exception(
                "Cannot find region defined in configuration file.")

        def _gen_glance_path(self):
            self.glance['path'] = _endpoint_for(self,
                                                'glance',
                                                self.keystone['region'],
                                                'publicURL')
            self.glance['adminPath'] = _endpoint_for(self,
                                                     'glance',
                                                     self.keystone['region'],
                                                     'adminURL')
            return True
            raise Exception(
                "Cannot find region defined in configuration file.")

        def _gen_keystone_admin_path(self):
            path = "http://%s:%s/%s" % (self.keystone['host'],
                                        self.keystone['admin_port'],
                                        self.keystone['apiver'])
            return path
        def setupNova(self):
            self.nova['X-Auth-Token'] = _generate_auth_token(self)
            _gen_nova_path(self)
            self.limits = {}
            self.flavor = {}

        def setupSwift(self):
            ret_hash = {}
            if 'auth_type' in self.config['swift'] and \
                self.config['swift']['auth_type'] == "swauth":
                ret_hash['auth_type'] = "swauth"
                ret_hash['auth_host'] = self.config['swift']['auth_host']
                ret_hash['auth_port'] = self.config['swift']['auth_port']
                ret_hash['auth_prefix'] = self.config['swift']['auth_prefix']
                ret_hash['auth_ssl'] = self.config['swift']['auth_ssl']
                ret_hash['account'] = self.config['swift']['account']
                ret_hash['username'] = self.config['swift']['username']
                ret_hash['password'] = self.config['swift']['password']
                # need to find a better way to get this.
                ret_hash['ver'] = 'v1.0'
                return ret_hash
            elif 'auth_type' in self.config['swift'] and \
                self.config['swift']['auth_type'] == 'keystone':
                ret_hash['auth_type'] = 'keystone'
                ret_hash['storage_url'] = _endpoint_for(self,
                                                        'swift',
                                                       self.keystone['region'],
                                                       'publicURL')
                ret_hash['auth_ssl'] = self.config['swift']['auth_ssl']
                ret_hash['account'] = self.config['swift']['account']
                ret_hash['username'] = self.config['swift']['username']
                ret_hash['password'] = self.config['swift']['password']
                return ret_hash
                print ret_hash
            raise Exception(
                          'Cannot find region defined in configuration file.')
            return ret_hash

        def setupKeystone(self):
            ret_hash = {}
            ret_hash['host'] = self.config['keystone']['host']
            ret_hash['port'] = self.config['keystone']['port']
            ret_hash['admin_port'] = self.config['keystone']['admin_port']
            ret_hash['apiver'] = self.config['keystone']['apiver']
            ret_hash['user'] = self.config['keystone']['user']
            ret_hash['pass'] = self.config['keystone']['password']
            ret_hash['tenantname'] = self.config['keystone']['tenantname']
            ret_hash['region'] = self.config['keystone']['region']
            return ret_hash

        # Parse the config file
        self.config = parse_config_file(self)

        if self.config.has_key('keystone'):
           self.nova = {}
           self.glance = {}
           self.swift = {}
           self.keystone = setupKeystone(self)
           self.keystone['admin_path'] = _gen_keystone_admin_path(self)
           _generate_auth_token(self)
           try:
               _gen_glance_path(self)
           except Exception:
               print "Valid endpoint not found for glance in configured" + \
                   "region %s" % self.keystone['region'] + \
                   "Attempting to continue anyway"
           if self.config.has_key('nova'):
               setupNova(self)

        if self.config.has_key('swift'):
            self.swift = setupSwift(self)




    @classmethod
    def tearDownClass(self):
        self.config = ""
        self.nova = ""
        self.keystone = ""
        self.glance = ""
        self.swift = ""
        self.rabbitmq = ""

    def setUp(self):
        x = 1

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

    def _keystone_json(self, user, passwd, tenantid):
        build = {"passwordCredentials": {
                            "username": user,
                            "password": passwd}}
        if tenantid:
            build['passwordCredentials']['tenantId'] = tenantid
        else:
            raise Exception("tenantId is required for Keystone "
                            "auth service v2.0")
        return json.dumps(build)
