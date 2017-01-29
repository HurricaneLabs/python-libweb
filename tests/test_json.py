import logging
from unittest import TestCase

import fauxfactory
import httpbin.core
from wsgi_intercept import add_wsgi_intercept, requests_intercept

from libweb.json import JsonService


class TestJson(TestCase):
    def get_app(self):
        return httpbin.core.app

    def setUp(self):
        requests_intercept.install()
        add_wsgi_intercept("httpbin.org", 80, self.get_app)

        logging.getLogger("requests").setLevel("ERROR")
        self.fake_target = fauxfactory.gen_ipaddr()
        self.service = JsonService(self.fake_target)
        self.service.swallow_exceptions = False

    def tearDown(self):
        requests_intercept.uninstall()

    def test_ignored_status_code_stop_iteration(self):
        status_code = 400 + fauxfactory.gen_integer(min_value=0, max_value=22)
        self.service.conf = {
            "url": "http://httpbin.org/status/{0}".format(str(status_code)),
            "ignored_status_codes": [status_code]
        }
        self.assertEqual(len(list(self.service)), 0)

    def test_multi_json(self):
        lines = fauxfactory.gen_integer(min_value=1, max_value=10)
        self.service.conf = {
            "url": "http://httpbin.org/stream/{0}".format(lines),
            "multi_json": True,
        }

        results = list()
        for result in self.service:
            self.assertIn("url", result)
            results.append(result)
        self.assertEqual(len(results), lines)

    def test_standard_json(self):
        self.service.conf = {
            "url": "http://httpbin.org/get"
        }

        self.assertEqual(len(list(self.service)), 1)

    def test_single_jsonpath(self):
        result_key = fauxfactory.gen_alpha().lower()
        self.service.conf = {
            "url": "http://httpbin.org/get",
            "jsonpath": {result_key: "$.headers.Host"}
        }

        data = dict()
        for _ in self.service:
            data.update(_)
        self.assertEqual(data.get(result_key, None), "httpbin.org")

    def test_jsonpath_multiple_matches(self):
        result_key = fauxfactory.gen_alpha().lower()
        self.service.conf = {
            "url": "http://httpbin.org/get",
            "jsonpath": {result_key: "$.headers.*"}
        }

        data = dict()
        for _ in self.service:
            data.update(_)
        self.assertEqual(len(data.get(result_key, None)), 5)

    def test_multiple_jsonpath(self):
        result_key_1 = fauxfactory.gen_alpha().lower()
        result_key_2 = fauxfactory.gen_alpha().lower()
        self.service.conf = {
            "url": "http://httpbin.org/get",
            "jsonpath": [
                {result_key_1: "$.headers.Host"},
                {result_key_2: "$.url"},
            ]
        }

        data = dict()
        for _ in self.service:
            data.update(_)

        self.assertIn(result_key_1, data)
        self.assertEqual(data[result_key_1], "httpbin.org")
        self.assertIn(result_key_2, data)
        self.assertEqual(data[result_key_2], "http://httpbin.org/get")
