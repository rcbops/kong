#!/usr/bin/python

from resttest.jsonrequester import JSONRequester

def print_it(*args):
    from pprint import pprint
    for a in args:
        pprint(a)
    return args

r= JSONRequester(request_transformers=[print_it],
                 response_transformers=[print_it])
