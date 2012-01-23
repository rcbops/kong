#!/usr/bin/python

from resttest.jsonrequester import JSONRequester

def print_it(*args):
    print args
    return args

r= JSONRequester(request_transformers=[print_it],
                 response_transformers=[print_it])
