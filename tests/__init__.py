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
import nose.plugins.skip
import os
import unittest2


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
        #inject class.tags when methods do not have tags defined.
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

        self.config = parse_config_file(self)

    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
        pass
