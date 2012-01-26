from resttest.jsonrequester import JSONRequester
from resttest.jsontools import nested_get, nested_search
from resttest.httptools import wrap_headers

class KongRequester(JSONRequester):
    def __init__(self,service,target="publicURL", predicates=[],
                 response_transformers=[], request_transformers=[],
                 config_file="../etc/config.ini"):
        super(KongRequester,self).__init__(predicates,
                                            response_transformers,
                                            request_transformers)
        self.config_file = config_file
        self.service=service
        self.target = target
        c = JSONRequester()
        (url, user, password, tenantid, region) = self.get_config()
        body = {"auth":{"passwordCredentials":{"username": user,
                "password": password},"tenantId": tenantid}}    
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
            raise ValueError('No endpoint found for service %s in region %s' \
                             + 'with target %s' % (service,target, region))
        if not print_it in self.request_transformers:
            self.request_transformers = [print_it] + self.request_transformers
        base = base_url(self.endpoint)
        if not base in self.request_transformers:
            self.request_transformers += [base]
        auth = wrap_headers({"X-Auth-Token": self.token})
        if not auth in self.request_transformers:
            self.request_transformers += [auth]
        if not print_it in self.response_transformers:
            self.response_transformers = self.response_transformers + [print_it]
    def get_config(self):
        #url, user, password, tenant
        from ConfigParser import ConfigParser
        p = ConfigParser()
        s = "KongRequester"
        p.read(self.config_file)
        url = p.get(s, "auth_url").rstrip("/") + "/v2.0/tokens"
        return url, p.get(s,"user"), p.get(s,"password"), \
            p.get(s, "tenantid"), p.get(s, "region")
        #"http://demo.rcb.me:5000/v2.0/tokens", "admin", "secrete", 1, RegionOne

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

