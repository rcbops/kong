from resttest.jsonrequester import JSONRequester
from resttest.jsontools import nested_get, nested_search
from resttest.httptools import wrap_headers


class KongRequester(JSONRequester):
    def __init__(self, service, target="publicURL", predicates=[],
                 response_transformers=[], request_transformers=[],
                 config_file="etc/config.ini",
                 section="KongRequester"):
        super(KongRequester, self).__init__(predicates,
                                            response_transformers,
                                            request_transformers)
        self.config_file = config_file
        self.service = service
        self.target = target
        self.section = section
        self.endpoint, self.token, self.services, self.data = \
            self._init_keystone(service, target)
        self.request_transformers += [base_url(self.endpoint)]
        self.request_transformers += [wrap_headers(
            {"X-Auth-Token": self.token})]
        self.request_transformers += [print_curl_request]
        self.response_transformers = self.response_transformers + [print_it]

    def get_config(self):
        #url, user, password, tenant
        from ConfigParser import ConfigParser
        p = ConfigParser()
        s = self.section
        p.read(self.config_file)
        url = p.get(s, "auth_url").rstrip("/") 
        if not url.find("/v2.0") >= 0: 
            url += "/v2.0/tokens"
        elif not url.find("/tokens") >= 0:
            url += "/tokens"
        tenant = p.get(s, "tenantname")
        user = p.get(s, "user")
        if not tenant and user.find(":") >= 0:
            tenant, user = user.split(":", 1)
        return url, user, p.get(s, "password"), tenant, p.get(s, "region")

    def _init_keystone(self, service, target):
        (url, user, password, tenantname, region) = self.get_config()
        body = {"auth": {"passwordCredentials": {"username": user,
                "password": password}, "tenantName": tenantname}}
        try:
            response, data = self.POST(url, body=body, code=200, 
                                       request_transformers=[print_it], 
                                       response_transformers=[print_it])
        except AssertionError:
            response, data = self.POST(url, body=body['auth'], code=200, 
                                       request_transformers=[print_it],
                                       response_transformers=[print_it])
            data['access'] = data['auth']
        services = nested_get("/access/serviceCatalog", data)
        try:
            endpoint = nested_search(
                "/access/serviceCatalog/*/type=%s/endpoints/*/region=%s/%s" %
                (service, region, target), data)[0]
        except IndexError:
            endpoint = []
        finally:
            if endpoint == []:
                raise ValueError(('No endpoint found for service "%s" in'
                                 + ' region "%s" with target "%s"\n'
                                 + 'service catalog: "%s"') %
                                 (service, region, target, services))
        token = nested_get("/access/token/id", data)
        return endpoint, token, services, data


class base_url(object):
    def __init__(self, uri):
        self.uri = uri

    def __call__(self, path, method, headers, body,
                 redirections, connection_type):
        uri = self.uri + path
        return uri, method, headers, body, redirections, connection_type

    def __eq__(self, o):
        return type(self) == type(o) and self.uri == o.uri


def print_curl_request(uri, method, headers, body,
                       redirections, connection_type):
    def posix_escape(s):
        s.replace("'", "'\"'\"'")
        return "'%s'" % (s)

    command = ["curl"]
    command += ["-H " + posix_escape("%s: %s") % (k, v) for k,v in headers.items()]
    if body:
        command += ["-d %s" % posix_escape(str(body))]
    command += ["-X %s" % (posix_escape(method)), posix_escape(uri) ]
    print " ".join(command)
    return uri, method, headers, body, redirections, connection_type

def print_it(*args):
    from pprint import pprint
    for a in args:
        pprint(a)
    return args
