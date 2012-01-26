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


def safe_nested_get(key, data):
    try:
        return nested_get(key, data)
    except:
        return None


def nested_search(key, data, acc=None):
    indexes = key.strip("/").split("/")
    head, rest = indexes[0], "/".join(indexes[1:])

    if acc == None:
        # first run
        acc = [data]
    if head == '':
        return acc
    elif head == '*':
        #special case 1 search,
        collect = []
        for i in acc:
            if type(i) == list:
                for j in i:
                    collect.append(j)
        acc = collect
    elif head.find("=") >= 0:
        #special case 2: SEARCH
        collect = []
        k, v = head.split("=", 1)
        for i in acc:
            value = safe_nested_get(k, i)
            if v == value:
                collect.append(i)
        acc = collect
    else:
        #we need to iterate through acc and remove items that no longer match
        acc = [safe_nested_get(head, d) for d in acc if
               safe_nested_get(head, d) != None]

    return nested_search(rest, data, acc)


def nested_match(key, data):
    return [d for d in data if len(nested_search(key, data)) != 0]


class with_keys_op(object):
    def __init__(self, d, op=lambda x, y: x == y,
                 error="json value at key not equal to provide value"):
        self.d = d\
        self.error = error
        self.op = op

    def __call__(self, response, data):
        jv = None
        r = False
        for k, v in self.d.iteritems():
            jv = nested_get(k, data)
            r = apply(self.op, (jv, v))
            if not r:
                self.error = ("json value %s at %s failed comparison " +
                              "against %s") % (jv, k, v)
        return r


def with_keys_eq(d):
    return with_keys_op(d)


def with_keys_ne(d):
    return with_keys_op(d, op=lambda x, y: x != y)


def json_response(response, data):
    if data != None and data != "":
        return response, json.loads(data)
    return response, data


def json_request(uri, method, headers, body, redirections, connection_type):
    nuri, nmethod, nheaders, nbody, nredirections, nconnection_type = \
        wrap_headers({"Content-Type": "application/json"})(**locals())
    if nbody != None:
        nbody = json.dumps(nbody)
    return uri, method, nheaders, nbody, redirections, connection_type
