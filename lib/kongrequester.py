from resttest.jsonrequester import JSONRequester
from resttest.jsontools import nested_get, nested_search
from resttest.httptools import wrap_headers

class KongRequester(JSONRequester):
    def __init__(self,service,target="publicURL", predicates=[],
                 response_transformers=[], request_transformers=[]):
        super(KongRequester,self).__init__(predicates,
                                            response_transformers,
                                            request_transformers)
        self.service=service
        self.target = target
        c = JSONRequester()
        (url, user, password, tenant) = self.get_config()
        body = {"auth": {"passwordCredentials": {"username": user,
                                                 "password": password},
                         "tenantId": tenant}}    
        try:
            response, data = c.POST(url, body=body, code=200)
        except AssertionError:
                response, data = c.POST(url, body=body['auth'],code=200)
                data['access'] = data['auth']
        self.services = nested_get("/access/serviceCatalog", data)
        self.endpoint = nested_search(
            "/access/serviceCatalog/*/type=%s/endpoints/*/region=RegionOne/%s" %
            (service, target), data)[0]
        self.token = nested_get("/access/token/id",data)
        if self.endpoint == []:
            raise ValueError('No endpoint found for service %s in RegionOne' \
                             + 'with target %s' % (service,target))
        if not print_it in self.request_transformers:
            self.request_transformers.insert(0,print_it)
        base = base_url(self.endpoint)
        if not base in self.request_transformers:
            self.request_transformers.append(base)
        auth = wrap_headers({"X-Auth-Token": self.token})
        if not auth in self.request_transformers:
            self.request_transformers.append(auth)
        if not print_it in self.response_transformers:
            self.response_transformers.insert(0,print_it)
    def get_config(self):
        #url, user, password, tenant
        return "http://demo.rcb.me:5000/v2.0/tokens", "admin", "secrete", 1

class base_url(object):
    def __init__(self,uri):
        self.uri = uri
    def __call__(self, path, method, headers, body, redirections, connection_type):
        uri = self.uri + path
        return uri, method, headers, body, redirections, connection_type
    def __eq__(self, o):
        return type(self) == type(o) and self.uri == o.uri
        
def print_it(*args):
    from pprint import pprint
    for a in args:
        pprint(a)
    return args

