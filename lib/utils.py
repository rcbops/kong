#!/usr/bin/python

from resttest.jsonrequester import JSONRequester
from kongrequester import print_it
from kongrequester import KongRequester
r= JSONRequester(request_transformers=[print_it],
                 response_transformers=[print_it])
SERVICES = {}
for service in (("image", "glance"), ("compute", "nova"),
          ("object-storage", "swift"), ("identity", "keystone")):
    try:
        s, aliases = service[0], service[1:]
        SERVICES[s] = KongRequester(s)
        for alias in aliases:
            SERVICES[alias] = SERVICES[s]
    except ValueError:
        #no endpoint
        pass

#one off keystone-admin
try:
    SERVICES['identity-admin'] = KongRequester('identity', target='adminURL')
    SERVICES['keystone-admin'] = SERVICES['identity-admin']
except ValueError:
    pass
