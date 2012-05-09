from resttest import Retryable, Requester
from httptools import codep
from jsontools import with_keys_eq, with_keys_ne, json_request
from jsontools import safe_json_response


class JSONRequester(Requester):
    def __init__(self, predicates=[], response_transformers=[],
                 request_transformers=[]):
        self._http_with_keys_eq = {
            "args": {"d": 1},
            "predicates": [(codep, ["code"]),
                            (with_keys_eq, ["d"])],
            "response_transformers": [
                (safe_json_response, [])],
            "request_transformers": [
                (json_request, [])]}
        self._http_raw_with_keys_eq = {
            "args": {"d": 1},
            "predicates": [(codep, ["code"]),
                            (with_keys_eq, ["d"])],
            "response_transformers": [
                (safe_json_response, [])]}
        self._http_raw_with_keys_ne = {
            "args": {"d": 1},
            "predicates": [(codep, ["code"]),
                            (with_keys_ne, ["d"])],
            "response_transformers": [
                (safe_json_response, [])]}
        self._http_with_keys_ne = {
            "args": {"d": 1},
            "predicates": [
                (codep, ["code"]),
                (with_keys_ne, ["d"])],
            "response_transformers": [
                (safe_json_response, [])],
            "request_transformers": [
                (json_request, ["uri", "headers", "body",
                                "response_transformers"])]}
        self._http = {
            "args": {"uri": 0},
            "predicates": [(codep, ["code"])],
            "response_transformers": [(safe_json_response, [])],
            "request_transformers": [
                (json_request, [])]}
        self._http_raw = {
            "args": {"uri": 0},
            "predicates": [(codep, ["code"])]}

        super(JSONRequester, self).__init__(predicates,
                                            response_transformers,
                                            request_transformers)
        #if not safe_json_response in self.response_transformers:
        #    self.response_transformers.append(safe_json_response)
        #if not json_request in self.request_transformers:
        #    self.request_transformers.append(json_request)
