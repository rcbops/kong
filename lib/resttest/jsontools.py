#!/usr/bin/python

import json
from copy import copy
from httptools import wrap_headers

def nested_get(key, data):
    indexes = key.strip("/").split("/")
    r = copy(data)
    while(len(indexes) > 0 and indexes[0] != ""):
        i, indexes = indexes[0], indexes[1:]
        try:
            r = r["%s" % i]
        except (TypeError, ValueError):
            i = int(i)
            r = r[i]
    return r

class with_keys_op(object):
    def __init__(self, d, op=lambda x,y: x == y, 
                 error="json value at key not equal to provide value"):
        self.d = d 
        self.error = error
        self.op = op
    def __call__(self, response, data):
        jv  = None
        r = False
        for k,v in self.d.iteritems():
            jv = nested_get(k, data)
            r = apply(self.op, (jv, v))
            if not r:
                self.error = "json value %s at %s failed comparison against %s" % \
                    (jv, k,v)
        return r

def with_keys_eq(d):
    return with_keys_op(d)

def with_keys_ne(d):
    return with_keys_op(d,op=lambda x,y: x != y)

def json_response(response,data):
    if data != None and data != "":
        return response, json.loads(data)
    return response, data

def json_request(uri, method, headers, body, redirections, connection_type):
    nuri, nmethod, nheaders, nbody, nredirections, nconnection_type = \
        wrap_headers({"Content-Type": "application/json"})(**locals())
    if nbody != None:
        nbody = json.dumps(nbody)
    return uri, method, nheaders, nbody, redirections, connection_type
