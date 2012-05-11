from resttest.jsonrequester import JSONRequester
from resttest.httptools import wrap_headers


class SwauthRequester(JSONRequester):
    def __init__(self, predicates=[], response_transformers=[],
                 request_transformers=[], config_file="etc/config.ini"):
        super(SwauthRequester, self).__init__(predicates,
                                              response_transformers,
                                              request_transformers)
        self.config_file = config_file
        self.endpoint, self.token = self._init_swauth()
        self.request_transformers += [base_url(self.endpoint)]
        self.request_transformers += [wrap_headers(
            {"X-Auth-Token": self.token})]
        self.request_transformers += [print_curl_request]
        self.response_transformers = self.response_transformers + [print_it]

    def get_config(self):
        #url, user, password, tenant
        from ConfigParser import ConfigParser
        p = ConfigParser()
        s = "swift"
        p.read(self.config_file)
        url = "http%s://%s:%s/%s/v1.0" % (
            p.get(s,"auth_ssl") == "yes" and "s" or "",
            p.get(s, "auth_host"),
            p.get(s, "auth_port"),
            p.get(s, "auth_prefix").strip("/"))
        return url, p.get(s, "username"), p.get(s, "password"), \
            p.get(s, "account")

    def _init_swauth(self):
        (url, user, password, account) = self.get_config()
        headers = {"X-Storage-User": "%s:%s" % (account, user),
                   "X-Storage-Pass": password}
        response, data = self.GET(url, headers=headers, code=200)
        endpoint = response['x-storage-url']
        token = response['x-auth-token']
        return endpoint, token


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
