#!/usr/bin/env python

import json
import os

from nose.plugins import Plugin

class Skipper(Plugin):
    def options(self, parser, env):
        super(Skipper, self).options(parser, env)
        parser.add_option('--package-set', action='store', dest='package_set',
                          default='diablo-final', metavar='PACKAGE',
                          help='Set package version set')

    def configure(self, options, conf):
        super(Skipper, self).configure(options, conf)
        self.enabled = True
        self.skips=[]

        self.packageSet = options.package_set
        self.parseConfigFile()

    def wantMethod(self, method):
        method_name = method.__name__
        if self.versionConfig.has_key(method_name):
            if self.versionConfig[method_name].has_key('min'):
                if self.packageSet < self.versionConfig[method_name]['min']:
                    self.skips.append(method_name)
                    return False
            if self.versionConfig[method_name].has_key('max'):
                if self.packageSet > self.versionConfig[method_name]['max']:
                    self.skips.append(method_name)
                    return False
            if self.versionConfig[method_name].has_key('exceptions'):
                i = 0
                try:
                    i = self.versionConfig[method_name]['exceptions'].index(self.packageSet)
                except ValueError:
                    i = -1

                if i != -1:
                    self.skips.append(method_name)
                    return False
        return None

    def parseConfigFile(self):
        cfg_file=os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              '..', 'etc', 'versions.json'))
        try:
            json_data = open(cfg_file).read()
            self.versionConfig = json.loads(json_data)
        except:
            print 'Warning:  cannot read config file %s' % (cfg_file,)
            self.versionConfig = {}

    def report(self, stream):
        if len(self.skips) == 0:
            return

        stream.write('Skipped tests (due to packageset version "%s")\n' % self.packageSet)

        for method in self.skips:
            stream.write('    ' + method + '\n')





