"""JSON Services

This module implements services using JSON over HTTP for communication
"""
from __future__ import absolute_import

import json
from collections import OrderedDict

import jsonpath_rw_ext

from .http import HttpService


class JsonService(HttpService):
    """An HTTP-based service that speaks JSON. Uses jsonpath to parse the returned
    document.

    Keyword arguments:
        jsonpath (dict or list of dicts): JSONpath configuration to extract/parse data
    """

    def get_data(self):
        """Make the HTTP requests and yield the data returned"""
        ignored_status_codes = [int(sc) for sc in self.conf.get("ignored_status_codes", [])]

        for request in self.make_requests():
            if request.status_code in ignored_status_codes:
                raise StopIteration

            if self.conf.get("multi_json", False):
                yield [json.loads(line) for line in request.text.split("\n") if line]
            else:
                yield request.json()

    def get_results(self):
        """Parse the JSON and yield a structured response"""
        # pylint: disable=too-many-nested-blocks
        for data in self.get_data():
            if "jsonpath" in self.conf:
                jsonpaths = self.conf["jsonpath"]
                if not isinstance(jsonpaths, list):
                    jsonpaths = [jsonpaths]
                for jsonpath_conf in jsonpaths:
                    new_data = OrderedDict()
                    for (key, jsonpath) in jsonpath_conf.items():
                        expr = jsonpath_rw_ext.parse(jsonpath)
                        for match in expr.find(data):
                            if key in new_data:
                                if not isinstance(new_data[key], list):
                                    new_data[key] = [new_data[key]]
                                new_data[key].append(match.value)
                            else:
                                new_data.update({key: match.value})
                            # print(new_data)
                    yield new_data
            else:
                if self.conf.get("multi_json", False):
                    for result in data:
                        yield result
                else:
                    yield data
