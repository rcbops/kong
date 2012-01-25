#!/usr/bin/python
from copy import copy

class textp(object):
    def __init__(self, text):
        self.text = text
    def __call__(self, response, data):
        if data.find(self.text) == -1:
            self.error='text %s not found in returned data' % (self.text)
            return False
        return True
    def __eq__(self, o):
        return type(self) == type(o) and self.code == o.code
    
class codep(object):
    error = "test failed"
    def __init__(self,code):
        self.code = "%s" % code
    def __call__(self, response, data):
        if response['status'] != self.code:
            self.error = 'Return code of "%s" is not "%s"' % (response['status'], self.code)
            return False
        return True
    def __eq__(self, o):
        return type(self) == type(o) and self.code == o.code
    
class wrap_headers(object):
    def __init__(self, headers):
        self.headers = headers
    def __call__(self, uri, method, headers, body, redirections, connection_type):
        nheaders = copy(headers)
        nheaders.update(self.headers)
        return uri, method, nheaders, body, redirections, connection_type
    def __eq__(self, o):
        return type(self) == type(o) and self.headers == o.headers
