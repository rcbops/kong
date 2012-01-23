from resttest import Retryable, Requester
from httptools import codep
from jsontools import with_keys_eq, with_keys_ne, json_request, json_response


class JSONRequester(Requester):
    def __init__(self,predicates=[],response_transformers=[],
                 request_transformers=[]):
        super(JSONRequester, self).__init__(predicates,
                                            response_transformers,
                                            request_transformers)
        if not json_response in self.response_transformers:
            self.response_transformers.append(json_response)
        if not json_request in self.request_transformers:
            self.request_transformers.append(json_request)
    _http_with_keys_eq = {"args": {"d": 1},
                               "predicates": [
                                (codep, ["code"]),
                                (with_keys_eq, ["d"])
    ]}
    _http_with_keys_ne = {"args": {"d": 1},
                               "predicates": [
                                (codep, ["code"]),
                                (with_keys_ne, ["d"])
    ]}
    _http = {"predicates": [(codep, ["code"])]}

