#!/usr/bin/python

from httplib2 import Http, DEFAULT_MAX_REDIRECTS
from functools import partial
from copy import copy


def Retryable(f):
    def wrapped(*args, **kwargs):
        from time import sleep
        timeout = kwargs.get("timeout", None)
        delay = kwargs.get("delay", None)
        if timeout and delay and delay > 0 and timeout > 0:
            del kwargs["timeout"]
            del kwargs["delay"]
            t = 0
            while(t < timeout - delay):
                try:
                    return f(*args, **kwargs)
                except:
                    sleep(delay)
                    t += delay
        return f(*args, **kwargs)
    return wrapped


def loop_f(functions, *args):
    #avoid mutating arguments
    nargs = copy(args)
    for f in functions:
        nargs = f(*nargs)
    return nargs


def loop_p(predicates, *args, **kwargs):
    #avoid mutating arguments
    nargs, nkwargs = copy(args), copy(kwargs)
    error = nkwargs.get("error", "predicate is not true")
    assertTrue = nkwargs.get("assertTrue", True)
    success = True
    for f in predicates:
        r = f(*nargs)
        success = success and r
        if not success:
            if hasattr(f, "error"):
                raise AssertionError(f.error)
            if assertTrue:
                raise AssertionError(error)
            return success
    return success


def request(uri, method="GET", headers={}, body=None,
            redirections=DEFAULT_MAX_REDIRECTS, connection_type=None,
            request_transformers=[], response_transformers=[], predicates=[],
            error="test failed"):
    c = Http()
    uri, method, headers, body, redirections, connection_type = \
            loop_f(request_transformers, uri, method, headers,
                   body, redirections, connection_type)
    response, data = c.request(uri,
                               method=method,
                               headers=headers,
                               body=body,
                               redirections=redirections,
                               connection_type=connection_type)
    response, data = loop_f(response_transformers, response, data)
    loop_p(predicates, response, data, error=error)
    return response, data


class Requester(object):
    def __init__(self, predicates=[], response_transformers=[],
                 request_transformers=[]):
        import copy
        self.predicates = copy.copy(predicates)
        self.response_transformers = copy.copy(response_transformers)
        self.request_transformers = copy.copy(request_transformers)
        for method in  ["GET", "PUT", "DELETE", "POST", "HEAD"]:
            for cm in self.__dict__.keys():
                if cm.find("_http") == 0:
                    new_method = cm.replace("_http", method, 1)
                    if not new_method in self.__dict__:
                        self.__dict__[new_method] = partial(
                            self.__class__._dispatch,
                            self,
                            method=method,
                            desc=self.__dict__[cm])

    def request(self, uri, method="GET", headers={}, body=None,
                redirections=DEFAULT_MAX_REDIRECTS, connection_type=None,
                request_transformers=[], response_transformers=[],
                predicates=[], error="test failed"):
        return request(uri, method, headers, body, redirections,
                       request_transformers=request_transformers + \
                       self.request_transformers,
                       response_transformers=response_transformers \
                                              + self.response_transformers,
                       predicates=predicates + self.predicates,
                       error=error)

    @Retryable
    def _dispatch(self, *args, **kwargs):
        args = list(args)
        desc = kwargs.get('desc', {})
        if 'desc' in kwargs:
            del kwargs['desc']
        topics = ["predicates", "request_transformers",
                  "response_transformers"]
        #move args we care about to kwargs for uniform access
        for k, v in desc.get("args", {}).items():
            kwargs[k] = args[v]
            del args[v]
        #for each topic, we grab the right arguments and init the functions
        for topic in topics:
            kwargs[topic] = kwargs.get(topic, [])
            for function in desc.get(topic, ()):
                f, f_keys = function
                f_args = tuple([kwargs[a] for a in f_keys if a in kwargs])
                if len(f_args) > 0 and len(f_args) == len(f_keys):
                    kwargs[topic] += [f(*f_args)]
                    for k in f_keys:
                        del kwargs[k]
                elif len(f_keys) == 0:
                    kwargs[topic] += [f]
        args = tuple(args)
        return self.request(*args, **kwargs)
