import logging
from unittest import TestCase

import fauxfactory
import httpbin.core
from wsgi_intercept import add_wsgi_intercept, requests_intercept

from libweb.regex import RegexService


class TestRegex(TestCase):
    def get_app(self):
        return httpbin.core.app

    def setUp(self):
        requests_intercept.install()
        add_wsgi_intercept("httpbin.org", 80, self.get_app)

        logging.getLogger("requests").setLevel("ERROR")
        self.fake_target = fauxfactory.gen_ipaddr()
        self.service = RegexService(self.fake_target)
        self.service.swallow_exceptions = False

    def tearDown(self):
        requests_intercept.uninstall()

    def do_request(self, url, **conf):
        if "method" not in conf:
            conf["method"] = "GET"

        return self.service._req(url, **conf)

    def test_regex_are_compiled(self):
        import re
        self.service.conf = {
            "parse": ["^.+$"]
        }
        [self.assertIsInstance(_, re._pattern_type) for _ in self.service.regexes]

    def test_get_html(self):
        self.service.conf = {
            "url": "http://httpbin.org/html"
        }

        [self.assertIn("<html>", _) for _ in self.service.get_html()]

    def test_regex_matches(self):
        self.service.conf = {
            "url": "http://httpbin.org/robots.txt",
            "parse": [
                "Disallow: (?P<disallowed>.+)"
            ]
        }

        data = dict()
        for _ in self.service.get_results():
            data.update(_)
        self.assertIn("disallowed", data)
        self.assertEqual(data["disallowed"], "/deny")
