#!/usr/bin/python

from resttest.jsonrequester import JSONRequester
from kongrequester import print_it
from kongrequester import KongRequester
import socket
r = JSONRequester(request_transformers=[print_it],
                 response_transformers=[print_it])
SERVICES = {}
for service in (("image", "glance"),
                ("compute", "nova"),
                ("object-store", "swift"),
                ("identity", "keystone"),
                ("metering", "ceilometer"),
                ("volume", "cinder")):
    try:
        s, aliases = service[0], service[1:]
        SERVICES[s] = KongRequester(s)
    except (ValueError, KeyError, socket.error):
        #no endpoint
        SERVICES[s] = None
    finally:
        try:
            for alias in aliases:
                SERVICES[alias] = SERVICES[s]
        except (ValueError, KeyError, socket.error):
            SERVICES[alias] = None

#one off keystone-admin
try:
    SERVICES['identity-admin'] = KongRequester('identity', target='adminURL')
    SERVICES['keystone-admin'] = SERVICES['identity-admin']
except (ValueError, socket.error):
    SERVICES['identity-admin'] = None
    SERVICES['keystone-admin'] = None

def read_in_chunks(infile, chunk_size=1024 * 64):
    file_data = open(infile, "rb")
    while True:
        chunk = file_data.read(chunk_size)
        if chunk:
            yield chunk
        else:
            return
    file_data.close()

#one off swauth
if SERVICES['object-store'] == None:
    from swauthrequester import SwauthRequester
    try:
        SERVICES['object-store'] = SwauthRequester()
        SERVICES['swift'] = SERVICES['object-store']
    except:
        pass
