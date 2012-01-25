#!/usr/bin/python

from resttest.jsonrequester import JSONRequester
from kongrequester import print_it
r= JSONRequester(request_transformers=[print_it],
                 response_transformers=[print_it])
